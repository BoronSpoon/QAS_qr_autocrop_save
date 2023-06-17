import numpy as np
import os
import cv2

def draw_aruco(dictionary=cv2.aruco.DICT_4X4_1000, id=0):
    dictionary = cv2.aruco.getPredefinedDictionary(dictionary)
    bits_count = dictionary.markerSize+2
    data = cv2.aruco.generateImageMarker(dictionary, id, sidePixels=bits_count) # add borderbits
    return data
    
if __name__ == "__main__":
    frame = draw_aruco(id=100)