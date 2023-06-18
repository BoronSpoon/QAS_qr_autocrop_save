class AED_Devices():
    def __init__():
        pass
    def encode_qr(
        self,
        qr_code_type = 0,
        **kwargs,
    ):
        string = ""
        if qr_code_type == 0:
            string = f'{qr_code_type};{kwargs["total_device_count"]},{kwargs["operator_name"]},{kwargs["chip_name"]}'
        elif qr_code_type == 1:
            string = f'{qr_code_type};'
            arg_dicts = kwargs["arg_dicts"]
            for i in range(len(arg_dicts)):
                arg_dict = arg_dicts[i]
                string += f'{arg_dict["folder_depth_count"]},{arg_dict["start_index"]},'
                string += f'{",".join([i for i in arg_dict["folder_names"]])};'
        elif qr_code_type == 2:
            string = f'{qr_code_type};'
            arg_dicts = kwargs["arg_dicts"]
            for i in range(len(arg_dicts)):
                arg_dict = arg_dicts[i]
                string += f'{arg_dict["start_device_count"]},{arg_dict["end_device_count"]},{arg_dict["start_aruco_count"]},{arg_dict["end_aruco_count"]},'
                string += f'{arg_dict["device_x_len"]},{arg_dict["device_y_len"]},{arg_dict["aruco_x_offset"]},{arg_dict["aruco_y_offset"]},'
                string += f'{arg_dict["aruco_size"]},'
                string += f'{",".join([i for i in arg_dict["folder_count_at_each_depth"]])};'
        elif qr_code_type == 3:
            string = f'{qr_code_type};{kwargs["process_count"]},{kwargs["process_name"]}'
        elif qr_code_type == 4:
            string = f'{qr_code_type},{kwargs["process_count"]};'
            arg_dicts = kwargs["arg_dicts"]
            for i in range(len(arg_dicts)):
                arg_dict = arg_dicts[i]
                string += f'{arg_dict["folder_depth_count"]},{arg_dict["start_index"]},'
                string += f'{",".join([i for i in arg_dict["folder_names"]])};'
        elif qr_code_type == 5:
            string = f'{qr_code_type},{kwargs["process_count"]};'
            arg_dicts = kwargs["arg_dicts"]
            for i in range(len(arg_dicts)):
                arg_dict = arg_dicts[i]
                string += f'{arg_dict["start_device_count"]},{arg_dict["end_device_count"]},'
                string += f'{",".join([i for i in arg_dict["folder_count_at_each_depth"]])};'
        
        return string

    if __name__ == "__main__":
        string = encode_qr(qr_code_type = 0)