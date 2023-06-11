import cv2
import numpy as np
import os
from contextlib import suppress
from decode_qrcode import *
from encode_qrcode import *
import sys
sys.path.append("test")
from draw_qr_code import *

def rotate_marker(frame_, angle, h, w):
    h_, w_ = frame_.shape[:2]
    center = (w/2, h/2)
    frame = cv2.copyMakeBorder(frame_, int((h-h_)/2), int((h-h_)/2), int((w-w_)/2), int((w-w_)/2), borderType=cv2.BORDER_CONSTANT)
    M = cv2.getRotationMatrix2D(center=center, angle=-angle*360/(2*np.pi), scale=1)
    frame = cv2.warpAffine(frame, M, (w, h), borderValue=(0,0,0))
    return frame

def calculate_mask(frame):
    return np.where(frame > 1, 0, 1)

cwd = os.path.dirname(__file__)
markers = {}
rotated_markers = {}
masks = {}
for input_, output_, x, y, dx, dy, angle in [
    ["microscope_1.jpg", "1.png", 160, 250, 9, 4, 0],
    ["microscope_2.jpg", "2.png", 150, 100, 12, 4, np.pi/14],
]:
    markers["TL"] = draw_qrcode(version=1, string=encode_corner_qr(x_pos=0,    y_pos=dy+1, device_width=dx, device_height=dy, marker_size=87e-6, marker_gap=87e-6, cx=4, cy=5, ci=1, cj=0, operator_name="yamada", sample_name="encoding test"))
    markers["TR"] = draw_qrcode(version=1, string=encode_corner_qr(x_pos=dx+1, y_pos=dy+1,    device_width=dx, device_height=dy, marker_size=87e-6, marker_gap=87e-6, cx=4, cy=5, ci=1, cj=0, operator_name="yamada", sample_name="encoding test"))
    markers["BL"] = draw_qrcode(version=1, string=encode_corner_qr(x_pos=0,    y_pos=0,    device_width=dx, device_height=dy, marker_size=87e-6, marker_gap=87e-6, cx=4, cy=5, ci=1, cj=0, operator_name="yamada", sample_name="encoding test"))
    markers["BR"] = draw_qrcode(version=1, string=encode_corner_qr(x_pos=dx+1, y_pos=0, device_width=dx, device_height=dy, marker_size=87e-6, marker_gap=87e-6, cx=4, cy=5, ci=1, cj=0, operator_name="yamada", sample_name="encoding test"))

    markers["P0"] = draw_qrcode(version=2, string=encode_process_qr(process_count=0, process_name="process test 0"))
    markers["P1"] = draw_qrcode(version=2, string=encode_process_qr(process_count=1, process_name="process test 1"))
    markers["P2"] = draw_qrcode(version=2, string=encode_process_qr(process_count=2, process_name="process test 2"))
    markers["P3"] = draw_qrcode(version=2, string=encode_process_qr(process_count=3, process_name="process test 3"))
    markers["P4"] = draw_qrcode(version=2, string=encode_process_qr(process_count=4, process_name="process test 4"))
    markers["P5"] = draw_qrcode(version=2, string=encode_process_qr(process_count=5, process_name="process test 5"))
    
    c, s = np.cos(angle), np.sin(angle)
    my_, mx_ = markers["TL"].shape[:2]
    my, mx = int(abs(c*my_)+abs(s*mx_)), int(abs(c*mx_)+abs(s*my_))
    for key in markers.keys():
        rotated_markers[key] = np.where(rotate_marker(markers[key], angle, my, mx)>127,255,0)
        masks[key] = calculate_mask(rotated_markers[key])
    frame = cv2.imread(os.path.join(cwd, "test", input_))
    # corner qr codes
    with suppress(ValueError): cx, cy = x+c*mx_*0 -s*my_*0,          y+s*mx_*0 +c*my_*0;          frame[int(cy-my/2) :int(cy+my/2), int(cx-mx/2) :int(cx+mx/2)] = frame[int(cy-my/2) :int(cy+my/2), int(cx-mx/2) :int(cx+mx/2)] * masks["TL"] + rotated_markers["TL"]
    with suppress(ValueError): cx, cy = x+c*mx_*(dx+1)-s*my_*0,      y+s*mx_*(dx+1)+c*my_*0;      frame[int(cy-my/2) :int(cy+my/2), int(cx-mx/2) :int(cx+mx/2)] = frame[int(cy-my/2) :int(cy+my/2), int(cx-mx/2) :int(cx+mx/2)] * masks["TR"] + rotated_markers["TR"]
    with suppress(ValueError): cx, cy = x+c*mx_*0 -s*my_*(dy+1),     y+s*mx_*0 +c*my_*(dy+1);     frame[int(cy-my/2) :int(cy+my/2), int(cx-mx/2) :int(cx+mx/2)] = frame[int(cy-my/2) :int(cy+my/2), int(cx-mx/2) :int(cx+mx/2)] * masks["BL"] + rotated_markers["BL"]
    with suppress(ValueError): cx, cy = x+c*mx_*(dx+1)-s*my_*(dy+1), y+s*mx_*(dx+1)+c*my_*(dy+1); frame[int(cy-my/2) :int(cy+my/2), int(cx-mx/2) :int(cx+mx/2)] = frame[int(cy-my/2) :int(cy+my/2), int(cx-mx/2) :int(cx+mx/2)] * masks["BR"] + rotated_markers["BR"]
    # process qr codes
    with suppress(ValueError): cx, cy = x+c*mx_*1-s*my_*0, y+s*mx_*1+c*my_*0; frame[int(cy-my/2) :int(cy+my/2), int(cx-mx/2) :int(cx+mx/2)] = frame[int(cy-my/2) :int(cy+my/2), int(cx-mx/2) :int(cx+mx/2)] * masks["P0"] + rotated_markers["P0"]
    with suppress(ValueError): cx, cy = x+c*mx_*2-s*my_*0, y+s*mx_*2+c*my_*0; frame[int(cy-my/2) :int(cy+my/2), int(cx-mx/2) :int(cx+mx/2)] = frame[int(cy-my/2) :int(cy+my/2), int(cx-mx/2) :int(cx+mx/2)] * masks["P1"] + rotated_markers["P1"]
    # with suppress(ValueError): cx, cy = x+c*mx_*3-s*my_*0, y+s*mx_*3+c*my_*0; frame[int(cy-my/2) :int(cy+my/2), int(cx-mx/2) :int(cx+mx/2)] = frame[int(cy-my/2) :int(cy+my/2), int(cx-mx/2) :int(cx+mx/2)] * masks["P2"] + rotated_markers["P2"]
    with suppress(ValueError): cx, cy = x+c*mx_*4-s*my_*0, y+s*mx_*4+c*my_*0; frame[int(cy-my/2) :int(cy+my/2), int(cx-mx/2) :int(cx+mx/2)] = frame[int(cy-my/2) :int(cy+my/2), int(cx-mx/2) :int(cx+mx/2)] * masks["P3"] + rotated_markers["P3"]
    with suppress(ValueError): cx, cy = x+c*mx_*5-s*my_*0, y+s*mx_*5+c*my_*0; frame[int(cy-my/2) :int(cy+my/2), int(cx-mx/2) :int(cx+mx/2)] = frame[int(cy-my/2) :int(cy+my/2), int(cx-mx/2) :int(cx+mx/2)] * masks["P4"] + rotated_markers["P4"]
    with suppress(ValueError): cx, cy = x+c*mx_*6-s*my_*0, y+s*mx_*6+c*my_*0; frame[int(cy-my/2) :int(cy+my/2), int(cx-mx/2) :int(cx+mx/2)] = frame[int(cy-my/2) :int(cy+my/2), int(cx-mx/2) :int(cx+mx/2)] * masks["P5"] + rotated_markers["P5"]
    cv2.imwrite(os.path.join(cwd, "test", output_), frame)
    while(True):
        cv2.imshow("frame", cv2.resize(frame, (int(frame.shape[1]/2),int(frame.shape[0]/2))))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break