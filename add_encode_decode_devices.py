class AED_Devices():
    def __init__():
        pass
    def encode_qrs(
        self,
    ):
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
    
    def decode_qrs(
        self,
    ):
        pass
    def decode_qr(
        self,
        string, 
    ):
        arg_dicts = string.split(";")
        qr_code_type = int(arg_dicts[0])
        arg_dict = arg_dicts[1]
        args = arg_dict.split(",")
        if qr_code_type == 0:
            self.total_device_count = int(args[0])
            self.operator_name      =     args[1]
            self.chip_name          =     args[2]
        elif qr_code_type == 1:
            for i, arg_dict in enumerate(arg_dicts[1:]):
                args = arg_dict.split(",")
                folder_depth_count = int(args[0])
                start_index        = int(args[1])
                folder_names       =     args[2:]
                self.device_folder_names[folder_depth_count][start_index:start_index+len(folder_names)] = folder_names
        elif qr_code_type == 2:
            for i, arg_dict in enumerate(arg_dicts[1:]):
                args = arg_dict.split(",")
                start_device_count         = int(args[0])
                end_device_count           = int(args[1])
                start_aruco_count          = int(args[2])
                end_aruco_count            = int(args[3])
                device_x_len               = int(args[4])
                device_y_len               = int(args[5])
                aruco_x_offset             = int(args[6])
                aruco_y_offset             = int(args[7])
                aruco_size                 = int(args[8])
                folder_count_at_each_depth =     args[9:]
                self.device_x_len[start_device_count:end_device_count][start_aruco_count:end_aruco_count]   = device_x_len
                self.device_y_len[start_device_count:end_device_count][start_aruco_count:end_aruco_count]   = device_y_len
                self.aruco_x_offset[start_device_count:end_device_count][start_aruco_count:end_aruco_count] = aruco_x_offset
                self.aruco_y_offset[start_device_count:end_device_count][start_aruco_count:end_aruco_count] = aruco_y_offset
                self.aruco_size[start_device_count:end_device_count][start_aruco_count:end_aruco_count]     = aruco_size
                self.device_folder[start_device_count:end_device_count][start_aruco_count:end_aruco_count]  = [self.device_folder_names[i][folder_count] for (i, folder_count) in enumerate(folder_count_at_each_depth)]
        elif qr_code_type == 3:
            self.process_count = int(arg_dicts[1])
            self.process_name  =     arg_dicts[2]
        elif qr_code_type == 4:
            for i, arg_dict in enumerate(arg_dicts[1:]):
                args = arg_dict.split(",")
                folder_depth_count = int(args[0])
                start_index        = int(args[1])
                folder_names       =     args[2:]
                self.process_folder_names[folder_depth_count][start_index:start_index+len(folder_names)] = folder_names
        elif qr_code_type == 5:
            for i, arg_dict in enumerate(arg_dicts[1:]):
                args = arg_dict.split(",")
                start_device_count         = int(args[0])
                end_device_count           = int(args[1])
                folder_count_at_each_depth =     args[2:]
                self.process_folder_names[start_device_count:end_device_count] = [self.process_folder_names[i][folder_count] for (i, folder_count) in enumerate(folder_count_at_each_depth)]
        
        return string

    if __name__ == "__main__":
        string = encode_qr(qr_code_type = 0)