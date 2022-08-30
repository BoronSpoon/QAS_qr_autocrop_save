import cv2
import sys
import time
import os, sys
import numpy as np
import pyboof as pb
import decode_qrcode
import blur_detector
from textwrap import dedent
cwd = os.path.dirname(__file__)

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

class Detect():        
    red = (0,0,255)
    green = (0,255,0)
    blue = (255,0,0)
    white = (255,255,255)
    black = (0,0,0)
    cwd = os.path.dirname(__file__)
    def __init__(self, savedir, width=1920, height=1080, max_processes=10, debug=False, mode="camera", wake_threshold=129.68402777777777, focus_stacking=False):
        self.mode = mode
        self.wake_threshold = wake_threshold
        self.focus_stacking = focus_stacking
        self.debug = debug # debug mode will write detection result to frame and display it (slow)
        self.savedir = savedir # folder to save the file
        self.buffer = {}
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
        self.bbox_center = np.mean(np.array(self.bbox), axis=0)

    def get_distance(self, point1, point2):
        distance = np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
        return distance

    def get_mean_distance(self, points):
        distance = np.mean(np.sqrt(np.sum(points**2, axis=1)), axis=0)
        return distance

    def get_marker_width(self):
        self.marker_real_width = self.corner_qr_dict[self.device][0]["marker_real_width"]
        self.marker_real_gap = self.corner_qr_dict[self.device][0]["marker_real_gap"]
        self.device_width = self.corner_qr_dict[self.device][0]["device_width"]
        self.device_height = self.corner_qr_dict[self.device][0]["device_height"]
        self.operator_name = self.corner_qr_dict[self.device][0]["operator_name"]
        self.device_name = self.corner_qr_dict[self.device][0]["device_name"]
        self.cx = self.corner_qr_dict[self.device][0]["cx"]
        self.cy = self.corner_qr_dict[self.device][0]["cy"]
        self.ci = self.corner_qr_dict[self.device][0]["ci"]
        self.cj = self.corner_qr_dict[self.device][0]["cj"]
        if d.corner_qr_count_for_device() == 1:
            bbox = self.corner_qr_dict[self.device][0]["bbox"]
            self.marker_width = self.get_mean_distance(np.array([
                [bbox[0][0]-bbox[1][0], bbox[0][1]-bbox[1][1]],
                [bbox[1][0]-bbox[2][0], bbox[1][1]-bbox[2][1]],
                [bbox[2][0]-bbox[3][0], bbox[2][1]-bbox[3][1]],
                [bbox[3][0]-bbox[0][0], bbox[3][1]-bbox[0][1]],
            ]))
            self.marker_gap = self.marker_width*self.marker_real_gap/self.marker_real_width
        elif d.corner_qr_count_for_device() == 2:
            centers = [self.corner_qr_dict[self.device][i]["bbox_center"] for i in range(2)]
            x_pos = [self.corner_qr_dict[self.device][i]["x_pos"] for i in range(2)]
            y_pos = [self.corner_qr_dict[self.device][i]["y_pos"] for i in range(2)]
            dx_pos = x_pos[0] - x_pos[1]
            dy_pos = y_pos[0] - y_pos[1]
            dx = (abs(dx_pos)-1)*self.marker_real_gap/self.marker_real_width + 1 # in multiples of marker_width, gap
            dy = (abs(dy_pos)-1)*self.marker_real_gap/self.marker_real_width + 1
            dd = np.sqrt(dx**2+dy**2)
            distance = self.get_mean_distance(np.array([
                [centers[0][0]-centers[1][0], centers[0][1]-centers[1][1]]
            ]))
            self.marker_width = distance/dd
            self.marker_gap = self.marker_width*self.marker_real_gap/self.marker_real_width

    def get_angle(self):
        if d.corner_qr_count_for_device() == 1:
            bbox = self.corner_qr_dict[self.device][0]["bbox"]
            self.angles = np.zeros(4)
            self.angles[0] = np.arctan2(bbox[2][1] - bbox[3][1], bbox[2][0] - bbox[3][0]) - np.pi*0/2
            self.angles[1] = np.arctan2(bbox[3][1] - bbox[0][1], bbox[3][0] - bbox[0][0]) - np.pi*1/2
            self.angles[2] = np.arctan2(bbox[0][1] - bbox[1][1], bbox[0][0] - bbox[1][0]) - np.pi*2/2
            self.angles[3] = np.arctan2(bbox[1][1] - bbox[2][1], bbox[1][0] - bbox[2][0]) - np.pi*3/2
            self.angles = np.where(self.angles < np.pi, self.angles+np.pi*2, self.angles)
            self.angles = np.where(self.angles < np.pi, self.angles+np.pi*2, self.angles)
            self.angle = np.mean(self.angles)
        elif d.corner_qr_count_for_device() == 2:
            centers = [self.corner_qr_dict[self.device][i]["bbox_center"] for i in range(2)]
            x_pos = [self.corner_qr_dict[self.device][i]["x_pos"] for i in range(2)]
            y_pos = [self.corner_qr_dict[self.device][i]["y_pos"] for i in range(2)]
            dx_pos = x_pos[1] - x_pos[0]
            dy_pos = y_pos[1] - y_pos[0]
            dx = np.sign(dx_pos)*((np.abs(dx_pos)-1)*self.marker_real_gap/self.marker_real_width + 1)
            dy = np.sign(dy_pos)*((np.abs(dy_pos)-1)*self.marker_real_gap/self.marker_real_width + 1)
            phi = np.arctan2(dy, dx)
            theta = np.arctan2(centers[1][1] - centers[0][1], centers[1][0] - centers[0][0])
            self.angle = theta - phi

    def get_marker_corner(self):
        x, y = self.corner_qr_dict[self.device][0]["bbox_center"]
        width, height = self.marker_width/2, self.marker_width/2
        c, s = np.cos(self.angle), np.sin(self.angle)
        self.marker_corner = [x + (c*width-s*height), y + (s*width+c*height)]

    def get_device_corner(self):
        x_pos = self.corner_qr_dict[self.device][0]["x_pos"]
        y_pos = self.corner_qr_dict[self.device][0]["y_pos"]
        width = self.marker_gap * (x_pos-1) + self.marker_width
        height = self.marker_gap * (y_pos-1) + self.marker_width
        x, y = self.marker_corner
        c, s = np.cos(self.angle), np.sin(self.angle)
        self.device_corner = [x - (c*width-s*height), y - (s*width+c*height)]

    def get_device_bounding_box(self, ):
        width = self.marker_gap * self.device_width
        height = self.marker_gap * self.device_height
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
        self.center_x, self.center_y = self.bbox_center
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
        self.bbox_center = np.mean(np.array(self.bbox), axis=0)

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
        return len(self.detector2.detections) > 0

    def shrink_original_frame(self,):
        self.combined_frame = np.vstack([self.original_frame, cv2.cvtColor(self.frame, cv2.COLOR_GRAY2BGR)])

    def imshow_shrunk_original_frame(self,):
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
        if d.focus_stacking:
            if f"{self.cx}_{self.cy}_{self.ci}_{self.cj}" in self.buffer.keys():
                frame = self.buffer[f"{self.cx}_{self.cy}_{self.ci}_{self.cj}"]["frame"]
                focus = self.buffer[f"{self.cx}_{self.cy}_{self.ci}_{self.cj}"]["focus"]
                focus_map = self.buffer[f"{self.cx}_{self.cy}_{self.ci}_{self.cj}"]["focus_map"]
                new_focus = max(self.processed_frame_focus, focus)
                new_focus_map = np.max(self.processed_frame_focus_map, focus_map)
                focus_stacked_processed_frame = np.where(self.processed_frame_focus_map > focus_map, self.processed_frame, frame) # use pixel value of best focused image
                self.buffer[f"{self.cx}_{self.cy}_{self.ci}_{self.cj}"] = {
                    "filename": [self.operator_name, self.device_name, f"{self.process_count}_{self.process_name}", f"{self.cx}_{self.cy}_{self.ci}_{self.cj}.png"],
                    "frame": focus_stacked_processed_frame,
                    "focus": new_focus,
                    "focus_map": new_focus_map,
                }
                return None
        else:
            if f"{self.cx}_{self.cy}_{self.ci}_{self.cj}" in self.buffer.keys():
                focus = self.buffer[f"{self.cx}_{self.cy}_{self.ci}_{self.cj}"]["focus"]
                if focus > self.processed_frame_focus : # if the newly obtained frame's focus is worse, keep the old frame in the buffer
                    return None
        self.buffer[f"{self.cx}_{self.cy}_{self.ci}_{self.cj}"] = {
            "filename": [self.operator_name, self.device_name, f"{self.process_count}_{self.process_name}", f"{self.cx}_{self.cy}_{self.ci}_{self.cj}.png"],
            "frame": self.processed_frame,
            "focus": self.processed_frame_focus,
            "focus_map": self.processed_frame_focus_map,
        }

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
        # detect the on/off of microscope light by mean intensity. if its over threshold, it is awake
        while True:
            if abs(np.mean(self.original_frame) - self.wake_threshold) > 1:
                self.monitor_is_awake = True
                print("monitor is awake")
                break
            time.sleep(10)
    
    def detect_monitor_sleep(self, ):
        # detect the on/off of microscope light by mean intensity. if its over threshold, it is awake
        count = 0
        while True:
            if count > 10:
                self.monitor_is_awake = False
                print("monitor is in sleep")
                break
            if abs(np.mean(self.original_frame) - self.wake_threshold) < 1:
                count += 1
            else:
                break

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

    def get_processed_frame_focus(self, ):
        grayscale_processed_frame = cv2.cvtColor(self.processed_frame, cv2.COLOR_BGR2GRAY)
        self.processed_frame_focus_map = blur_detector.detectBlur(grayscale_processed_frame, downsampling_factor=4, num_scales=4, scale_start=2, num_iterations_RF_filter=3)
        self.processed_frame_focus = np.mean(self.processed_frame_focus_map)

    def qr_is_duplicate(self, ):
        device = f"{self.cx}, {self.cy}, {self.ci}, {self.cj}, {self.device_name}"
        if device not in self.corner_qr_dict.keys():
            return False
        else:
            x_pos0 = self.corner_qr_dict[device][0]["x_pos"]
            x_pos1 = self.x_pos
            y_pos0 = self.corner_qr_dict[device][0]["y_pos"]
            y_pos1 = self.y_pos
            return (x_pos0 == x_pos1) and (y_pos0 == y_pos1)

    def clear_corner_qr_dict(self,):
        self.corner_qr_dict = {}

    def add_to_corner_qr_dict(self, ):
        device = f"{self.cx}, {self.cy}, {self.ci}, {self.cj}, {self.device_name}"
        if device not in self.corner_qr_dict.keys():
            self.corner_qr_dict[device] = [{
                "x_pos": self.x_pos,
                "y_pos": self.y_pos,
                "bbox": self.bbox,
                "bbox_center": self.bbox_center,
                "marker_real_width": self.marker_real_width,
                "marker_real_gap": self.marker_real_gap,
                "device_width": self.device_width,
                "device_height": self.device_height,
                "operator_name": self.operator_name,
                "device_name": self.device_name,
                "cx": self.cx,
                "cy": self.cy,
                "ci": self.ci,
                "cj": self.cj,
            }]
        else:
            self.corner_qr_dict[device].append({
                "x_pos": self.x_pos,
                "y_pos": self.y_pos,
                "bbox": self.bbox,
                "bbox_center": self.bbox_center,
                "marker_real_width": self.marker_real_width,
                "marker_real_gap": self.marker_real_gap,
                "device_width": self.device_width,
                "device_height": self.device_height,
                "operator_name": self.operator_name,
                "device_name": self.device_name,
                "cx": self.cx,
                "cy": self.cy,
                "ci": self.ci,
                "cj": self.cj,
            })

    def corner_qr_count_for_device(self, ):
        device = f"{self.cx}, {self.cy}, {self.ci}, {self.cj}, {self.device_name}"
        if device in self.corner_qr_dict:
            return len(self.corner_qr_dict[device])
        else:
            return 0

if __name__ == '__main__':
    cwd = os.path.dirname(__file__)
    #d = Detect(savedir=os.path.join("%USERPROFILE%", "Google Drive", "microscope"), mode="camera")
    d = Detect(savedir=os.path.join(cwd, "test"), mode="video", debug=True)
    if d.mode == "video": d.prepare_capture(os.path.join(cwd, "test", "1.avi"))
    if d.mode == "video" and d.debug: d.prepare_video_writer(os.path.join(cwd, "test", "1_result.avi"))
    d.get_video_parameters() # debug
    if d.mode == "camera": d.prepare_capture(0)
    if d.mode == "camera": d.set_camera_parameters(width=1920, height=1080, fps=60)
    while d.frames_available:
        if d.mode == "video": d.read_video_frame()
        d.detect_monitor_wake()
        while d.monitor_is_awake and d.frames_available:
            d.detect_monitor_sleep()
            # Load image.
            if d.mode == "video": d.read_video_frame()
            if d.mode == "camera": d.read_camera_frame()
            if d.mode == "image": d.read_image(os.path.join(cwd, "images", "test_images", "2.png"))
            d.preprocess()
            t1 = time.time()
            d.detect_rough() # 35 ms
            d.clear_corner_qr_dict()
            for d.result, d.bbox in zip(d.results, d.bboxes):
                if d.is_corner_qr(): # get bounding box for only corner QR code
                    d.decode_corner_qr() # 0 ms
                    if d.corner_qr_count_for_device() < 2: # limit to 2 corner qrs
                        if not d.qr_is_duplicate(): # if qr is not duplicate
                            d.extend_bbox() # 0 ms
                            d.crop_frame() # 5 ms
                            ret = d.detect_precise() # 50 ms
                            if ret:
                                d.shift_bounding_box_to_image_coordinate() # 0 ms
                                if d.debug: d.draw_precise_marker_bounding_box() # 0 ms
                                d.add_to_corner_qr_dict()
            for d.device in d.corner_qr_dict.keys():
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
                #d.process_frame_for_saving() # 20 ms
                #d.get_processed_frame_focus() # ?
                #d.store_processed_frame_to_ram() # ?
            if d.debug: d.draw_rough_marker_bounding_box() # 0 ms
            t2 = time.time()
            if d.mode == "video" and d.debug: d.shrink_original_frame()
            if d.debug: d.imshow_shrunk_original_frame() # 20 ms
            if d.mode == "video" and d.debug: d.write_combined_frame_to_video_writer() # 5 ms
            print('Time Taken : ', round(1000*(t2 - t1),1), ' ms')
        d.write_processed_frame_to_disk() # write processed frame to disk when monitor goes to sleep
    cv2.destroyAllWindows()
    d.release_video_writer()

    # 330 ms debug and video mode
    # 100 ms video mode
    # ? ms camera mode