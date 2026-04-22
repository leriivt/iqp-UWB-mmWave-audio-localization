from mmWave_hardware import *
import numpy as np
import time

class MockHardwareInterface():

    def __init__(self, fps: float = 5.0):
        super().__init__()
        self.fps = fps
        self.running = False
        self.measurement_callback: Optional[Callable[[mmWaveFrame], None]] = None
        
        #read in from a file of frames
        self.frames = np.load("mmWave_frames_1776325128.npy", allow_pickle=True) 
        self.frame_index = 0
        self.total_frames = len(self.frames)

    def set_measurement_callback(self, callback: Callable[[mmWaveFrame], None]):
        """Set callback for processed measurements.
            The callback allows you to feed in a function that
            will be called with each new mmWaveFrame after it's processed.
            Can be used to add the frames to a queue of send it through MQTT
        """
        self.measurement_callback = callback

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _run(self):
        while self.running:
            frame = self._generate_frame()
            if self.measurement_callback:
                self.measurement_callback(frame)
            time.sleep(1.0 / self.fps)
            

    def _generate_frame(self) -> mmWaveFrame:
        frame = self.frames[self.frame_index]
        self.frame_index = (self.frame_index + 1) % self.total_frames #loop through the frames in the file
        return frame