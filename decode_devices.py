from pprint import pprint

class DecodeDevices():
    def __init__(self, ):
        self.operator_name = "Placeholder Operator Name",
        self.chip_name = "Placeholder Chip Name"
        self.devices = {}
        self.device_x_mins = {}
        self.device_y_mins = {}
        self.device_x_lens = {}
        self.device_y_lens = {}
        self.device_aruco_x_offsets = {}
        self.device_aruco_y_offsets = {}
        self.device_aruco_sizes = {}
        self.device_folder_names = {}
        self.process_folder_names = {}
        self.processes = {}
        self.process_names = {}
        self.device_count = 0
        self.process_count = 0
        
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

    def decode_qrs(
            self, 
            strings,
        ):
        for key0 in strings.keys():
            if key0 in [0,1,2]:
                for string in strings[key0]:
                    self.decode_qr(string)
            else:
                for key1 in strings[key0].keys():
                    for string in strings[key0][key1]:
                        self.decode_qr(string)

    def decode_qr(
        self,
        string,
    ):
        arg_dicts = string.split(";")
        qr_code_type = int(arg_dicts[0].split(",")[0])

        if qr_code_type == 0:
            args = arg_dicts[1].split(",")
            self.total_device_count = int(args[0])
            self.operator_name      =     args[1]
            self.chip_name          =     args[2]
        elif qr_code_type == 1:
            for i, arg_dict in enumerate(arg_dicts[1:]):
                if arg_dict != "":
                    args = arg_dict.split(",")
                    start_index        = int(args[0])
                    folder_names       =     args[1:]
                    for index in range(len(folder_names)):
                        self.device_folder_names[start_index + index] = folder_names[index]

        elif qr_code_type == 2:
            for i, arg_dict in enumerate(arg_dicts[1:]):
                if arg_dict != "":
                    args = arg_dict.split(",")
                    start_device_count         = int(args[0])
                    end_device_count           = int(args[1])
                    start_aruco_count          = int(args[2])
                    end_aruco_count            = int(args[3])
                    device_x_min               = int(args[4])
                    device_y_min               = int(args[5])
                    device_x_len               = int(args[6])
                    device_y_len               = int(args[7])
                    aruco_x_offset             = int(args[8])
                    aruco_y_offset             = int(args[9])
                    aruco_size                 = int(args[10])
                    folder_count_at_each_depth =     args[11:]
                    for device_count in range(start_device_count,end_device_count):
                        self.device_x_mins[device_count] = device_x_min
                        self.device_y_mins[device_count] = device_y_min
                        self.device_x_lens[device_count] = device_x_len
                        self.device_y_lens[device_count] = device_y_len
                        self.devices[device_count] = [self.device_folder_names[int(folder_count)] for folder_count in folder_count_at_each_depth]
                        self.device_aruco_x_offsets[device_count] = {}
                        self.device_aruco_y_offsets[device_count] = {}
                        for aruco_count in range(start_aruco_count,end_aruco_count):
                            self.device_aruco_x_offsets[device_count][aruco_count] = aruco_x_offset
                            self.device_aruco_y_offsets[device_count][aruco_count] = aruco_y_offset
                            self.device_aruco_sizes[device_count] = aruco_size
                    
        elif qr_code_type == 3:
            process_count = int(arg_dicts[0].split(",")[1])
            for i, arg_dict in enumerate(arg_dicts[1:]):
                if arg_dict != "":
                    args = arg_dict.split(",")
                    process_name = args[0]
                    self.process_names[process_count] = process_name

        elif qr_code_type == 4:
            process_count = int(arg_dicts[0].split(",")[1])
            if process_count not in self.process_folder_names.keys():
                self.process_folder_names[process_count] = {}
            for i, arg_dict in enumerate(arg_dicts[1:]):
                if arg_dict != "":
                    args = arg_dict.split(",")
                    start_index        = int(args[0])
                    folder_names       =     args[1:]
                    for index in range(len(folder_names)):
                        self.process_folder_names[process_count][start_index + index] = folder_names[index]

        elif qr_code_type == 5:
            print(arg_dicts)
            process_count = int(arg_dicts[0].split(",")[1])
            for i, arg_dict in enumerate(arg_dicts[1:]):
                if arg_dict != "":
                    args = arg_dict.split(",")
                    start_device_count         = int(args[0])
                    end_device_count           = int(args[1])
                    folder_count_at_each_depth = [int(i) for i in args[2:]]
                    for device_count in range(start_device_count,end_device_count):            
                        if device_count not in self.processes.keys():
                            self.processes[device_count] = {}
                        if process_count not in self.processes[device_count].keys():
                            self.processes[device_count][process_count] = {}
                        self.processes[device_count][process_count] = [
                            self.process_folder_names[process_count][folder_count] for folder_count in folder_count_at_each_depth
                        ]
        
        return string

if __name__ == "__main__":
    pass