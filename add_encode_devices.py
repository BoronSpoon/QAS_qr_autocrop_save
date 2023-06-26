# format rule
# use range(len(arg)) because arg can be list or dict
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
        self.device_aruco = {}
        self.device_folder_names = {}
        self.process_folder_names = {}
        self.processes = {}
        self.process_names = {}
        for i in range(len(process_names)):
            self.process_names[i] = process_names[i]
        self.device_count = 0
        self.process_count = 0

    def print(self):
        print(f"operator_name = {self.operator_name}")
        print(f"chip_name = {self.chip_name}")
        print(f"devices = {self.devices}")
        print(f"device_aruco = {self.device_aruco}")
        print(f"device_folder_names = {self.device_folder_names}")
        print(f"process_folder_names = {self.process_folder_names}")
        print(f"process_names = {self.process_names}")
        print(f"processes = {self.processes}")

    def add_device(
        self,
        device_folder_names, # list of names of folder from parent to children
        process_folder_names, # list of names of folder from parent to children
        device_x_len, 
        device_y_len, 
        aruco_x_offsets, 
        aruco_y_offsets, 
        aruco_sizes, 
    ):
        if self.device_count not in self.devices.keys():
            self.devices[self.device_count] = {
                "x_len": device_x_len,
                "y_len": device_y_len,
            }

        if self.device_count not in self.device_aruco.keys():
            self.device_aruco[self.device_count] = {}
            for i in range(min(len(aruco_x_offsets), len(aruco_y_offsets), len(aruco_sizes))):
                aruco_x_offset = aruco_x_offsets[i]
                aruco_y_offset = aruco_y_offsets[i]
                aruco_size = aruco_sizes[i]
                self.device_aruco[self.device_count][i] = {
                    "x_offset": aruco_x_offset,
                    "y_offset": aruco_y_offset,
                    "size": aruco_size,
                }

        for folder_depth_count in range(len(device_folder_names)):
            if folder_depth_count not in self.device_folder_names.keys():
                self.device_folder_names[folder_depth_count] = []
            if device_folder_names[folder_depth_count] not in self.device_folder_names[folder_depth_count]:
                self.device_folder_names[folder_depth_count].append(device_folder_names[folder_depth_count])

        self.processes[self.device_count] = {}
        if self.device_count not in self.process_folder_names.keys():
            self.process_folder_names[self.device_count] = {}
        for process_count in range(len(process_folder_names[0])):
            if process_count not in self.process_folder_names[self.device_count].keys():
                self.process_folder_names[self.device_count][process_count] = {}
            for folder_depth_count in range(len(process_folder_names[process_count])):
                folder_name = process_folder_names[self.device_count][process_count][folder_depth_count]
                if folder_depth_count not in self.process_folder_names[process_count].keys():
                    self.process_folder_names[self.device_count][process_count][folder_depth_count] = []
                if folder_name not in self.process_folder_names[process_count][folder_depth_count]:
                    self.process_folder_names[self.device_count][process_count][folder_depth_count].append(folder_name)
                if folder_depth_count == 0:
                    self.processes[self.device_count][process_count] = []
                self.processes[self.device_count][process_count].append(self.process_folder_names[process_count][folder_depth_count].index(folder_name))

        self.device_count += 1 
        
    def encode_qrs(
        self,
        qr_code_type_count = 6,
        char_count_limit = 108,
        **kwargs,
    ):
        self.device_count = len(self.devices)
        self.process_count = len(self.processes)
        strings = {i:[] for i in range(qr_code_type_count)}

        for qr_code_type in range(qr_code_type_count):

            if qr_code_type == 0:
                strings[qr_code_type].append(
                    f'{qr_code_type};{len(self.devices)},{self.operator_name},{self.chip_name};'    
                )

            elif qr_code_type == 1:
                for folder_depth_count in range(len(self.device_folder_names)):
                    folder_names = self.device_folder_names[folder_depth_count]
                    accumulated_string = ""
                    string_header = f'{qr_code_type};{folder_depth_count},{0}'
                    for i in range(len(folder_names)):
                        if i == 0:
                            current_string = f',{folder_names[i]}'
                        else:
                            current_string = f',{folder_names[i]}'
                        if i == len(folder_names)-1: # last element
                            # not within char_count_limit, split and append individually
                            if len(string_header + accumulated_string + current_string) + 1 > char_count_limit: # +1 is for ";"    
                                strings[qr_code_type].append(f"{string_header}{accumulated_string};")
                                string_header = f'{qr_code_type};{folder_depth_count},{i}'
                                strings[qr_code_type].append(f"{string_header}{current_string};")
                            else: # within char_count_limit
                                strings[qr_code_type].append(f"{string_header}{accumulated_string}{current_string};")
                        else:
                            if len(string_header + accumulated_string + current_string) + 1 > char_count_limit: # +1 is for ";"    
                                strings[qr_code_type].append(f"{string_header}{accumulated_string};")
                                string_header = f'{qr_code_type};{folder_depth_count},{i}'
                                accumulated_string = current_string
                            else: # within char_count_limit
                                accumulated_string += current_string

            elif qr_code_type == 2:
                accumulated_string = ""
                string_header = f"{qr_code_type};"
                for i in range(len(self.devices)):
                    for j in range(len(self.device_aruco)):
                        current_string = "".join([
                            f'{i},{i+1},',
                            f'{j},{j+1},',
                            f'{self.devices[i]["x_len"]},{self.devices[i]["y_len"]},',
                            f'{self.device_aruco[i][j]["x_offset"]},{self.device_aruco[i][j]["y_offset"]},',
                            f'{self.device_aruco[i][j]["size"]},',
                            f'{",".join([i for i in self.device_folder_names[i]])};',
                        ])

                    if i == len(self.devices)-1 and j == len(self.device_aruco)-1: # last element
                        if len(string_header + accumulated_string + current_string) > char_count_limit: # not within char_count_limit, split and append individually
                            strings[qr_code_type].append(string_header + accumulated_string)
                            strings[qr_code_type].append(string_header + current_string)
                        else: # within char_count_limit
                            strings[qr_code_type].append(string_header + accumulated_string + current_string)
                    else: 
                        if len(string_header + accumulated_string + current_string) > char_count_limit:  # not within char_count_limit, split and append the one within limit
                            strings[qr_code_type].append(string_header + accumulated_string)
                            accumulated_string = current_string
                        else:
                            accumulated_string += current_string

            elif qr_code_type == 3:
                accumulated_string = ""
                string_header = f"{qr_code_type};"
                for process_count in range(len(self.process_names)):
                    process_name = self.process_names[process_count]
                    current_string = "".join([
                        f'{process_count},{process_name};',
                    ])

                    if process_count == len(self.process_names)-1: # last element
                        if len(string_header + accumulated_string + current_string) > char_count_limit: # not within char_count_limit, split and append individually
                            strings[qr_code_type].append(string_header + accumulated_string)
                            strings[qr_code_type].append(string_header + current_string)
                        else: # within char_count_limit
                            strings[qr_code_type].append(string_header + accumulated_string + current_string)
                    else: 
                        if len(string_header + accumulated_string + current_string) > char_count_limit:  # not within char_count_limit, split and append the one within limit
                            strings[qr_code_type].append(string_header + accumulated_string)
                            accumulated_string = current_string
                        else:
                            accumulated_string += current_string

            elif qr_code_type == 4:
                for device_count in range(len(self.process_folder_names)): # process
                    for process_count in range(len(self.process_folder_names[0])):
                        for folder_depth_count in range(len(self.process_folder_names[0][0])):
                            folder_names = self.process_folder_names[device_count][process_count][folder_depth_count]
                            accumulated_string = ""
                            string_header = f'{qr_code_type},{process_count};{folder_depth_count},{0}'
                            for i in range(len(folder_names)):
                                if i == 0:
                                    current_string = f',{folder_names[i]}'
                                else:
                                    current_string = f',{folder_names[i]}'
                                if i == len(folder_names)-1: # last element
                                    # not within char_count_limit, split and append individually
                                    if len(string_header + accumulated_string + current_string) + 1 > char_count_limit: # +1 is for ";"    
                                        strings[qr_code_type].append(f"{string_header}{accumulated_string};")
                                        string_header = f'{qr_code_type};{folder_depth_count},{i}'
                                        strings[qr_code_type].append(f"{string_header}{current_string};")
                                    else: # within char_count_limit
                                        strings[qr_code_type].append(f"{string_header}{accumulated_string}{current_string};")
                                else:
                                    if len(string_header + accumulated_string + current_string) + 1 > char_count_limit: # +1 is for ";"    
                                        strings[qr_code_type].append(f"{string_header}{accumulated_string};")
                                        string_header = f'{qr_code_type};{folder_depth_count},{i}'
                                        accumulated_string = current_string
                                    else: # within char_count_limit
                                        accumulated_string += current_string

            elif qr_code_type == 5:
                accumulated_string = ""
                for j in range(len(self.devices[0])): # number of processes
                    for i in range(len(self.devices)): # number of devices
                        if i == 0: # create new QR code at new process
                            string_header = f"{qr_code_type},{j};"
                        current_string = "".join([
                            f'{i},{i+1},',
                            f'{",".join([str(i) for i in self.processes[i][j]])};',
                        ])
                        if j == len(self.devices[0])-1 and i == len(self.devices)-1: # last element
                            if len(string_header + accumulated_string + current_string) > char_count_limit: # not within char_count_limit, split and append individually
                                strings[qr_code_type].append(string_header + accumulated_string)
                                strings[qr_code_type].append(string_header + current_string)
                            else: # within char_count_limit
                                strings[qr_code_type].append(string_header + accumulated_string + current_string)
                        else: 
                            if len(string_header + accumulated_string + current_string) > char_count_limit:  # not within char_count_limit, split and append the one within limit
                                strings[qr_code_type].append(string_header + accumulated_string)
                                accumulated_string = current_string
                            else:
                                accumulated_string += current_string
        
        return strings
    
if __name__ == "__main__":
    ed = EncodeDevices(
        operator_name = "Placeholder Operator Name",
        chip_name = "Placeholder Chip Name",
        process_names = ["EB", "MLE"],
    )
    ed.add_device(
        device_folder_names = [
            ["mzi", "coplanar"],
            ["mzi", "coplanar"],
            ["mzi", "coplanar"],
            ["mzi", "coplanar"],
            ["mzi", "single_line"],
            ["mzi", "single_line"],
            ["mzi", "single_line"],
            ["mzi", "single_line"],
        ],
        process_folder_names = [ # [device, process, folder_depth]
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
        device_x_len = 100,
        device_y_len = 10,
        aruco_x_offsets = [0],
        aruco_y_offsets = [0],
        aruco_sizes = [20],
    )
    ed.print()
    strings = ed.encode_qrs()
    print(strings)
    from decode_devices import DecodeDevices
    dd = DecodeDevices()
    for key in strings.keys():
        for string in strings[key]:
            dd.decode_qr(string)
    dd.print()