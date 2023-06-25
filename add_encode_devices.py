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
                string = f'{qr_code_type};{len(self.devices)},{self.operator_name},{self.chip_name}'
                strings[qr_code_type].append(string)
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
                string_list = []
                string_len_list = []
                for i in range(len(self.devices)):
                    for j in range(len(self.device_aruco)):
                        string = ""
                        string += f'{qr_code_type};{i},{i+1},'
                        string += f'{j},{j+1},'
                        string += f'{self.devices[i]["device_x_len"]},{self.devices[i]["device_y_len"]},'
                        string += f'{self.device_aruco[i][j]["aruco_x_offset"]},{self.device_aruco[i][j]["aruco_y_offset"]},'
                        string += f'{self.device_aruco[i][j]["aruco_size"]},'
                        string += f'{",".join([i for i in self.devices[i]["folder_count_at_each_depth"]])};'
                        string_list.append(string)
                        string_len_list.append(len(string))

                total_string_len = 0
                string = ""
                for i in range(len(string_len_list)):
                    string_ = string_list[i]
                    total_string_len += string_len_list[i]
                    if i == len(string_len_list)-1: # last element
                        if total_string_len > char_count_limit: # not within char_count_limit, split and append individually
                            strings[qr_code_type].append(string)
                            strings[qr_code_type].append(string_)
                        else: # within char_count_limit
                            strings[qr_code_type].append(string + string_)
                    else: 
                        if total_string_len > char_count_limit:  # not within char_count_limit, split and append the one within limit
                            strings[qr_code_type].append(string)
                            string = string_
                        else:
                            string += string_

            elif qr_code_type == 3:
                for process_count, process in enumerate(self.processes):
                    string = f'{qr_code_type};{process_count},{process["name"]}'
                    strings[qr_code_type].append(string)
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
                string = ""
                for i in range(len(self.devices)):
                    string += f'{qr_code_type};{i},{i+1},'
                    string += f'{",".join([i for i in self.devices[i]["folder_count_at_each_depth"]])};'
                    string_list.append(string)
                    string_len_list.append(len(string))

                total_string_len = 0
                string = ""
                for i in range(len(string_len_list)):
                    string_ = string_list[i]
                    total_string_len += string_len_list[i]
                    if i == len(string_len_list)-1: # last element
                        if total_string_len > char_count_limit: # not within char_count_limit, split and append individually
                            strings[qr_code_type].append(string)
                            strings[qr_code_type].append(string_)
                        else: # within char_count_limit
                            strings[qr_code_type].append(string + string_)
                    else: 
                        if total_string_len > char_count_limit:  # not within char_count_limit, split and append the one within limit
                            strings[qr_code_type].append(string)
                            string = string_
                        else:
                            string += string_
        
        return strings
    
    if __name__ == "__main__":
        string = encode_qr(qr_code_type = 0)