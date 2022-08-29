from math import ceil, log2
from skimage import transform as tf
import cv2

def dec(binary):
    return int(binary,2)

def read_bit_range(start, count, bits):
    return 2**(count+1) & bits >> start

class Capture():
    def __init__(self, ):
        width = 1920
        height = 1080
    def capture(self, ):
        ret, frame = self.cap.read()
    def rotate_image(self, ):
        M = cv2.getRotationMatrix2D((height/2, width/2), angle, 1)
        rotated_image = cv2.warpAffine(frame, M, (height, width), borderValue=(0,0,0,0))
    def read_rune(self, ):
        pass
    def find_rune_corners(self, ):
        bottom_right_x, bottom_right_y, width, slope, bits = self.read_rune()
        x_position_is_at_max = read_bit_range(0, 1, bits)
        y_position_is_at_max = read_bit_range(1, 1, bits)
        x_position = read_bit_range(2, 6, bits)
        y_position = read_bit_range(8, 6, bits)
        self.x0 = bottom_right_x - x_position*width*slope
        self.y0 = bottom_right_y - y_position*width*slope
        #self.tform_params = tf.estimate_transform('similarity', src, dst).params
    def read_qr_device_info(self, ):
        pass
    def find_bounding_boxes(self, ):
        pass
    def read_qr_process_info(self, ):
        pass
    def load_image_from_disk(self, ):
        pass
    def save_image_to_disk(self, ):
        pass