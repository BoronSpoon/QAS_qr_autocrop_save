import cv2
import sys
import time
import os
cwd = os.path.dirname(__file__)

def displayBbox(im, bbox):
    if bbox is not None:
        bbox = [bbox[0].astype(int)]
        n = len(bbox[0])
        for i in range(n):
            cv2.line(im, tuple(bbox[0][i]), tuple(bbox[0][(i+1) % n]), (0,255,0), 3)

if __name__ == '__main__':
    detector = cv2.wechat_qrcode_WeChatQRCode(
        os.path.join(cwd, "model", "detect.prototxt"),
        os.path.join(cwd, "model", "detect.caffemodel"),
        os.path.join(cwd, "model", "sr.prototxt"),
        os.path.join(cwd, "model", "sr.caffemodel")
    )
    
    #img = cv2.imread(os.path.join(cwd, "test", "test_qr.png"))
    img = cv2.imread(os.path.join(cwd, "test", "2.png"))
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
 
    cv2.imshow("Image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()