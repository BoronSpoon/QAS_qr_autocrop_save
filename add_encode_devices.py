class AED_Devices():
    def __init__():
        pass
    def add_device(
        self,
    ):
        pass
    def add_process(
        self,
    ):
        pass
    def encode_qr(
        self,
        qr_code_type_count = 6,
        char_count_limit = 108,
        **kwargs,
    ):
        strings = {i:[] for i in range(qr_code_type_count)}
        string = ""
        for qr_code_type in range(qr_code_type_count):
            if qr_code_type == 0:
                strings[qr_code_type].append(
                    f'{qr_code_type};{len(self.devices)},{self.operator_name},{self.chip_name}'    
                )

            elif qr_code_type == 1:
                for folder_depth_count, folder_names in self.device_folder_names.keys():
                    i = 0
                    string = ""
                    while (i < len(folder_names)):
                        if string == "":
                            string = f'{qr_code_type};{folder_depth_count},{i}'
                        string_ = f',{folder_names[i]}'
                        if len(string + string_ + 1) > char_count_limit: # +1 is for ";"
                            strings[qr_code_type].append(f"{string};")
                            string = ""
                            continue
                        else:
                            string += string_
                            i += 1

            elif qr_code_type == 2:
                i = 0
                j = 0
                accumulated_string_len = 0
                accumulated_string = ""
                string_header = f"{qr_code_type};"
                string_header_len = len(string_header)
                for i in range(len(self.devices)):
                    for j in range(len(self.device_aruco)):
                        current_string = "".join([
                            f'{i},{i+1},',
                            f'{j},{j+1},',
                            f'{self.devices[i]["device_x_len"]},{self.devices[i]["device_y_len"]},',
                            f'{self.device_aruco[i][j]["aruco_x_offset"]},{self.device_aruco[i][j]["aruco_y_offset"]},',
                            f'{self.device_aruco[i][j]["aruco_size"]},',
                            f'{",".join([i for i in self.devices[i]["folder_count_at_each_depth"]])};',
                        ])
                        current_string_len = len(current_string)

                    if i == len(self.devices)-1 and j == len(self.device_aruco)-1: # last element
                        if accumulated_string_len + current_string_len > char_count_limit: # not within char_count_limit, split and append individually
                            strings[qr_code_type].append(string_header + accumulated_string)
                            strings[qr_code_type].append(string_header + current_string)
                        else: # within char_count_limit
                            strings[qr_code_type].append(string_header + accumulated_string + current_string)
                    else: 
                        if accumulated_string_len + current_string_len > char_count_limit:  # not within char_count_limit, split and append the one within limit
                            strings[qr_code_type].append(string_header + accumulated_string)
                            accumulated_string_len = current_string_len
                            accumulated_string = current_string
                        else:
                            accumulated_string_len += current_string_len
                            accumulated_string += current_string

            elif qr_code_type == 3:
                for process_count, process in enumerate(self.processes):
                    strings[qr_code_type].append(
                        f'{qr_code_type};{process_count},{process["name"]}'
                    )

            elif qr_code_type == 4:
                i = 0
                string = ""
                for folder_depth_count, folder_names in self.process_folder_names.keys():
                    while (i < len(folder_names)):
                        if string == "":
                            string = f'{qr_code_type};{folder_depth_count},{i},'
                        string_ = f',{folder_names[i]}'

                        if len(string + string_) + 1 > char_count_limit:
                            strings[qr_code_type].append(f"{string};")
                            string = ""
                            continue
                        else:
                            string += string_
                            i += 1

            elif qr_code_type == 5:
                i = 0                
                accumulated_string_len = 0
                accumulated_string = ""
                for j in range(len(self.devices[0])): # number of processes
                    for i in range(len(self.devices)): # number of devices
                        if i == 0: # create new QR code at new process
                            string_header = f"{qr_code_type},{j};"
                            string_header_len = len(string_header)
                        else:
                            current_string = "".join([
                                f'{i},{i+1},',
                                f'{",".join([i for i in self.processes[i][j]["folder_count_at_each_depth"]])};',
                            ])
                            current_string_len = len(current_string)
                        if j == len(self.devices[0])-1 and i == len(self.devices)-1: # last element
                            if string_header_len + accumulated_string_len + current_string_len > char_count_limit: # not within char_count_limit, split and append individually
                                strings[qr_code_type].append(string_header + accumulated_string)
                                strings[qr_code_type].append(string_header + current_string)
                            else: # within char_count_limit
                                strings[qr_code_type].append(string_header + accumulated_string + current_string)
                        else: 
                            if string_header_len + accumulated_string_len + current_string_len > char_count_limit:  # not within char_count_limit, split and append the one within limit
                                strings[qr_code_type].append(string_header + accumulated_string)
                                accumulated_string_len = current_string_len
                                accumulated_string = current_string
                            else:
                                accumulated_string_len += current_string
                                accumulated_string += current_string
        
        return strings
    
    if __name__ == "__main__":
        strings = encode_qr(qr_code_type = 0)