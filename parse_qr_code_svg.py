import os, sys
import numpy as np
cwd = os.path.dirname(__file__)
sys.path.append(os.path.join(cwd, "..", "autocad","autocadshapes"))
from svgpathtools import svg2paths, wsvg
import svgpathtools
from basic_shapes import square, circle
layer = "Ag%0_LPC_"

def get_total_width_of_qr_code(path, width, gap):
    lines, attributes = svg2paths(path)
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

# square qr code
def draw_qr_code_in_cad(path, shape="square", x0=0, y0=0, width=1, gap=0):
    total_width = get_total_width_of_qr_code(path, width, gap)
    lines, attributes = svg2paths(path)
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
    cwd = os.path.dirname(__file__)
    # square
    draw_qr_code_in_cad(os.path.join(cwd, "test", "1.svg"), x0=0, y0=0, width=3) # width(=height) of one pixel in micrometers
    # circular
    draw_qr_code_in_cad(os.path.join(cwd, "test", "1.svg"), shape="circle", x0=110, y0=0, width=1, gap=0.5) # width(=height) of one pixel in micrometers