import qrcode
import numpy as np
import cv2
import os
import qrcode.image.svg

def draw_and_save_qrcode(version=4, box_size=4, string=""):
    cwd = os.path.dirname(__file__)
    qr = qrcode.QRCode(
        version=version,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=box_size,
        border=0,
        image_factory=qrcode.image.svg.SvgPathImage,
    )
    qr.add_data(string)
    qr.make(fit=True)
    img = qr.make_image(fill_color=(255,255,255), back_color=(0,0,0))
    with open(os.path.join(cwd, "test", "1.svg"), "wb") as f:
        img.save(f)

if __name__ == "__main__":
    draw_and_save_qrcode(version=4, box_size=4, string="test123")
