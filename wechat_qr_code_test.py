import cv2
import sys
import time
import os
import numpy as np
cwd = os.path.dirname(__file__)

def displayBbox(im, bboxes):
    if bboxes is not None:
        bboxes = [bbox.astype(np.int32) for bbox in bboxes]
        cv2.polylines(im, bboxes, True, (0,0,255), 3)

if __name__ == '__main__':
    detector = cv2.wechat_qrcode_WeChatQRCode(
        os.path.join(cwd, "model", "detect.prototxt"),
        os.path.join(cwd, "model", "detect.caffemodel"),
        os.path.join(cwd, "model", "sr.prototxt"),
        os.path.join(cwd, "model", "sr.caffemodel")
    )
    
    #img = cv2.imread(os.path.join(cwd, "test", "test_qr.png"))
    img = cv2.imread(os.path.join(cwd, "test", "2.png"))
    img = np.where(img<200, 255, 0).astype(np.uint8)
    #cv2.imshow("a", img)
    #cv2.waitKey(0)
 
    t1 = time.time()
    # Detect and decode.
    res, points = detector.detectAndDecode(img)
    t2 = time.time()
    # Detected outputs.
    if len(res) > 0:
        print('Time Taken : ', round(1000*(t2 - t1),1), ' ms')
        print('Output : ', res[0])
        print('Bounding Box : ', points)
        displayBbox(img, points)
    else:
        print('QRCode not detected')

    img = cv2.resize(img, (0,0), fx=0.5, fy=0.5) 
    cv2.imshow("Image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()