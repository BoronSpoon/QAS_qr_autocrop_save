import os, sys
import numpy as np
cwd = os.path.dirname(__file__)
sys.path.append(os.path.join(cwd, "..", "autocad","autocadshapes"))
from svgpathtools import svg2paths, wsvg
import svgpathtools
from basic_shapes import polyline
layer = "Ag%0_LPC_"

# square qr code
def draw_qr_code_in_cad(path):
    lines, attributes = svg2paths(path)
    polyline_points = []
    for line in lines[0]:
        if type(line) == svgpathtools.path.Line:
            start = [np.real(line.start), np.imag(line.start)]
            end = [np.real(line.end), np.imag(line.end)]
            polyline_points.append(start)
            if end == polyline_points[0]: # if polyline is closed
                polyline(polyline_points, layer) # draw polyline and empty polyline list
                polyline_points = []
        elif type(line) == svgpathtools.path.Curve:
            pass

if __name__ == "__main__":
    cwd = os.path.dirname(__file__)
    # square
    draw_qr_code_in_cad(os.path.join(cwd, "test", "1.svg"))
    # circular
    draw_qr_code_in_cad(os.path.join(cwd, "test", "1.svg"))