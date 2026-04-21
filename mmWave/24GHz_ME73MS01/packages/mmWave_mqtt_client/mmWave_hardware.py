#import sys_data #contains definitions of data structures for mmWave data parsing

import json
import logging
import threading
import struct
from typing import Callable, Optional
from dataclasses import dataclass
import math

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



MAGIC_HEADER = b'\x55\xA5'

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
            # Check if we have enough for a header with length
            if len(self.buffer) < 4:
                break
            frame_len = int.from_bytes(self.buffer[2:4], 'little') + 4 #little endian
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
    HEAD    2 bytes
    LEN     2 bytes (little endian)
    FUNC CODE 1 byte (we care about "passive reporter" which is 0x2)
    CMD    2 bytes (specifies speficic function)
    PERSONNEL DATA  ? bytes (length of personnel data in bytes, should be a multiple of 10 since each person has 10 bytes of data)
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

        func_code = frame_bytes[4] #5th byte is function code
        if func_code != 0x2: #we only care about passive reporter frames which have function code 0x2
            return None        
        personnel_data = frame_bytes[7:frame_len-1] #exclude checksum which is last byte


        new_mmWave_frame.personnel = self._parse_personnel_data(personnel_data)

        return new_mmWave_frame

    #helper function to parse the personnel data section of a frame 
    #into a list of mmWavePersonnelFrame objects
    #10 bytes per person
    def _parse_personnel_data(self, personnel_bytes: bytes):
        personnel_list = []
        for i in range(0, len(personnel_bytes), 10):
            person_data = personnel_bytes[i:i+10]

            new_mmWave_personnel_frame = mmWavePersonnelFrame()
            
            #parse person data into ID and distance info
            new_mmWave_personnel_frame.id = int.from_bytes(person_data[0:1], 'little')
            #byte 1 is whether person is nobody, static, or moving
            #if is nobody, we can skip the rest of the data for this person
            if person_data[1] == 0: #nobody
                continue
            distance = int.from_bytes(person_data[2:4], 'little')
            #bytes 4 and 5 are speed
            yaw = int.from_bytes(person_data[6:7], 'little', signed=True) #in degrees
            pitch = int.from_bytes(person_data[7:8], 'little', signed=True)


            new_mmWave_personnel_frame.x = distance * math.cos(math.radians(yaw)) * math.cos(math.radians(pitch))
            new_mmWave_personnel_frame.y = distance * math.sin(math.radians(yaw)) * math.cos(math.radians(pitch))
            new_mmWave_personnel_frame.z = distance * math.sin(math.radians(pitch))

            personnel_list.append(new_mmWave_personnel_frame)
        return personnel_list

    
    def stop(self):
        self.running = False
        self.serial_conn.close()

