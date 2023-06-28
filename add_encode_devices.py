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
        self.device_x_lens = {}
        self.device_y_lens = {}
        self.device_aruco_x_offsets = {}
        self.device_aruco_y_offsets = {}
        self.device_aruco_sizes = {}
        self.device_folder_names = []
        self.process_folder_names = []
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
        print(f"device_x_lens = {self.device_x_lens}")
        print(f"device_y_lens = {self.device_y_lens}")
        print(f"device_aruco_x_offsets = {self.device_aruco_x_offsets}")
        print(f"device_aruco_y_offsets = {self.device_aruco_y_offsets}")
        print(f"device_aruco_sizes = {self.device_aruco_sizes}")
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
        self.device_x_lens[self.device_count] = device_x_len
        self.device_y_lens[self.device_count] = device_y_len

        if self.device_count not in self.device_aruco_x_offsets.keys():
            self.device_aruco_x_offsets[self.device_count] = {}
        if self.device_count not in self.device_aruco_y_offsets.keys():
            self.device_aruco_y_offsets[self.device_count] = {}
        if self.device_count not in self.device_aruco_sizes.keys():
            self.device_aruco_sizes[self.device_count] = {}
        for aruco_count in range(min(len(aruco_x_offsets), len(aruco_y_offsets), len(aruco_sizes))):
            self.device_aruco_x_offsets[self.device_count][aruco_count] = aruco_x_offsets[aruco_count]
            self.device_aruco_y_offsets[self.device_count][aruco_count] = aruco_y_offsets[aruco_count]
            self.device_aruco_sizes[self.device_count][aruco_count] = aruco_sizes[aruco_count]

        self.devices[self.device_count] = []
        for folder_depth_count in range(len(device_folder_names)):
            if device_folder_names[folder_depth_count] not in self.device_folder_names:
                self.device_folder_names.append(device_folder_names[folder_depth_count])
            self.devices[self.device_count].append(self.device_folder_names.index(device_folder_names[folder_depth_count]))
            
        self.processes[self.device_count] = {}
        for process_count in range(len(process_folder_names[0])):
            for folder_depth_count in range(len(process_folder_names[process_count])):
                folder_name = process_folder_names[self.device_count][process_count][folder_depth_count]
                if folder_name not in self.process_folder_names:
                    self.process_folder_names.append(folder_name)
                if folder_depth_count == 0:
                    self.processes[self.device_count][process_count] = []
                self.processes[self.device_count][process_count].append(self.process_folder_names.index(folder_name))

        self.device_count += 1 
        
    def encode_qrs(
        self,
        qr_code_type_count = 6,
        char_count_limit = 108,
        **kwargs,
    ):
        self.device_count = len(self.devices)
        self.process_count = len(self.processes)
        self.strings = {i:[] for i in range(qr_code_type_count)}

        for qr_code_type in range(qr_code_type_count):

            if qr_code_type == 0:
                self.strings[qr_code_type].append(
                    f'{qr_code_type};{len(self.devices)},{self.operator_name},{self.chip_name};'    
                )

            elif qr_code_type == 1:
                for folder_depth_count in range(len(self.device_folder_names)):
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
                for device_count in range(len(self.device_x_lens)):
                    for aruco_count in range(len(self.device_aruco_x_offsets)):
                        current_string = "".join([
                            f'{device_count},{device_count+1},',
                            f'{aruco_count},{aruco_count+1},',
                            f'{self.device_x_lens[device_count]},{self.device_y_lens[device_count]},',
                            f'{self.device_aruco_x_offsets[device_count][aruco_count]},{self.device_aruco_y_offsets[device_count][aruco_count]},',
                            f'{self.device_aruco_sizes[device_count][aruco_count]},',
                            f'{",".join([str(i) for i in self.devices])};',
                        ])

                    if device_count == len(self.device_x_lens)-1 and aruco_count == len(self.device_aruco_x_offsets)-1: # last element
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
                accumulated_string = ""
                string_header = f"{qr_code_type};"
                for process_count in range(len(self.process_names)):
                    process_name = self.process_names[process_count]
                    current_string = "".join([
                        f'{process_count},{process_name};',
                    ])

                    if process_count == len(self.process_names)-1: # last element
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

            elif qr_code_type == 4:
                accumulated_string = ""
                string_header = f'{qr_code_type},{process_count};{0}'
                for i in range(len(self.process_folder_names)):
                    current_string = f',{self.process_folder_names[i]}'
                    if i == len(self.process_folder_names)-1: # last element
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

            elif qr_code_type == 5:
                accumulated_string = ""
                for process_count in range(len(self.processes[0])):
                    for device_count in range(len(self.processes)):
                        if device_count == 0: # create new QR code at new process
                            string_header = f"{qr_code_type},{process_count};"
                        current_string = "".join([
                            f'{device_count},{device_count+1},',
                            f'{",".join([str(i) for i in self.processes[device_count][process_count]])};',
                        ])
                        if process_count == len(self.processes[0])-1 and device_count == len(self.processes)-1: # last element
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
        
        return self.strings
    
    def get_combined_qr_bits(
        self, 
    ):
        for qr_code_type, strings in self.strings.items():
            if qr_code_type == 0:
                pass
            elif qr_code_type == 1:
                pass
            elif qr_code_type == 2:
                pass
            elif qr_code_type == 3:
                pass
            elif qr_code_type == 4:
                pass
            elif qr_code_type == 5:
                pass


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