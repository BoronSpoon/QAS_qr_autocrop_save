alphanumeric_count = 45
alphanumeric2numeric_dict = {
    "0": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "A": 10,
    "B": 11,
    "C": 12,
    "D": 13,
    "E": 14,
    "F": 15,
    "G": 16,
    "H": 17,
    "I": 18,
    "J": 19,
    "K": 20,
    "L": 21,
    "M": 22,
    "N": 23,
    "O": 24,
    "P": 25,
    "Q": 26,
    "R": 27,
    "S": 28,
    "T": 29,
    "U": 30,
    "V": 31,
    "W": 32,
    "X": 33,
    "Y": 34,
    "Z": 35,
    " ": 36,
    "$": 37,
    "%": 38,
    "*": 39,
    "+": 40,
    "-": 41,
    ".": 42,
    "/": 43,
    ":": 44,
}

def alphanumeric2numeric(string):
    total = 0
    for count, char in enumerate(string):
        total += (alphanumeric_count**count)*alphanumeric2numeric_dict[char]
    return total

def alphanumeric2binary(string):
    total = 0
    for count, char in enumerate(string):
        total += (alphanumeric_count**count)*alphanumeric2numeric_dict[char]
    return bin(total)[2:] # remove "0b"

def classify_qr(string):
    # bit 0~1:
    # 0 (indicates corner QR)
    # 1 (indicates process QR)
    bit0 = alphanumeric2binary(string[0])[-1]
    if bit0 == "0":
        return "corner_QR"
    elif bit0 == "1":
        return "process_QR"
    else:
        return None

def decode_corner_qr(string):
    # total 47 alphanumeric letters

    # position (16 bits)
    # alphanumeric*1 (bit 0: 0, indicates corner QR)
    bits = alphanumeric2binary(string[0])
    assert bits[-1] == "0"
    # x position: alphanumeric*2
    x_pos = alphanumeric2numeric(string[1:3])
    # y position: alphanumeric*2
    y_pos = alphanumeric2numeric(string[3:5])
    # device_width (in multiple of marker gap): alphanumeric*2
    device_width = alphanumeric2numeric(string[5:7])
    # device_gap (in multiple of marker gap): alphanumeric*2
    device_height = alphanumeric2numeric(string[7:9])
    # marker size (6 numbers: 1.0422e-6->104226)
    # alphanumeric*4
    numerics = alphanumeric2numeric(string[9:13])
    numerics = str(numerics)
    marker_size = float(f"{numerics[0]}.{numerics[1:5]}e-{numerics[5]}")
    # marker gap (6 numbers: 1.0422e-6->104226)
    # alphanumeric*4
    numerics = alphanumeric2numeric(string[13:17])
    numerics = str(numerics)
    marker_gap = float(f"{numerics[0]}.{numerics[1:5]}e-{numerics[5]}")
    # count (2*4 numbers: x,y,i,j)
    # alphanumeric*6
    cx = alphanumeric2numeric(string[17:19])
    cy = alphanumeric2numeric(string[19:21])
    ci = alphanumeric2numeric(string[21:23])
    cj = alphanumeric2numeric(string[23:25])
    # operator name (8 letters: yamada)
    # alphanumeric*8
    operator_name = string[25:33].rstrip()
    # sample name (14 letters: TY_test_condition)
    # alphanumeric*14
    sample_name = string[33:46].rstrip()
    return x_pos, y_pos, device_width, device_height, marker_size, marker_gap, cx, cy, ci, cj, operator_name, sample_name

def decode_process_qr(string):
    # total 29 alphanumeric letters

    # indication of process QR (2 bit: 1)
    # alphanumeric*1
    bits = alphanumeric2binary(string[0])
    assert bits[-1] == "1"
    # process count (3 numbers: 001)
    # alphanumeric*2
    process_count = alphanumeric2numeric(string[1:3])
    # process name (26 letters: TY_test_condition)
    # alphanumeric*26
    process_name = string[3:28].rstrip()
    return process_count, process_name