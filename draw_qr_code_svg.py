import qrcode
import numpy as np
import cv2
import os
import qrcode.image.svg
from qrcode.image.styles.moduledrawers import SquareModuleDrawer, CircleModuleDrawer

def draw_and_save_qrcode(version=4, box_size=4, string="", shape="square", path=None):
    qr = qrcode.QRCode(
        version=version,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=box_size,
        border=0,
        image_factory=qrcode.image.svg.SvgPathImage,
    )
    qr.add_data(string)
    qr.make(fit=True)
    if shape is None:
        img = qr.make_image(fill_color=(255,255,255), back_color=(0,0,0))
    elif shape is not None:
        img = qr.make_image(fill_color=(255,255,255), back_color=(0,0,0), module_drawer=shape)
    with open(path, "wb") as f:
        img.save(f)

if __name__ == "__main__":
    cwd = os.path.dirname(__file__)
    print(dir(qrcode.image.styles.moduledrawers))
    draw_and_save_qrcode(version=4, box_size=4, string="test123", path=os.path.join(cwd, "test", "1.svg"))
    draw_and_save_qrcode(version=4, box_size=4, string="test123", shape=CircleModuleDrawer, path=os.path.join(cwd, "test", "2.svg"))