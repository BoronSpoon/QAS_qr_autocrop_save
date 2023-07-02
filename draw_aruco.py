import numpy as np
import os
import cv2
from draw_qr import *

def get_aruco_pixels(dictionary=cv2.aruco.DICT_4X4_1000, id=0):
    dictionary = cv2.aruco.getPredefinedDictionary(dictionary)
    bits_count = dictionary.markerSize+2
    data = cv2.aruco.generateImageMarker(dictionary, id, sidePixels=bits_count) # add borderbits
    return data

def draw_aruco_cv2(px_size=10, dictionary=cv2.aruco.DICT_4X4_1000, id=0, data=None):
    if data is None:
        data = get_aruco_pixels(dictionary=dictionary, id=id)
    frame = cv2.resize(255-data*255, (0, 0), fx=px_size, fy=px_size, interpolation=0)
    return frame

def draw_aruco_polylines(xmin, ymin, px_size, dictionary=cv2.aruco.DICT_4X4_1000, id=0, data=None):
    if data is None:
        data = get_aruco_pixels(dictionary=dictionary, id=id)
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
    frame = get_aruco_pixels(id=100)