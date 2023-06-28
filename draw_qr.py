import pyqrcode
import numpy as np

def string2array(string):
    data = string.split("\n")
    data = [i for i in data if i != ""]
    data = [[int(i) for i in list(j)] for j in data]
    return np.array(data).astype(np.uint8)

def draw_qrcode(error="Q", version=8, string=""):
    qr = pyqrcode.QRCode(string, error=error, version=version, mode="binary", encoding='iso-8859-1')
    frame = string2array(qr.text(quiet_zone=0))
    return frame
    
if __name__ == "__main__":
    frame = draw_qrcode(string="test")
    print(frame)