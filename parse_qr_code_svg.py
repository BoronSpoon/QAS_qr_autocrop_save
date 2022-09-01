import os, sys
import numpy as np
cwd = os.path.dirname(__file__)
sys.path.append(os.path.join(cwd, "..", "autocad","autocadshapes"))
from svgpathtools import svg2paths, wsvg
import svgpathtools
from basic_shapes import square
layer = "Ag%0_LPC_"

def get_total_width_and_zoom_of_qr_code(path, width, gap):
    lines, attributes = svg2paths(path)
    polyline_points = []
    min_x = 1e9
    max_x = -1e9
    for line in lines[0]:
        start = [np.real(line.start), np.imag(line.start)]
        end = [np.real(line.end), np.imag(line.end)]
        polyline_points.append(start)
        if end == polyline_points[0]: # if polyline is closed
            x, y = np.mean(np.array(polyline_points), axis=0)
            min_x, max_x = min(np.min(np.array(polyline_points)[:,0]), min_x), max(np.max(np.array(polyline_points)[:,0]), max_x)
            zoom = (width + gap)/(max_x - min_x)
            polyline_points = []
    total_width = max_x - min_x
    return total_width, zoom

# square qr code
def draw_qr_code_in_cad(path, x0=0, y0=0, width=1, gap=0):
    total_width, zoom = get_total_width_and_zoom_of_qr_code(path, width, gap)
    lines, attributes = svg2paths(path)
    polyline_points = []
    for line in lines[0]:
        if type(line) == svgpathtools.path.Line:
            start = [np.real(line.start), np.imag(line.start)]
            end = [np.real(line.end), np.imag(line.end)]
            polyline_points.append(start)
            if end == polyline_points[0]: # if polyline is closed
                x, y = np.mean(np.array(polyline_points), axis=0)
                min_x, max_x = np.min(np.array(polyline_points)[:,0]), np.max(np.array(polyline_points)[:,0])
                zoom = (width + gap)/(max_x - min_x)
                # draw polyline and empty polyline list
                # invert y and move bottom left to (x0, y0)
                square(x0+x*zoom, y0+(total_width-y)*zoom, width, width, xy0_position="center", layer=layer)
                polyline_points = []
        elif type(line) == svgpathtools.path.Curve:
            pass

if __name__ == "__main__":
    cwd = os.path.dirname(__file__)
    # square
    draw_qr_code_in_cad(os.path.join(cwd, "test", "1.svg"), x0=0, y0=0, width=3) # width(=height) of one pixel in micrometers
    # circular
    draw_qr_code_in_cad(os.path.join(cwd, "test", "1.svg"), x0=110, y0=0, width=1, gap=0.5) # width(=height) of one pixel in micrometers