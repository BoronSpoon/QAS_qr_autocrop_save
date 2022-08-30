import cv2
import sys
import time
import os, sys
import numpy as np
import pyboof as pb
import decode_qrcode
from textwrap import dedent
cwd = os.path.dirname(__file__)

class Detect():        
    red = (0,0,255)
    green = (0,255,0)
    blue = (255,0,0)
    white = (255,255,255)
    black = (0,0,0)
    cwd = os.path.dirname(__file__)
    def __init__(self, savedir, width=1920, height=1080, max_processes=10, debug=False):
        self.debug = debug # debug mode will write detection result to frame and display it (slow)
        self.savedir = savedir # folder to save the file
        self.buffer = []
        self.frame_count = 0
        self.frames_available = True
        self.width, self.height = width, height
        self.bbox_padding_ratio = 1.5
        self.max_processes = max_processes
        # for qrcode detection and decoding on whole image
        self.detector1 = cv2.wechat_qrcode_WeChatQRCode(
            os.path.join(cwd, "model", "detect.prototxt"),
            os.path.join(cwd, "model", "detect.caffemodel"),
            os.path.join(cwd, "model", "sr.prototxt"),
            os.path.join(cwd, "model", "sr.caffemodel")
        )
        # for qrcode bounding box drawing on cropped image
        self.detector2 = pb.FactoryFiducial(np.uint8).qrcode()

    def draw_bounding_box(self, bbox, color=(0,0,255)):
        bbox = bbox.astype(int)
        n = len(bbox)
        for i in range(n):
            cv2.line(self.original_frame, (bbox[i][0], bbox[i][1]), (bbox[(i+1)%n][0], bbox[(i+1)%n][1]), color, 3)

    def draw_precise_marker_bounding_box(self):
        self.draw_bounding_box(self.bbox, color=self.red)

    def draw_rough_marker_bounding_box(self):
        self.draw_bounding_box(self.bbox, color=self.green)

    def draw_device_bounding_box(self):
        self.draw_bounding_box(self.device_bbox, color=self.blue)

    def draw_corner_circle(self, corner, color=(0,0,255)):
        cv2.circle(self.original_frame, [int(i) for i in corner], 10, color, -1)
        cv2.circle(self.original_frame, [int(i) for i in corner], 10, color, -1)
    
    def draw_corner_circles(self, ):
        self.draw_corner_circle(self.marker_corner, color=self.red)
        self.draw_corner_circle(self.device_corner, color=self.green)

    def shift_bounding_box_to_image_coordinate(self):
        self.bbox = np.array(self.detector2.detections[0].bounds.convert_tuple()) + np.array([self.min_x, self.min_y])

    def get_distance(self, point1, point2):
        distance = np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
        return distance

    def get_marker_width(self):
        self.marker_width = self.get_distance(self.bbox[2], self.bbox[3])
        self.marker_gap = self.marker_width + self.marker_real_gap/self.marker_real_width

    def get_angle(self):
        point1, point2 = self.bbox[2], self.bbox[3]
        self.angle = np.arctan2(point1[1] - point2[1], point1[0] - point2[0])

    def get_marker_corner(self):
        self.marker_corner = self.bbox[2]

    def get_device_corner(self):
        width = self.marker_width * self.x_pos
        height = self.marker_width * self.y_pos
        x, y = self.marker_corner
        c, s = np.cos(self.angle), np.sin(self.angle)
        self.device_corner = [x - (c*width-s*height), y - (s*width+c*height)]

    def get_device_bounding_box(self, ):
        width = self.marker_width * self.device_width
        height = self.marker_width * self.device_height
        x, y = self.device_corner
        c, s = np.cos(self.angle), np.sin(self.angle)
        self.device_bbox = np.array([
            [x, y],
            [x+c*width, y+s*width],
            [x+c*width-s*height, y+s*width+c*height],
            [x-s*height, y+c*height],
        ])

    def rotate_and_crop(self, width=None, height=None, center=None):
        if width is None:
            width = self.marker_width*self.device_width
        if height is None:
            height = self.marker_width*self.device_height
        if center is None:
            center = np.mean(self.device_bbox, axis=0)
        M = cv2.getRotationMatrix2D(center, self.angle * 360/(2*np.pi), scale=1)
        frame = cv2.warpAffine(self.untouched_frame, M, [self.untouched_frame.shape[1], self.untouched_frame.shape[0]])
        x = center[0] - width/2
        y = center[1] - height/2
        return frame[int(y):int(y+height), int(x):int(x+width)]

    def preprocess(self):
        self.untouched_frame = np.copy(self.original_frame)
        self.frame = np.copy(self.original_frame)
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        self.frame = 255 - self.frame
        self.mask = np.zeros_like(self.original_frame)
        _, self.frame = cv2.threshold(self.frame, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    def extend_bbox(self):
        # get bounding box for the qr code
        min_x_, max_x_, min_y_, max_y_ = np.min(self.bbox, axis=0)[0], np.max(self.bbox, axis=0)[0], np.min(self.bbox, axis=0)[1], np.max(self.bbox, axis=0)[1]
        self.center_x, self.center_y = (min_x_ + max_x_)/2, (min_y_ + max_y_)/2
        span_x_, span_y_ = max_x_ - self.center_x, max_y_ - self.center_y
        # extend bounding box to fit whole qr code
        self.span_x, self.span_y = self.bbox_padding_ratio*span_x_, self.bbox_padding_ratio*span_y_
        self.min_x, self.min_y = max(0, self.center_x-self.span_x), max(0, self.center_y-self.span_y)
        self.max_x, self.max_y = min(self.width, self.center_x+self.span_x), min(self.height, self.center_y+self.span_y)

    def crop_frame(self):
        # crop image by bounding box
        self.cropped_frame = self.frame[int(self.min_y):int(self.max_y), int(self.min_x):int(self.max_x)]
        # pyboof only accepts uint8 grayscale image
        self.cropped_framepb = pb.ndarray_to_boof(np.ascontiguousarray(self.cropped_frame))

    def is_corner_qr(self,):
        return decode_qrcode.classify_qr(self.result) == "corner_QR"

    def decode_corner_qr(self):
        self.x_pos, self.y_pos, self.device_width, self.device_height, self.marker_real_width, self.marker_real_gap, self.cx, self.cy, self.ci, self.cj, self.operator_name, self.device_name = decode_qrcode.decode_corner_qr(self.result)

    def decode_process_qr(self, result=None):
        if result is None:
            return decode_qrcode.decode_process_qr(self.result)
        else:
            return decode_qrcode.decode_process_qr(result)

    def draw_rotated_text(self, org, text, font=cv2.FONT_HERSHEY_COMPLEX, fontScale=0.6, color=(0,0,0), thickness=1, anchor="bottom_left", **kwargs):
        (label_width, label_height), baseline = cv2.getTextSize(text, font, fontScale, thickness)
        self.mask *= 0
        x0, y0 = org
        dy = int(label_height + baseline)
        if anchor == "bottom_left":
            for i, line in enumerate(text.split('\n')[::-1]):
                y = y0 - i*dy
                cv2.putText(self.mask, line, (x0, y), font, fontScale, self.white, thickness, **kwargs)
        elif anchor == "top_left":
            for i, line in enumerate(text.split('\n')):
                y = y0 + i*dy
                cv2.putText(self.mask, line, (x0, y), font, fontScale, self.white, thickness, **kwargs)
        M = cv2.getRotationMatrix2D(org, -self.angle*360/(2*np.pi), 1.0)
        self.mask = cv2.warpAffine(self.mask, M, [self.mask.shape[1], self.mask.shape[0]], borderValue=(0,0,0))
        self.original_frame = self.original_frame * np.where(self.mask > 1, 0, 1) + (self.mask/255 * np.array([[color]]))
        self.original_frame = self.original_frame.astype(np.uint8)

    def draw_device_data_text(self):
        text = dedent(f"""
            x,y pos: {self.x_pos}, {self.y_pos}, device width,height: {self.device_width}, {self.device_height},
            marker size, gap: {self.marker_real_width}, {self.marker_real_gap}, 
            cx,cy,ci,cj: {self.cx}, {self.cy}, {self.ci}, {self.cj}, 
            name, sample: {self.operator_name}, {self.device_name}
        """)
        self.draw_rotated_text([int(i) for i in self.device_corner], text, anchor="top_left")
        
    def draw_process_data_text(self):
        try:
            text = dedent(f"""
                count: {self.process_count},
                name: {self.process_name},
            """)
            self.draw_rotated_text([int(i) for i in self.process_qr_corner], text, anchor="bottom_left")
        except:
            pass

    def detect_rough(self, ):
        self.results, self.bboxes = self.detector1.detectAndDecode(self.frame)
        self.bboxes = [np.array(bbox) for bbox in self.bboxes]

    def detect_precise(self, ):
        self.detector2.detect(self.cropped_framepb)
        return len(d.detector2.detections) > 0

    def reset_processed_devices(self,):
        self.processed_devices = []

    def device_has_not_been_processed(self, ):
        return [self.cx, self.cy, self.ci, self.cj, self.device_name] not in self.processed_devices

    def add_to_processed_devices(self,):
        self.processed_devices.append([self.cx, self.cy, self.ci, self.cj, self.device_name])

    def imshow_shrunk_original_frame(self,):
        self.combined_frame = np.vstack([self.original_frame, cv2.cvtColor(self.frame, cv2.COLOR_GRAY2BGR)])
        #cv2.imshow("original_frame", cv2.resize(self.original_frame, (int(self.original_frame.shape[1]/2), int(self.original_frame.shape[0]/2))))
        cv2.imshow("frame", cv2.resize(self.combined_frame, (int(self.combined_frame.shape[1]/3), int(self.combined_frame.shape[0]/3))))
        cv2.waitKey(1)

    def detect_process_qr(self,):
        cropped_process_qr_frame = self.rotate_and_crop_process_qr()
        try:
            results, bboxes = self.detector1.detectAndDecode(cropped_process_qr_frame)
            process_counts = []
            process_names = {}
            for result, bbox in zip(results, bboxes):
                process_count, process_name = self.decode_process_qr(result)
                process_counts.append(process_count)
                process_names[process_count] = process_name
            # find the max process count and set it as the current process
            self.process_count = max(process_counts)
            self.process_name = process_names[self.process_count]
            
            width, height = self.marker_gap*self.process_count, self.marker_gap
            x, y = self.device_corner 
            c, s = np.cos(self.angle), np.sin(self.angle)
            self.process_qr_corner = [x - (c*(-width)-s*height), y - (s*(-width)+c*height)]
        except:
            pass

    def rotate_and_crop_process_qr(self, ):
        x, y = self.device_corner
        c, s = np.cos(self.angle), np.sin(self.angle)
        for qr_count in range(1,min(self.max_processes, self.device_width)+1)[::-1]:
            try:
                width, height = self.marker_gap*qr_count, self.marker_gap
                center = [x - (c*(-width)/2-s*height/2), y - (s*(-width)/2+c*height/2)]
                width, height = width+self.marker_gap/4, height+self.marker_gap/4 # widen detection range
                M = cv2.getRotationMatrix2D(center, self.angle * 360/(2*np.pi), scale=1)
                frame = cv2.warpAffine(self.frame, M, [self.frame.shape[1], self.frame.shape[0]])
                x = center[0] - width/2
                y = center[1] - height/2
                return frame[int(y):int(y+height), int(x):int(x+width)]
            except:
                pass

    def process_frame_for_saving(self,):
        self.processed_frame = self.rotate_and_crop()

    def store_processed_frame_to_ram(self,): # store processed image to RAM for low latency instead of disk
        self.buffer.append({
            "filename": [self.operator_name, self.device_name, f"{self.process_count}_{self.process_name}", f"{self.cx}_{self.cy}_{self.ci}_{self.cj}.png"],
            "frame": self.processed_frame,
        })

    def write_processed_frame_to_disk(self,): # write processed image in RAM to disk
        for frame_dict in self.buffer:
            filename = frame_dict["filename"]
            frame = frame_dict["frame"]
            directory = os.path.join(self.savedir, *filename[:-1])
            path = os.path.join(self.savedir, *filename)
            if not os.path.isdir(directory):
                os.mkdirs(directory)
            cv2.imwrite(path, frame)

    def detect_monitor_wake(self, ): 
        # read frame and take max value: if it is not 0, the monitor is awake
        while True:
            if np.max(self.original_frame) != 0:
                self.monitor_is_awake = True
                break
            time.sleep(10)
    
    def detect_monitor_sleep(self, ):
        # read frame and take max value: if it is not 0, the monitor is awake
        if np.max(self.original_frame) == 0:
            self.monitor_is_awake = False
        pass

    def prepare_capture(self, path=None):
        self.cap = cv2.VideoCapture(path)

    def set_camera_parameters(self, width=1920, height=1080, fps=60):
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)

    def get_video_parameters(self, ):
        self.total_frame_count = int(self.cap.get(cv2. CAP_PROP_FRAME_COUNT))

    def read_camera_frame(self, ):
        ret, self.original_frame = self.cap.read()
        assert ret, "check camera connection"

    def read_video_frame(self, ):
        self.frame_count += 1
        if self.frame_count == self.total_frame_count:
            self.frames_available = False
        ret, self.original_frame = self.cap.read()

    def read_image(self, path=None):
        d.original_frame = cv2.imread(path)
  
    def prepare_video_writer(self, path=None):
        self.writer = cv2.VideoWriter(
            path,
            cv2.VideoWriter_fourcc('M','J','P','G'), 30, (1920, 2160)
        )

    def write_combined_frame_to_video_writer(self, ):
        self.writer.write(self.combined_frame)

    def release_video_writer(self, ):
        self.writer.release()

if __name__ == '__main__':
    d = Detect(savedir=os.path.join("%USERPROFILE%", "Google Drive", "microscope"))
    cwd = os.path.dirname(__file__)
    d.prepare_capture(os.path.join(cwd, "videos", "1.avi"))
    d.prepare_video_writer(os.path.join(cwd, "videos", "1_result.avi")) # debug
    d.get_video_parameters() # debug
    #d.prepare_capture(0)
    #d.set_camera_parameters(width=1920, height=1080, fps=60)
    while d.frames_available:
        d.read_video_frame()
        d.detect_monitor_wake()
        while d.monitor_is_awake and d.frames_available:
            d.detect_monitor_sleep()
            # Load image.
            d.read_video_frame()
            try:
                #d.read_camera_frame()
                #d.read_image(os.path.join(cwd, "images", "test_images", "2.png"))
                d.preprocess()
                t1 = time.time()
                d.detect_rough() # 35 ms
                d.reset_processed_devices() # 2 ms
                for d.result, d.bbox in zip(d.results, d.bboxes):
                    if d.is_corner_qr(): # get bounding box for only corner QR code
                        d.decode_corner_qr() # 0 ms
                        if d.device_has_not_been_processed(): # process only one corner_QR for each device(x_pos, y_pos)
                            d.extend_bbox() # 0 ms
                            d.crop_frame() # 5 ms
                            ret = d.detect_precise() # 50 ms
                            if ret:
                                d.shift_bounding_box_to_image_coordinate() # 0 ms
                                if d.debug: d.draw_precise_marker_bounding_box() # 0 ms
                                d.get_marker_width() # 0 ms
                                d.get_angle() # 0 ms
                                d.get_marker_corner() # 0 ms
                                d.get_device_corner() # 0 ms
                                if d.debug: d.draw_corner_circles() # 0 ms
                                d.get_device_bounding_box() # 0 ms
                                if d.debug: d.draw_device_bounding_box() # 0 ms
                                if d.debug: d.draw_device_data_text() # 110 ms
                                d.detect_process_qr() # 50 ms
                                if d.debug: d.draw_process_data_text() # 110 ms
                                d.process_frame_for_saving() # 20 ms
                                d.add_to_processed_devices()
                                continue # skip next line
                    if d.debug: d.draw_rough_marker_bounding_box() # 0 ms
                t2 = time.time()
                if d.debug: d.imshow_shrunk_original_frame() # 20 ms
                if d.debug: d.write_combined_frame_to_video_writer() # 5 ms
                print('Time Taken : ', round(1000*(t2 - t1),1), ' ms')
            except Exception as e:
                d.release_video_writer()
                print(e)
        #d.write_processed_frame_to_disk() # write processed frame to disk when monitor goes to sleep
        #while True:
        #    if cv2.waitKey(1) & 0xFF == ord('q'):
        #        break
    cv2.destroyAllWindows()
    d.release_video_writer()

    # 400 ms