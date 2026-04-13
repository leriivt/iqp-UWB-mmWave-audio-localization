import serial
import threading
import queue

from .config import mmWaveConfig
'''
This module defines the SerialReader class, 
which handles reading data from the mmWave 
hardware via a serial connection. It uses a 
separate thread to continuously read from the 
serial port and stores incoming data in a thread-safe 
queue for processing by the main application.
'''
class SerialReader:
    def __init__(self, config: mmWaveConfig):
        self.config = config
        self.serial_conn = None
        self.running = False

        #queue for storing incoming serial data
        self.data_queue = queue.Queue()

        self.read_thread = None

    def start(self):
        self.serial_conn = serial.Serial(
            self.config.serial_port,
            self.config.baud_rate
        )

        self.running = True
        self.read_thread = threading.Thread(target=self._read_serial_loop, daemon=True)
        self.read_thread.start()

    def stop(self):
        self.running = False
        self.ser.close()

    def _read_serial_loop(self):
        while self.running:
            data = self.ser.read(self.ser.in_waiting or 1)
            if data:
                self.data_queue.put(data)
            
    
        
