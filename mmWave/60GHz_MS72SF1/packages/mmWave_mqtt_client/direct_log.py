from mmWave_hardware import *
import time

config = mmWaveConfig()
hardware_interface = mmWaveHardwareInterface(config, mode=0)

def log_mmWave_frame_personnel(frame: mmWaveFrame):
    logger.info(json.dumps({
        "event": "new_mmWave_frame",
        "frame_count": frame.current_frame_count,
        "num_personnel": len(frame.personnel),
        "personnel": [
            {
                "id": p.id,
                "x": p.x,
                "y": p.y,
                "z": p.z,
                "speed_x": p.speed_x,
                "speed_y": p.speed_y,
                "speed_z": p.speed_z
            }
            for p in frame.personnel
        ]
    }))

def log_mmWave_frame_point_cloud(frame: mmWaveFrame):
    logger.info(json.dumps({
        "event": "new_mmWave_frame",
        "frame_count": frame.current_frame_count,
        "num_points": len(frame.point_cloud),
        "point_cloud": [
            {
                "x": p.x,
                "y": p.y,
                "z": p.z,
            }
            for p in frame.point_cloud
        ]
    }))

hardware_interface.set_measurement_callback(log_mmWave_frame_personnel)
hardware_interface.start()

#loop forever, can be stopped with Ctrl+C
#otherwise the daemon thread will just kill itself when this main script exits
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    hardware_interface.stop()