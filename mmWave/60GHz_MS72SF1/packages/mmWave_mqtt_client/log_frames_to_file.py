from mmWave_hardware import *
import time
import numpy as np

config = mmWaveConfig()
hardware_interface = mmWaveHardwareInterface(config)


FRAME_PERIOD_MS = 200
LOG_TIME_MINUTES = 5
MAX_FRAMES = int((LOG_TIME_MINUTES * 60 * 1000) / FRAME_PERIOD_MS)  # 1500

def log_mmWave_frame(frame: mmWaveFrame, arr: list):
    arr.append(frame)
    if len(arr) >= MAX_FRAMES:
        #save to file
        arr = np.array(arr, dtype=object) #save as numpy array of objects (mmWaveFrame instances)
        filename = f"mmWave_frames_{int(time.time())}.npy"
        np.save(filename, arr)
        print(f"Saved {len(arr)} frames to {filename}")
        #exit program
        hardware_interface.stop()
        exit(0)

arr = []
hardware_interface.set_measurement_callback(lambda frame: log_mmWave_frame(frame, arr))
hardware_interface.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    hardware_interface.stop()
