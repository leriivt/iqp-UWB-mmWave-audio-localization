

class SYS_DATA(object):
    def __init__(self):
        self.data_all = ""
        self.mac = ""
        self.rssi = -120
        self.ID = 0
        self.data = []
        self.scan_timeout = 1
        self.err_command_list = []


sys_data2 = SYS_DATA()

class SYS_RELIABILITY_DATA(object):
    def __init__(self):
        self.SN = 0
        self.name = ""
        self.Send_command_TYPE = "ASCII"
        self.Send_data_TYPE = "ASCII"
        self.return_ok_command_TYPE = "ASCII"
        self.return_ok_data_TYPE = "ASCII"
        self.return_err_command_TYPE = "ASCII"
        self.return_err_data_TYPE = "ASCII"
        
        self.Send_command = ""
        self.Send_data = ""
        self.return_ok_command = ""
        self.return_ok_data = ""
        self.return_err_command = ""
        self.return_err_data = ""

        self.next_delay = 0
        self.Previous_delay = 0
        self.err_delay = 0
        self.err_flag = 0
        self.result_remark = ""


class SYS_RELIABILITY_SEND_DATA(object):
    def __init__(self):
        self.SN = 0
        self.name = ""
        
        self.Send_data_str = ""
        self.Send_data_hex = ""

        self.return_ok_data_str = ""
        self.return_ok_data_hex = ""

        self.return_err_data_str = ""
        self.return_err_data_hex = ""

        self.next_delay = 0
        self.Previous_delay = 0
        self.err_delay = 0
        self.err_flag = 0
        self.result_remark = ""





class SYS_mmWave_write(object):
    def __init__(self):
        self.name = ""
        self.command_type = "ASCII"
        self.command = ""
        self.data_type = "INT"
        self.data = 0
        self.command_end_type = "ASCII"
        self.command_end = "\n"
        self.rev_type = "ASCII"
        self.rev_len_max = 0
        self.rev_data = 0

        self.send_len = 0
        self.send_max = 0
        self.send_min = 0
        
        self.rev_len = 0
        self.rev_max = 0
        self.rev_min = 0


class SYS_mmWave_Frame(object):
    def __init__(self):
        self.Frame_header = ""
        self.total_length = 0
        self.current_frame_count = 0
        self.TLV1 = 0
        self.constant = 0
        self.TLV2 = 0
        self.length_of_personnel_data = 0
        self.Reserved = ""
        self.Personnel = []

class SYS_mmWave_Personnel_Frame(object):
    def __init__(self):
        self.new_id = ""
        self.ID = 0
        self.reserve = ""
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

        self.speed_x = 0.0
        self.speed_y = 0.0
        self.speed_z = 0.0


class SYS_mmWave_total_data(object):
    def __init__(self):
        self.Current_number_of_people = 0
        self.Person_ID_dict_Current = {}

        self.Person_ID_dict_last = {}
        self.Person_ID_dict_history = {}
        
