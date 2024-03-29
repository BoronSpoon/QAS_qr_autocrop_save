# format rule
# use range(len(arg)) because arg can be list or dict
from draw_qrcode import *
from draw_aruco import *
import numpy as np
import cv2
from pprint import pprint

class EncodeDevices():
    def __init__(
            self,
            operator_name = "Placeholder Operator Name",
            chip_name = "Placeholder Chip Name",
            process_names = [],
        ):
        self.operator_name = operator_name
        self.chip_name = chip_name
        self.devices = {}
        self.device_x_mins = {}
        self.device_y_mins = {}
        self.device_x_lens = {}
        self.device_y_lens = {}
        self.device_aruco_x_offsets = {}
        self.device_aruco_y_offsets = {}
        self.device_aruco_sizes = {}
        self.device_folder_names = []
        self.process_folder_names = {}
        self.processes = {}
        self.process_names = {}
        for i in range(len(process_names)):
            self.process_names[i] = process_names[i]
        self.device_count = 0
        self.process_count = 0
        self.whitespace = 3
        
    def print(self):
        print(f"operator_name = {self.operator_name}")
        print(f"chip_name = {self.chip_name}")
        print(f"devices = ")
        pprint(self.devices)
        #print(f"device_folder_names = {self.device_folder_names}")
        print(f"device_x_mins = {self.device_x_mins}")
        print(f"device_y_mins = {self.device_y_mins}")
        print(f"device_x_lens = {self.device_x_lens}")
        print(f"device_y_lens = {self.device_y_lens}")
        print(f"device_aruco_x_offsets = ")
        pprint(self.device_aruco_x_offsets)
        print(f"device_aruco_y_offsets = ")
        pprint(self.device_aruco_y_offsets)
        print(f"device_aruco_sizes = {self.device_aruco_sizes}")
        #print(f"process_folder_names = {self.process_folder_names}")
        print(f"process_names = {self.process_names}")
        print(f"processes = ")
        pprint(self.processes)

    def add_device(
        self,
        device_folder_names, # list of names of folder from parent to children
        process_folder_names, # list of names of folder from parent to children
        device_x_min,
        device_y_min,
        device_x_len, 
        device_y_len, 
        aruco_x_offsets, 
        aruco_y_offsets, 
        aruco_size, 
    ):
        self.device_x_mins[self.device_count] = device_x_min
        self.device_y_mins[self.device_count] = device_y_min
        self.device_x_lens[self.device_count] = device_x_len
        self.device_y_lens[self.device_count] = device_y_len

        if self.device_count not in self.device_aruco_x_offsets.keys():
            self.device_aruco_x_offsets[self.device_count] = {}
        if self.device_count not in self.device_aruco_y_offsets.keys():
            self.device_aruco_y_offsets[self.device_count] = {}
        for aruco_count in range(min(len(aruco_x_offsets), len(aruco_y_offsets))):
            self.device_aruco_x_offsets[self.device_count][aruco_count] = aruco_x_offsets[aruco_count]
            self.device_aruco_y_offsets[self.device_count][aruco_count] = aruco_y_offsets[aruco_count]
            self.device_aruco_sizes[self.device_count] = aruco_size # same size for all aruco_count in device

        self.devices[self.device_count] = []
        for folder_depth_count in range(len(device_folder_names)):
            device_folder_name = device_folder_names[folder_depth_count]
            if device_folder_name not in self.device_folder_names:
                self.device_folder_names.append(device_folder_name)
            self.devices[self.device_count].append(self.device_folder_names.index(device_folder_name))
            
        self.processes[self.device_count] = {}
        for process_count in range(len(process_folder_names)):
            if process_count not in self.process_folder_names.keys():
                self.process_folder_names[process_count] = []
            for folder_depth_count in range(len(process_folder_names[0])):
                folder_name = process_folder_names[process_count][folder_depth_count]
                if folder_name not in self.process_folder_names[process_count]:
                    self.process_folder_names[process_count].append(folder_name)
                if folder_depth_count == 0:
                    self.processes[self.device_count][process_count] = []
                self.processes[self.device_count][process_count].append(self.process_folder_names[process_count].index(folder_name))

        self.device_count += 1
        
    def add_device_4_corners( # add_device with (used for default configuration)
        self,
        device_folder_names, # list of names of folder from parent to children
        process_folder_names, # list of names of folder from parent to children
        device_x_min,
        device_y_min,
        device_x_len, 
        device_y_len, 
        aruco_size=10, # 10um default aruco size
    ):
        aruco_x_offsets=[
            [device_x_min - 6*aruco_size], # bottom left  (-x, -y)
            [device_x_min + device_x_len], # bottom right (x,  -y)
            [device_x_min - 6*aruco_size], # top left     (-x, y)
            [device_x_min + device_x_len], # top right    (x,  y)
        ]
        aruco_y_offsets=[
            [device_y_min - 6*aruco_size], # bottom left  (-x, -y)
            [device_y_min - 6*aruco_size], # bottom right (x,  -y)
            [device_y_min + device_y_len], # top left     (-x, y)
            [device_y_min + device_y_len], # top right    (x,  y)
        ]
        self.add_device( # add_device with aruco at 4 corners (used for default configuration)
            device_folder_names, # list of names of folder from parent to children
            process_folder_names, # list of names of folder from parent to children
            device_x_min,
            device_y_min,
            device_x_len, 
            device_y_len, 
            aruco_x_offsets=aruco_x_offsets, 
            aruco_y_offsets=aruco_y_offsets,
            aruco_size=aruco_size,
        )
        return {
            "device_count": self.device_count - 1,
            "aruco_x_offsets": aruco_x_offsets,
            "aruco_y_offsets": aruco_y_offsets,
            "aruco_size": aruco_size,
        }
        
    def add_device_2_corners( # add_device with (used for default configuration)
        self,
        device_folder_names, # list of names of folder from parent to children
        process_folder_names, # list of names of folder from parent to children
        device_x_min,
        device_y_min,
        device_x_len, 
        device_y_len, 
        aruco_size=10, # 10um default aruco size
    ):
        aruco_x_offsets=[
            [device_x_min - 6*aruco_size], # bottom left  (-x, -y)
            [device_x_min + device_x_len], # top right    (x,  y)
        ]
        aruco_y_offsets=[
            [device_y_min - 6*aruco_size], # bottom left  (-x, -y)
            [device_y_min + device_y_len], # top right    (x,  y)
        ]
        self.add_device( # add_device with aruco at 4 corners (used for default configuration)
            device_folder_names, # list of names of folder from parent to children
            process_folder_names, # list of names of folder from parent to children
            device_x_min,
            device_y_min,
            device_x_len, 
            device_y_len, 
            aruco_x_offsets=aruco_x_offsets,
            aruco_y_offsets=aruco_y_offsets,
            aruco_size=aruco_size,
        )
        return {
            "device_count": self.device_count - 1,
            "aruco_x_offsets": aruco_x_offsets,
            "aruco_y_offsets": aruco_y_offsets,
            "aruco_size": aruco_size,
        }

    def encode_qrs(
        self,
        qr_code_type_count = 6,
        char_count_limit = 108,
        **kwargs,
    ):
        self.device_len = len(self.devices)
        self.process_len = len(self.process_names)
        self.strings = {}
        for i in [0,1,2]:
            self.strings[i] = []
        for i in [3,4,5]:
            self.strings[i] = {j: [] for j in range(self.process_len)}

        for qr_code_type in range(qr_code_type_count):

            if qr_code_type == 0:
                self.strings[qr_code_type].append(
                    f'{qr_code_type};{len(self.devices)},{self.operator_name},{self.chip_name};'    
                )

            elif qr_code_type == 1:
                accumulated_string = ""
                string_header = f'{qr_code_type};{0}'
                for i in range(len(self.device_folder_names)):
                    if i == 0:
                        current_string = f',{self.device_folder_names[i]}'
                    else:
                        current_string = f',{self.device_folder_names[i]}'
                    if i == len(self.device_folder_names)-1: # last element
                        # not within char_count_limit, split and append individually
                        if len(string_header + accumulated_string + current_string) + 1 > char_count_limit: # +1 is for ";"    
                            self.strings[qr_code_type].append(f"{string_header}{accumulated_string};")
                            string_header = f'{qr_code_type};{i}'
                            self.strings[qr_code_type].append(f"{string_header}{current_string};")
                        else: # within char_count_limit
                            self.strings[qr_code_type].append(f"{string_header}{accumulated_string}{current_string};")
                    else:
                        if len(string_header + accumulated_string + current_string) + 1 > char_count_limit: # +1 is for ";"    
                            self.strings[qr_code_type].append(f"{string_header}{accumulated_string};")
                            string_header = f'{qr_code_type};{i}'
                            accumulated_string = current_string
                        else: # within char_count_limit
                            accumulated_string += current_string

            elif qr_code_type == 2:
                accumulated_string = ""
                string_header = f"{qr_code_type};"
                for device_count in range(self.device_len):
                    for aruco_count in range(len(self.device_aruco_x_offsets[device_count])):
                        current_string = "".join([
                            f'{device_count},{device_count+1},',
                            f'{aruco_count},{aruco_count+1},',
                            f'{self.device_x_mins[device_count]},{self.device_y_mins[device_count]},',
                            f'{self.device_x_lens[device_count]},{self.device_y_lens[device_count]},',
                            f'{self.device_aruco_x_offsets[device_count][aruco_count]},{self.device_aruco_y_offsets[device_count][aruco_count]},',
                            f'{self.device_aruco_sizes[device_count]},',
                            f'{",".join([str(i) for i in self.devices[device_count]])};',
                        ])

                    if device_count == self.device_len-1 and aruco_count == len(self.device_aruco_x_offsets[0])-1: # last element
                        if len(string_header + accumulated_string + current_string) > char_count_limit: # not within char_count_limit, split and append individually
                            self.strings[qr_code_type].append(string_header + accumulated_string)
                            self.strings[qr_code_type].append(string_header + current_string)
                        else: # within char_count_limit
                            self.strings[qr_code_type].append(string_header + accumulated_string + current_string)
                    else: 
                        if len(string_header + accumulated_string + current_string) > char_count_limit:  # not within char_count_limit, split and append the one within limit
                            self.strings[qr_code_type].append(string_header + accumulated_string)
                            accumulated_string = current_string
                        else:
                            accumulated_string += current_string

            elif qr_code_type == 3:
                for process_count in range(self.process_len):
                    process_name = self.process_names[process_count]
                    string_header = f"{qr_code_type},{process_count};"
                    current_string = f'{process_name};'
                    self.strings[qr_code_type][process_count].append(string_header + current_string)

            elif qr_code_type == 4:
                accumulated_string = ""
                for process_count in range(self.process_len):
                    string_header = f'{qr_code_type},{process_count};{0}'
                    for i in range(len(self.process_folder_names[0])):
                        current_string = f',{self.process_folder_names[process_count][i]}'
                        if i == len(self.process_folder_names[process_count])-1: # last element
                            # not within char_count_limit, split and append individually
                            if len(string_header + accumulated_string + current_string) + 1 > char_count_limit: # +1 is for ";"    
                                self.strings[qr_code_type][process_count].append(f"{string_header}{accumulated_string};")
                                string_header = f'{qr_code_type};{i}'
                                self.strings[qr_code_type][process_count].append(f"{string_header}{current_string};")
                            else: # within char_count_limit
                                self.strings[qr_code_type][process_count].append(f"{string_header}{accumulated_string}{current_string};")
                        else:
                            if len(string_header + accumulated_string + current_string) + 1 > char_count_limit: # +1 is for ";"    
                                self.strings[qr_code_type][process_count].append(f"{string_header}{accumulated_string};")
                                string_header = f'{qr_code_type};{i}'
                                accumulated_string = current_string
                            else: # within char_count_limit
                                accumulated_string += current_string

            elif qr_code_type == 5:
                accumulated_string = ""
                for process_count in range(self.process_len):
                    for device_count in range(self.device_len):
                        if device_count == 0: # create new QR code at new process
                            string_header = f"{qr_code_type},{process_count};"
                        current_string = "".join([
                            f'{device_count},{device_count+1},',
                            f'{",".join([str(i) for i in self.processes[device_count][process_count]])};',
                        ])
                        if device_count == self.device_len-1: # last element
                            if len(string_header + accumulated_string + current_string) > char_count_limit: # not within char_count_limit, split and append individually
                                self.strings[qr_code_type][process_count].append(string_header + accumulated_string)
                                self.strings[qr_code_type][process_count].append(string_header + current_string)
                            else: # within char_count_limit
                                self.strings[qr_code_type][process_count].append(string_header + accumulated_string + current_string)
                        else: 
                            if len(string_header + accumulated_string + current_string) > char_count_limit:  # not within char_count_limit, split and append the one within limit
                                self.strings[qr_code_type][process_count].append(string_header + accumulated_string)
                                accumulated_string = current_string
                            else:
                                accumulated_string += current_string   
        
        return self.strings
    
    def get_combined_qr_bits(
        self, 
    ):
        col_counts = []
        # find out the max column, rows
        
        col_counts.append(len(self.strings[0]) + len(self.strings[1]) + len(self.strings[2])) # for qr_code_type in [0,1,2] 
        for process_count in range(self.process_count):
            col_counts.append(len(self.strings[3][process_count]) + len(self.strings[4][process_count]) + len(self.strings[5][process_count]))
        
        row_len = 1 + self.process_len
        col_len = max(col_counts)

        single_qr_code_size = len(get_qrcode_pixels()) # get single qr code bits len 
        self.data = np.zeros(( # get (row,col) tiles qr code bits len
            single_qr_code_size*row_len + self.whitespace*(row_len-1),
            single_qr_code_size*col_len + self.whitespace*(col_len-1),
        ), dtype=np.uint8)

        row_count = 0
        col_count = 0
        for qr_code_type in [0,1,2]:
            for string in self.strings[qr_code_type]:
                self.data[
                    (single_qr_code_size+self.whitespace)*row_count: (single_qr_code_size+self.whitespace)*row_count + single_qr_code_size,
                    (single_qr_code_size+self.whitespace)*col_count: (single_qr_code_size+self.whitespace)*col_count + single_qr_code_size,
                ] = get_qrcode_pixels(string)
                col_count += 1
            
        for process_count in range(self.process_len):
            row_count = process_count + 1
            col_count = 0
            for qr_code_type in [3,4,5]:
                for string in self.strings[qr_code_type][process_count]:
                    self.data[
                        (single_qr_code_size+self.whitespace)*row_count: (single_qr_code_size+self.whitespace)*row_count + single_qr_code_size,
                        (single_qr_code_size+self.whitespace)*col_count: (single_qr_code_size+self.whitespace)*col_count + single_qr_code_size,
                    ] = get_qrcode_pixels(string)
                col_count += 1
        return self.data

if __name__ == "__main__":
    encoder = EncodeDevices(
        operator_name = "Placeholder Operator Name",
        chip_name = "Placeholder Chip Name",
        process_names = ["EB", "MLE"],
    )
    for device_folder_names, process_folder_names in zip(
        [ # [device, folder_depth]
            ["mzi", "coplanar"],
            ["mzi", "coplanar"],
            ["mzi", "coplanar"],
            ["mzi", "coplanar"],
            ["mzi", "single_line"],
            ["mzi", "single_line"],
            ["mzi", "single_line"],
            ["mzi", "single_line"],
        ], [ # [device, process, folder_depth]
            [
                ["100uC/cm^2", "mzi", "1mm"],
                ["25%", "gap (um)", "2"], 
            ], [
                ["110uC/cm^2", "mzi", "1mm"],
                ["25%", "gap (um)", "2"], 
            ], [
                ["120uC/cm^2", "mzi", "1mm"],
                ["25%", "gap (um)", "1"], 
            ], [
                ["130uC/cm^2", "mzi", "1mm"],
                ["25%", "gap (um)", "1"], 
            ], [
                ["100uC/cm^2", "mzi", "0.5mm"],
                ["25%", "width (um)", "1"], 
            ], [
                ["110uC/cm^2", "mzi", "0.5mm"],
                ["25%", "width (um)", "2"], 
            ], [
                ["120uC/cm^2", "mzi", "0.5mm"],
                ["25%", "width (um)", "4"], 
            ], [
                ["130uC/cm^2", "mzi", "0.5mm"],
                ["25%", "width (um)", "8"], 
            ],
        ],
    ):
        encoder.add_device(
            device_folder_names = device_folder_names,
            process_folder_names = process_folder_names,
            device_x_min = 0,
            device_y_min = 0,
            device_x_len = 100,
            device_y_len = 10,
            aruco_x_offsets = [0],
            aruco_y_offsets = [0],
            aruco_size = 20,
        )
    #encoder.print()
    strings = encoder.encode_qrs()
    #print(strings)
    data = encoder.get_combined_qr_bits()
    cv2.imshow("frame", draw_qrcode_cv2(px_size=3, data=data))
    while(True):
        if cv2.waitKey(0) & 0xFF == ord('q'):
            break
    from decode_devices import DecodeDevices
    decoder = DecodeDevices()
    decoder.decode_qrs(strings)

    decoder.print()