from datetime import datetime

alphanumeric_count = 45
numeric2alphanumeric_dict = {
    0: "0",
    1: "1",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    8: "8",
    9: "9",
    10: "A",
    11: "B",
    12: "C",
    13: "D",
    14: "E",
    15: "F",
    16: "G",
    17: "H",
    18: "I",
    19: "J",
    20: "K",
    21: "L",
    22: "M",
    23: "N",
    24: "O",
    25: "P",
    26: "Q",
    27: "R",
    28: "S",
    29: "T",
    30: "U",
    31: "V",
    32: "W",
    33: "X",
    34: "Y",
    35: "Z",
    36: " ",
    37: "$",
    38: "%",
    39: "*",
    40: "+",
    41: "-",
    42: ".",
    43: "/",
    44: ":",
}

def numeric2alphanumeric(numeric, string_count=None):
    string = ""
    if string_count is None:
        string_count = 100
    for i in range(string_count):
        numeric_ = numeric % alphanumeric_count
        numeric = numeric // alphanumeric_count
        string += numeric2alphanumeric_dict[numeric_]
    return string[:string_count]

def binary2alphanumeric(binary, string_count=None):
    numeric = int(binary, 2)
    return numeric2alphanumeric(numeric, string_count)

def encode_corner_qr(x_pos=0, y_pos=0, device_width=10, device_height=5, marker_size=87e-6, marker_gap=87e-6, cx=0, cy=0, ci=0, cj=0, operator_name="", sample_name=""):
    # total 47 alphanumeric letters
    string = ""
    # position (16 bits)
    # alphanumeric*1 (bit 0: 0, indicates corner QR)
    string += binary2alphanumeric("0", string_count=1)
    # x position: alphanumeric*2
    string += numeric2alphanumeric(x_pos, string_count=2)
    # y position: alphanumeric*2
    string += numeric2alphanumeric(y_pos, string_count=2)
    # device_width (in multiple of marker gap): alphanumeric*2
    string += numeric2alphanumeric(device_width, string_count=2)
    # device_height (in multiple of marker gap): alphanumeric*2
    string += numeric2alphanumeric(device_height, string_count=2)
    # marker size (6 numbers: 1.0422e-6->104226)
    # alphanumeric*4
    marker_size = f"{marker_size:.4e}"
    marker_size = int(marker_size[0] + marker_size[2:6] + marker_size[-1])
    string += numeric2alphanumeric(marker_size, string_count=4)
    # marker gap (6 numbers: 1.0422e-6->104226)
    # alphanumeric*4
    marker_gap = f"{marker_gap:.4e}"
    marker_gap = int(marker_gap[0] + marker_gap[2:6] + marker_gap[-1])
    string += numeric2alphanumeric(marker_size, string_count=4)
    # count (2*4 numbers: x,y,i,j)
    # alphanumeric*2
    string += numeric2alphanumeric(cx, string_count=2)
    string += numeric2alphanumeric(cy, string_count=2)
    string += numeric2alphanumeric(ci, string_count=2)
    string += numeric2alphanumeric(cj, string_count=2)
    # operator_name (8 letters: yamada)
    # alphanumeric*8
    assert len(str(operator_name)) <= 8
    if operator_name == "": # if operator is empty, fill with placeholder
        operator_name = "john doe"
    string += operator_name.ljust(8)
    # sample name (14 letters: TY_test_condition)
    # alphanumeric*14
    assert len(sample_name) <= 14
    if sample_name == "": # if sample name is empty, fill with date and time
        sample_name = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    string += sample_name.ljust(14) # pad with spaces
    return string

def encode_process_qr(process_count=0, process_name=""):
    # total 29 alphanumeric letters
    string = ""
    # indication of process QR (2 bit: 1)
    # alphanumeric*1
    string += binary2alphanumeric("1", string_count=1)
    # process count (3 numbers: 001)
    # alphanumeric*2
    string += numeric2alphanumeric(process_count, string_count=2)
    # process name (26 letters: TY_test_condition)
    # alphanumeric*26
    assert len(process_name) <= 26
    if process_name == "": # if sample name is empty, fill with date and time
        process_name = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    string += process_name.ljust(22) # pad with spaces
    return string

if __name__ == "__main__":
    from decode_qrcode import *
    result0 = encode_corner_qr(x_pos=0, y_pos=0, device_width=10, device_height=5, marker_size=87e-6, marker_gap=87e-6, cx=4, cy=5, ci=1, cj=0, operator_name="yamada", sample_name="encoding test")
    result1 = encode_corner_qr(x_pos=9, y_pos=0, device_width=10, device_height=5, marker_size=87e-6, marker_gap=87e-6, cx=4, cy=5, ci=1, cj=0, operator_name="yamada", sample_name="encoding test")
    result2 = encode_corner_qr(x_pos=0, y_pos=4, device_width=10, device_height=5, marker_size=87e-6, marker_gap=87e-6, cx=4, cy=5, ci=1, cj=0, operator_name="yamada", sample_name="encoding test")
    result3 = encode_corner_qr(x_pos=9, y_pos=4, device_width=10, device_height=5, marker_size=87e-6, marker_gap=87e-6, cx=4, cy=5, ci=1, cj=0, operator_name="yamada", sample_name="encoding test")
    result4 = encode_process_qr(process_count=0, process_name="process 0")
    result5 = encode_process_qr(process_count=1, process_name="process 1")
    result6 = encode_process_qr(process_count=2, process_name="process 2")

    print(result0)
    print(result1)
    print(result2)
    print(result3)
    print(result4)
    print(result5)
    print(result6)

    print(classify_qr(result0))
    print(classify_qr(result1))
    print(classify_qr(result2))
    print(classify_qr(result3))
    print(classify_qr(result4))
    print(classify_qr(result5))
    print(classify_qr(result6))

    print(decode_corner_qr(result0))
    print(decode_corner_qr(result1))
    print(decode_corner_qr(result2))
    print(decode_corner_qr(result3))
    print(decode_process_qr(result4))
    print(decode_process_qr(result5))
    print(decode_process_qr(result6))