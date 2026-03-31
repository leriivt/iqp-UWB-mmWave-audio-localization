#contains classes that store mmWave data (depricated)

class SYS_mmWave_total_data(object):
    def __init__(self):
        self.Current_number_of_people = 0
        self.Person_ID_dict_Current = {}

        self.Person_ID_dict_last = {}
        self.Person_ID_dict_history = {}

class SYS_mmWave_Frame(object):
    def __init__(self):
        self.Frame_header = ""
        self.total_length = 0
        self.current_frame_count = 0
        self.TLV1 = 0 #TLV serves as a separator between different types of data. 01 00 00 00 is followed by point cloud data, while 02 00 00 00 is followed by people count data.
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


