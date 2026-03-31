#import sys_data #contains definitions of data structures for mmWave data parsing

import json
import logging
import threading
import time
from dataclasses import dataclass


try:
    import serial
except ImportError:
    serial = None

from .config import mmWaveConfig


@dataclass
class mmWaveTotalData:
    current_number_of_people: int = 0
    person_id_dict_current: dict = None
    person_id_dict_last: dict = None
    person_id_dict_history: dict = None

@dataclass
class mmWaveFrame:
    frame_header: str = ""
    total_length: int = 0
    current_frame_count: int = 0
    TLV1: int = 0 #TLV serves as a separator between different types of data. 01 00 00 00 is followed by point cloud data, while 02 00 00 00 is followed by people count data.
    constant: int = 0
    TLV2: int = 0
    length_of_personnel_data: int = 0
    reserved: str = ""
    personnel: list = None

@dataclass
class mmWavePersonnelFrame:
    new_id: str = ""
    id: int = 0
    reserved: str = ""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    speed_x: float = 0.0
    speed_y: float = 0.0
    speed_z: float = 0.0


class mmWaveHardwareInterface:

    def __init__(self, config: mmWaveConfig):
        self.config = config
        self.serial_conn = None
        self.running = False
        self.mmWave_total_data = mmWaveTotalData()



    def start(self) --> bool:
        '''Start the mmWave hardware interface'''
        try:
            if serial is None:
                raise ImportError("pyserial not available")
        
        self.serial_conn = serial.Serial(
            self.config.serial_port,
            self.config.baud_rate
        )

        self.running = True

        # Start reading thread
        self.read_thread = threading.Thread(target=self._read_serial_loop, daemon=True)
        self.read_thread.start()

    def _read_serial_loop(self):

    '''
    Takes in a hex string of mmWave data, parses it according 
    to the mmWave frame protocol, and updates the SYS_mmWave_total_data object 
    with the current number of people and their IDs. 
    
    It also puts the effective personnel data into a queue for further processing.
    '''
    def mmWave_frame_protocol_parsing(self, data): #data is in hex characters (hex string i think)
        len1 = len(data)
        if len1 < 64: #frames should always be longer than 64 hex characters
            print("Error frame length")
            return -1
        new_mmWave_frame = mmWaveFrame()  #define a new Frame
        new_mmWave_frame.frame_header = data[:16] #first 8bytes are header (corresponding to 16 hex characters)
        d1 = data[16:24] #4 bytes for length
        new_mmWave_frame.total_length = hex_string_to_int(d1)
        d1 = data[24:32] #4 bytes for frame count
        new_mmWave_frame.current_frame_count = hex_string_to_int(d1)
        d1 = data[32:40] #4 bytes for TLV1 (01 00 00 00)
        new_mmWave_frame.TLV1 = hex_string_to_int(d1)
        d1 = data[40:48] #4 bytes for point cloud data length (constant value 0) (why is dont they give us point cloud data?)
        new_mmWave_frame.constant = hex_string_to_int(d1)
        d1 = data[48:56] #4 bytes for TLV2 (02 00 00 00)
        new_mmWave_frame.TLV2 = hex_string_to_int(d1)
        d1 = data[56:64] #4 bytes for personnel data length
        d2 = hex_string_to_int(d1)
        d3 = int(d2 / 32) #number of personnel
        new_mmWave_frame.length_of_personnel_data = d3

        effective_data = data[64:] #all the rest of the data is personell data

        self.mmWave_total_data.current_number_of_people = d3
        # print("Current_number_of_people = ", d3)
        self.mmWave_coordinate_q.put(effective_data)  
        
        return 0