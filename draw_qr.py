import pyqrcode
import numpy as np

def string2array(string):
    data = string.split("\n")
    data = [i for i in data if i != ""]
    data = [[int(i) for i in list(j)] for j in data]
    return np.array(data).astype(np.uint8)

def draw_qrcode(string="", error="Q", version=8):
    qr = pyqrcode.QRCode(string, error=error, version=version, mode="binary", encoding='iso-8859-1')
    data = string2array(qr.text(quiet_zone=0))
    return data
    
if __name__ == "__main__":
    data = draw_qrcode(string="test")
    print(data)