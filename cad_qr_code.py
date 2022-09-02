import qrcode
import cv2
import qrcode.image.svg
from qrcode.image.styles.moduledrawers import SquareModuleDrawer, CircleModuleDrawer
import os, sys
import numpy as np
cwd = os.path.dirname(__file__)
sys.path.append(os.path.join(cwd, "..", "autocad","autocadshapes"))
from basic_shapes import square, circle
from svgpathtools import svg2paths, wsvg
import svgpathtools
import io

def qr_code(x0=0, y0=0, width=3, gap=0, text="test123", shape="square", version=4, layer=None):
    svg_bytes = draw_and_save_qrcode(version, text)
    draw_qr_code_in_cad(svg_bytes, x0, y0, width, gap, shape, layer) # width(=height) of one pixel in micrometers

def draw_and_save_qrcode(version, text):
    qr = qrcode.QRCode(
        version=version,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=10, 
        border=0,
        image_factory=qrcode.image.svg.SvgPathImage,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color=(255,255,255), back_color=(0,0,0)).to_string().decode("utf-8")
    img = str.replace(img, "mm", "") # remove units
    img = img.encode("utf-8")
    return img

def get_total_width_of_qr_code(svg_bytes):
    with io.BytesIO() as b:
        b.write(svg_bytes)
        b.seek(0)
        lines, attributes = svg2paths(b)
    polyline_points = []
    min_x = 1e9
    max_x = -1e9
    for line in lines[0]:
        start = [np.real(line.start), np.imag(line.start)]
        end = [np.real(line.end), np.imag(line.end)]
        polyline_points.append(start)
        if end == polyline_points[0]: # if polyline is closed
            min_x, max_x = min(np.min(np.array(polyline_points)[:,0]), min_x), max(np.max(np.array(polyline_points)[:,0]), max_x)
            polyline_points = []
    total_width = max_x - min_x
    return total_width

def draw_qr_code_in_cad(svg_bytes, x0, y0, width, gap, shape, layer):
    total_width = get_total_width_of_qr_code(svg_bytes)
    with io.BytesIO() as b:
        b.write(svg_bytes)
        b.seek(0)
        lines, attributes = svg2paths(b)
    polyline_points = []
    for line in lines[0]:
        if type(line) == svgpathtools.path.Line:
            start = [np.real(line.start), np.imag(line.start)]
            end = [np.real(line.end), np.imag(line.end)]
            polyline_points.append(start)
            if end == polyline_points[0]: # if polyline is closed, draw polyline and empty polyline list
                cx, cy = np.mean(np.array(polyline_points), axis=0)
                # invert y and move bottom left to (x0, y0)
                if shape == "square":
                    x, y = x0+cx*(width+gap), y0+(total_width-cy)*(width+gap)
                    square(x, y, width, width, xy0_position="center", layer=layer)
                elif shape == "circle":
                    x, y = x0+cx*(width+gap), y0+(total_width-cy)*(width+gap)
                    x_count, y_count = cx, total_width-cy # bottom left is 0,0
                    # aliment markers should be square even for circular qr code
                    if (x_count < 7 and y_count < 7) or (x_count < 7 and y_count > total_width-7) or (x_count > total_width-7 and y_count > total_width-7) or (total_width-9 < x_count < total_width-4 and 4 < y_count < 9): # the alignment marker is 1+1+3+1+1=7 blocks wide
                        square(x, y, (width+gap), (width+gap), xy0_position="center", layer=layer) # draw square alignment marker
                    else:
                        circle(x, y, width, xy0_position="center", layer=layer)
                    
                polyline_points = []
        elif type(line) == svgpathtools.path.Curve:
            pass

if __name__ == "__main__":
    # square
    qr_code(x0=0, y0=0, width=3, text="square_test", layer = "Ag%0_LPC_") # width(=height) of one pixel in micrometers
    # circular
    qr_code(x0=110, y0=0, width=1, text="circle_test", gap=0.5, shape="circle", layer = "Ag%0_LPC_") # width(=height) of one pixel in micrometers