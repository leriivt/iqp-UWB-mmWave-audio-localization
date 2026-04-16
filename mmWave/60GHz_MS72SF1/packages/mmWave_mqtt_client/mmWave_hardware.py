#import sys_data #contains definitions of data structures for mmWave data parsing

import json
import logging
import threading
import struct
from typing import Callable, Optional
from dataclasses import dataclass


try:
    import serial
except ImportError:
    serial = None

from config import mmWaveConfig

# Setup JSON logging
logging.basicConfig(
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


@dataclass
class mmWaveTotalData:
    current_number_of_people: int = 0
    person_id_dict_current: dict = None
    person_id_dict_last: dict = None
    person_id_dict_history: dict = None

@dataclass
class mmWaveFrame:
    current_frame_count: int = 0
    personnel: list = None
    point_cloud: list = None

@dataclass
class mmWavePersonnelFrame:
    id: int = 0

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    speed_x: float = 0.0
    speed_y: float = 0.0
    speed_z: float = 0.0

@dataclass
class mmWavePointCloudFrame:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    v: float = 0
    snr: float = 0
    id: float = 0
    power: float = 0


def bytes_to_float(b: bytes) -> float:
    """Convert 4 bytes to a float (assuming IEEE 754 format)."""   
    return struct.unpack('<f', b)[0]  # little-endian float


MAGIC_HEADER = b'\x01\x02\x03\x04\x05\x06\x07\x08'

class mmWaveHardwareInterface:
    def __init__(self, config: mmWaveConfig, mode: int = 0):
        self.config = config
        self.mode = mode
        self.serial_conn = None
        self.running = False
        #self.mmWave_total_data = mmWaveTotalData()
        self.measurement_callback: Optional[Callable[[mmWaveFrame], None]] = None

        #buffer for incoming serial data
        self.buffer = bytearray()

    def set_measurement_callback(self, callback: Callable[[mmWaveFrame], None]):
        """Set callback for processed measurements.
            The callback allows you to feed in a function that
            will be called with each new mmWaveFrame after it's processed.
            Can be used to add the frames to a queue of send it through MQTT
        """
        self.measurement_callback = callback



    def start(self) -> bool:
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

            return True
        
        except Exception as e:
            logger.error(json.dumps({
                "event": "mmWave_interface_start_failed",
                "error": str(e),
                "serial_port": self.config.serial_port
            }))
            return False


    def _read_serial_loop(self):
        while self.running:
            data = self.serial_conn.read(self.serial_conn.in_waiting or 1)
            if data:
                self.buffer.extend(data)

                self._process_buffer()

            
            
    def _process_buffer(self):
        """Process the buffer to extract complete frames and update total data."""
        while True:
            index = self.buffer.find(MAGIC_HEADER)
            if index == -1: #cant find any more frames in the buffer
                break
            # Discard bytes before magic word
            if index > 0:
                self.buffer = self.buffer[index:]
            # Check if we have enough for a header
            if len(self.buffer) < 12:
                break
            frame_len = int.from_bytes(self.buffer[8:12], 'little') #little endian
            # Check if we have the full frame
            if len(self.buffer) < frame_len:
                break
            frame_bytes = bytes(self.buffer[:frame_len])
            self.buffer = self.buffer[frame_len:]

            processed_frame = self._parse_frame(frame_bytes)
            if processed_frame is None:
                continue  # skip bad frame, keep processing buffer

            #use the callback function once we process a frame
            if self.measurement_callback:
                self.measurement_callback(processed_frame)
                 
    
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
    #helper function to parse a complete frame of data into a mmWaveFrame object
    def _parse_frame(self, frame_bytes: bytes):
        frame_len = len(frame_bytes)
        if frame_len < 32: #frames should always be longer than 32 bytes
            logger.warning(json.dumps({
                "event": "frame_too_short",
                "frame_length": len(frame_bytes),
                "minimum_length": 32
            }))
            return None

        new_mmWave_frame = mmWaveFrame()  #define a new Frame
        new_mmWave_frame.current_frame_count = int.from_bytes(frame_bytes[12:16], 'little')
        
        '''
        if (self.mode == 0): #if we are looking at personnel data
            #bytes 16 to 28 are TLV tags and constant values, skip them

            #length_of_personnel_data = int.from_bytes(frame_bytes[28:32], 'little')
            #number_of_personnel = int(length_of_personnel_data / 32)
        
            personnel_data = frame_bytes[32:] #all the rest of the data is personnel data
            new_mmWave_frame.personnel = self._parse_personnel_data(personnel_data)

        if (self.mode == 1): #if we are looking at point cloud data
            #bytes 16 to 20 are TLV tag 1
            point_cloud_data_len = int.from_bytes(frame_bytes[20:24], 'little')

            point_cloud_data = frame_bytes[24:24+point_cloud_data_len]
            new_mmWave_frame.point_cloud = self._parse_point_cloud_data(point_cloud_data)
        '''
        #bytes 16 to 20 are TLV tag 1
        point_cloud_data_len = int.from_bytes(frame_bytes[20:24], 'little')
        point_cloud_end_index = 24 + point_cloud_data_len
        point_cloud_data = frame_bytes[24:point_cloud_end_index]
        new_mmWave_frame.point_cloud = self._parse_point_cloud_data(point_cloud_data)


        #4 bytes after point cloud data is TLV tag 2, then 4 bytes of personnel data length
        personnel_data = frame_bytes[point_cloud_end_index + 4 + 4:] #all the rest of the data is personnel data
        new_mmWave_frame.personnel = self._parse_personnel_data(personnel_data)

        return new_mmWave_frame

    #helper function to parse the personnel data section of a frame 
    #into a list of mmWavePersonnelFrame objects
    def _parse_personnel_data(self, personnel_bytes: bytes):
        personnel_list = []
        for i in range(0, len(personnel_bytes), 32):
            person_data = personnel_bytes[i:i+32]

            new_mmWave_personnel_frame = mmWavePersonnelFrame()
            
            #parse person data into ID and distance info
            #note: first 4 bytes are reserved and unused
            new_mmWave_personnel_frame.id = int.from_bytes(person_data[4:8], 'little')

            new_mmWave_personnel_frame.x = bytes_to_float(person_data[8:12])
            new_mmWave_personnel_frame.y = bytes_to_float(person_data[12:16])
            new_mmWave_personnel_frame.z = bytes_to_float(person_data[16:20])

            new_mmWave_personnel_frame.speed_x = bytes_to_float(person_data[20:24])
            new_mmWave_personnel_frame.speed_y = bytes_to_float(person_data[24:28])
            new_mmWave_personnel_frame.speed_z = bytes_to_float(person_data[28:32])

            personnel_list.append(new_mmWave_personnel_frame)
        return personnel_list

    #helper function to parse the point cloud data section of a frame
    #into a list of mmWavePointCloudFrame objects
    def _parse_point_cloud_data(self, point_cloud_bytes: bytes):
        point_cloud_list = []
        for i in range(0, len(point_cloud_bytes), 25):
            point_data = point_cloud_bytes[i:i+25]

            new_mmWave_point_cloud_frame = mmWavePointCloudFrame()

            new_mmWave_point_cloud_frame.x = bytes_to_float(point_data[0:4])
            new_mmWave_point_cloud_frame.y = bytes_to_float(point_data[4:8])
            new_mmWave_point_cloud_frame.z = bytes_to_float(point_data[8:12])

            new_mmWave_point_cloud_frame.v = point_data[12] * 0.11 #multipy by 0.11m/s to get true velocity
            new_mmWave_point_cloud_frame.snr = bytes_to_float(point_data[13:17])
            new_mmWave_point_cloud_frame.id = bytes_to_float(point_data[17:21])
            new_mmWave_point_cloud_frame.power = bytes_to_float(point_data[21:25])

            point_cloud_list.append(new_mmWave_point_cloud_frame)
        return point_cloud_list
    
    def stop(self):
        self.running = False
        self.serial_conn.close()

