from cgitb import small
import cv2
import numpy as np
import os
from contextlib import suppress
from decode_qrcode import *
from encode_qrcode import *
from draw_qr_code import *

cwd = os.path.dirname(__file__)

w_, h_ = 3508, 2480
frame = np.ones((h_, w_, 3))*255
small_frame_ = cv2.imread(os.path.join(cwd, "test", "1.png"))
total_w, total_h = 0, 0
for j in range(3):
    for i in range(2,15):
        small_frame = cv2.resize(small_frame_, (int(small_frame_.shape[1]/i), int(small_frame_.shape[0]/i)))
        h, w = small_frame.shape[:2]
        frame[total_h:total_h+h, total_w:total_w+w] = small_frame
        total_h += h
    total_w += 970
    total_h = 0
    for i in range(15,150):
        small_frame = cv2.resize(small_frame_, (int(small_frame_.shape[1]/i), int(small_frame_.shape[0]/i)))
        h, w = small_frame.shape[:2]
        frame[total_h:total_h+h, total_w:total_w+w] = small_frame
        total_h += h
    total_w += 130
    total_h = 0
    for i in range(150, 1000):
        small_frame = cv2.resize(small_frame_, (int(small_frame_.shape[1]/i), int(small_frame_.shape[0]/i)))
        h, w = small_frame.shape[:2]
        frame[total_h:total_h+h, total_w:total_w+w] = small_frame
        total_h += h
    total_w += 50
    total_h = 0

cv2.imwrite(os.path.join(cwd, "test", "1_print.png"), frame.astype(np.uint8))