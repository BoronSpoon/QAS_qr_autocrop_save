import qrcode
import numpy as np
import cv2
import os
import qrcode.image.svg
from qrcode.image.styles.moduledrawers import SquareModuleDrawer, CircleModuleDrawer

def draw_and_save_qrcode(version=4, box_size=4, string="", path=None):
    qr = qrcode.QRCode(
        version=version,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=box_size,
        border=0,
        image_factory=qrcode.image.svg.SvgPathImage,
    )
    qr.add_data(string)
    qr.make(fit=True)
    img = str(qr.make_image(fill_color=(255,255,255), back_color=(0,0,0)).to_string)
    with open(path, "w") as f:
        img = str.replace(img, "mm", "") # remove units
        f.write(img[2:-1]) # remove b''

if __name__ == "__main__":
    cwd = os.path.dirname(__file__)
    draw_and_save_qrcode(version=4, box_size=4, string="test123", path=os.path.join(cwd, "test", "1.svg"))