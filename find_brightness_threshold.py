import cv2
import numpy as np

# finds brightness threshold to detect the on/off of microscope light
# the threshold uses mean intensity of every pixel
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FPS, 60)
mean_min_ = 1e9
mean_max_ = 0
min_min_ = 1e9
min_max_ = 0
max_min_ = 1e9
max_max_ = 0
for i in range(10000):
    for j in range(100):
        ret, frame = cap.read()
        mean_min_ = min(np.mean(frame), mean_min_)
        mean_max_ = max(np.mean(frame), mean_max_)
        min_min_ = min(np.min(frame), min_min_)
        min_max_ = max(np.min(frame), min_max_)
        max_min_ = min(np.max(frame), max_min_)
        max_max_ = max(np.max(frame), max_max_)
    print(f"(mean) min,max={mean_min_}, {mean_max_}, (min) min,max={min_min_}, {min_max_}, (max) min,max={max_min_}, {max_max_}")
    
# when pc is off: (mean) min,max=129.68402777777777, 129.68402777777777, (min) min,max=0, 0, (max) min,max=255, 255
# when light is off: (mean) min,max=12.984489776234568, 149.94212593235596, (min) min,max=0, 0, (max) min,max=255, 255
# when light is off and sample is on:
# when light is on:
# when light is on and sample is on: