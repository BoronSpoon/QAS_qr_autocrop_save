import pyqrcode
import numpy as np
import cv2

def string2array(string):
    data = string.split("\n")
    data = [i for i in data if i != ""]
    data = [[int(i) for i in list(j)] for j in data]
    return np.array(data).astype(np.uint8)

def get_qrcode_pixels(string="", error="Q", version=8):
    qr = pyqrcode.QRCode(string, error=error, version=version, mode="binary", encoding='iso-8859-1')
    data = string2array(qr.text(quiet_zone=0))
    return data

def draw_qrcode_cv2(px_size=10, string="", error="Q", version=8, data=None):
    if data is None:
        data = get_qrcode_pixels(string=string, error=error, version=version)
    frame = cv2.resize(255-data*255, (0, 0), fx=px_size, fy=px_size, interpolation=0)
    return frame

def draw_qrcode_polylines(xmin, ymin, px_size, string="", error="Q", version=8, data=None):
    if data is None:
        data = get_qrcode_pixels(string=string, error=error, version=version)
    polylines = []
    for y in range(data.shape[0]):
        for x in range(data.shape[1]):
            if data[y][x] == 1:
                polylines.append([
                    [xmin + x*px_size,     ymin + y*px_size],
                    [xmin + x*px_size,     ymin + (y+1)*px_size],
                    [xmin + (x+1)*px_size, ymin + (y+1)*px_size],
                    [xmin + (x+1)*px_size, ymin + y*px_size],
                ])
    return polylines
    
if __name__ == "__main__":
    data = get_qrcode_pixels(string="test")
    print(data)