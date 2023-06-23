class AED_Devices():
    def __init__():
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
                string = f'{qr_code_type};{kwargs["total_device_count"]},{kwargs["operator_name"]},{kwargs["chip_name"]}'
                strings[qr_code_type].append(string)
            elif qr_code_type == 1:
                i = 0
                string = ""
                arg_dicts = kwargs["arg_dicts"]
                while (i < len(arg_dicts)):
                    if string == "":
                        string = f'{qr_code_type};'
                    arg_dict = arg_dicts[i]
                    string_ = ""
                    string_ += f'{arg_dict["folder_depth_count"]},{arg_dict["start_index"]},'
                    string_ += f'{",".join([i for i in arg_dict["folder_names"]])};'
                    if len(string + string_) > char_count_limit:
                        strings[qr_code_type].append(string)
                        string = ""
                        continue
                    else:
                        string += string
                        i += 1
            elif qr_code_type == 2:
                i = 0
                string = ""
                arg_dicts = kwargs["arg_dicts"]
                while (i < len(arg_dicts)):
                    if string == "":
                        string = f'{qr_code_type};'
                    arg_dict = arg_dicts[i]
                    string_ = ""
                    string_ += f'{arg_dict["start_device_count"]},{arg_dict["end_device_count"]},{arg_dict["start_aruco_count"]},{arg_dict["end_aruco_count"]},'
                    string_ += f'{arg_dict["device_x_len"]},{arg_dict["device_y_len"]},{arg_dict["aruco_x_offset"]},{arg_dict["aruco_y_offset"]},'
                    string_ += f'{arg_dict["aruco_size"]},'
                    string_ += f'{",".join([i for i in arg_dict["folder_count_at_each_depth"]])};'
                    
                    if len(string + string_) > char_count_limit:
                        strings[qr_code_type].append(string)
                        string = ""
                        continue
                    else:
                        string += string
                        i += 1
            elif qr_code_type == 3:
                string = f'{qr_code_type};{kwargs["process_count"]},{kwargs["process_name"]}'
                strings[qr_code_type].append(string)
            elif qr_code_type == 4:
                i = 0
                string = ""
                arg_dicts = kwargs["arg_dicts"]
                while (i < len(arg_dicts)):
                    if string == "":
                        string = f'{qr_code_type};'
                    arg_dict = arg_dicts[i]
                    string_ = ""
                    string_ += f'{arg_dict["folder_depth_count"]},{arg_dict["start_index"]},'
                    string_ += f'{",".join([i for i in arg_dict["folder_names"]])};'

                    if len(string + string_) > char_count_limit:
                        strings[qr_code_type].append(string)
                        string = ""
                        continue
                    else:
                        string += string
                        i += 1
            elif qr_code_type == 5:
                i = 0
                string = ""
                arg_dicts = kwargs["arg_dicts"]
                while (i < len(arg_dicts)):
                    if string == "":
                        string = f'{qr_code_type};'
                    arg_dict = arg_dicts[i]
                    string_ = ""
                    string_ += f'{arg_dict["start_device_count"]},{arg_dict["end_device_count"]},'
                    string_ += f'{",".join([i for i in arg_dict["folder_count_at_each_depth"]])};'

                    if len(string + string_) > char_count_limit:
                        strings[qr_code_type].append(string)
                        string = ""
                        continue
                    else:
                        string += string
                        i += 1
        
        return strings
    
    if __name__ == "__main__":
        string = encode_qr(qr_code_type = 0)