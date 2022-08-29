import qrcode
import numpy as np
import cv2

def pillow2cv2(frame_):
    frame = np.array(frame_, dtype=np.uint8)
    if frame.ndim == 2: # grayscale
        pass
    elif frame.shape[2] == 3: # rgb->bgr
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    elif frame.shape[2] == 4:  # rgba->bgra
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGRA)
    return frame

def draw_qrcode(version=4, box_size=4, string=""):
    qr = qrcode.QRCode(
        version=version,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=box_size,
        border=0,
    )
    qr.add_data(string)
    qr.make(fit=True)
    return pillow2cv2(qr.make_image(fill_color=(255,255,255), back_color=(0,0,0)))