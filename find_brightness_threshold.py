import cv2
import numpy as np

# finds brightness threshold to detect the on/off of microscope light
# the threshold uses mean intensity of every pixel
cap = cv2.VideoCapture(0)
min_ = 0
max_ = 1e9
for i in range(10000):
    for j in range(100):
        ret, frame = cap.read()
        intensity = np.mean(frame)
        min_ = min(intensity, min_)
        max_ = max(intensity, max_)
    print(f"min, max = {min_}, {max_}")
    