import serial
import threading
import queue
import struct

import * from .sys_mmWave
'''
Takes in the raw byte data from SerialReader and parses it into structured frames
and stores is in sys-mmWaveFrame format.
'''
MAGIC_HEADER = b'\x01\x02\x03\x04\x05\x06\x07\x08'  

class FrameParser:
    def __init__(self):
        self.buffer = bytearray()
        self.frame_queue = queue.Queue()

    def feed(self, raw_bytes: bytes):
        """Feed raw bytes; returns list of complete parsed frames."""
        self.buffer.extend(raw_bytes)

        while True:
            index = self.buffer.find(MAGIC_HEADER)
            if index == -1: #cant find any more frames in the buffer
                break
            # Discard bytes before magic word
            if index > 0:
                self.buffer = self.buffer[index:]
            # Check if we have enough for a header
            if len(self.buffer) < 12:  # header size varies by SDK
                break
            frame_len = int.from_bytes(self.buffer[8:12], 'little') #little endian
            # Check if we have the full frame
            if len(self.buffer) < frame_len:
                break
            frame_bytes = bytes(self.buffer[:frame_len])
            self.buffer = self.buffer[frame_len:]
            self.frame_queue.put(self._parse_frame(frame_bytes))


    '''
    HEAD    8 bytes
    LEN     4 bytes (little endian)
    FRAME COUNT 4 bytes (little endian)
    TLV1    4 bytes (01 00 00 00)
    POINT CLOUD DATA LEN 4 bytes (constant value 0)
    TLV2    4 bytes (02 00 00 00)
    PERSONNEL DATA LEN 4 bytes (length of personnel data in bytes, should be a multiple of 32 since each person has 32 bytes of data)
    PERSONNEL DATA (32 bytes per person, contains ID and distance info for each person)
    '''
    def _parse_frame(self, frame_bytes: bytes):
        frame_len = len(frame_bytes)
        if frame_len < 32: #frames should always be longer than 32 bytes
            print("Error frame length")
            return -1

        new_mmWave_frame = mmWaveFrame()  #define a new Frame
        new_mmWave_frame.current_frame_count = int.from_bytes(frame_bytes[12:16], 'little')

        #bytes 16 to 28 are TLV tags and constant values, skip them

        #length_of_personnel_data = int.from_bytes(frame_bytes[28:32], 'little')
        #number_of_personnel = int(length_of_personnel_data / 32)
        personnel_data = frame_bytes[32:] #all the rest of the data is personnel data
        new_mmWave_frame.personnel = self._parse_personnel_data(personnel_data)

        return new_mmWave_frame

    def _parse_personnel_data(self, personnel_bytes: bytes):
        personnel_list = []
        for i in range(0, len(personnel_bytes), 32):
            person_data = personnel_bytes[i:i+32]

            new_mmWave_personnel_frame = mmWavePersonnelFrame()
            
            #parse person data into ID and distance info
            new_mmWave_personnel_frame.id = int.from_bytes(person_data[4:8], 'little')

            new_mmWave_personnel_frame.x = bytes_to_float(person_data[8:12])
            new_mmWave_personnel_frame.y = bytes_to_float(person_data[12:16])
            new_mmWave_personnel_frame.z = bytes_to_float(person_data[16:20])

            new_mmWave_personnel_frame.speed_x = bytes_to_float(person_data[20:24])
            new_mmWave_personnel_frame.speed_y = bytes_to_float(person_data[24:28])
            new_mmWave_personnel_frame.speed_z = bytes_to_float(person_data[28:32])

            personnel_list.append(new_mmWave_personnel_frame)
        return personnel_list


def bytes_to_float(b: bytes) -> float:
    """Convert 4 bytes to a float (assuming IEEE 754 format)."""
    
    return struct.unpack('<f', b)[0]  # little-endian float