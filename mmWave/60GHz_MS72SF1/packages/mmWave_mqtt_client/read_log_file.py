from mmWave_hardware import *
import numpy as np
import pickle

def pickle_load_all_frames_flat(filepath: str):
    all_frames = []
    with open(filepath, "rb") as f:
        while True:
            try:
                batch = pickle.load(f)
                all_frames.extend(batch)
            except EOFError:
                break
    return all_frames
#arr = np.load("mmWave_frames_1776325128.npy", allow_pickle=True) 
arr = pickle_load_all_frames_flat("collected_frames_1776860054.pkl")

print(f"Loaded {len(arr)} frames")
print(type(arr[0]))

def print_frame_info(frame: mmWaveFrame):
    print(f"Frame count: {frame.current_frame_count}")
    print(f"Number of personnel: {len(frame.personnel)}")
    for p in frame.personnel:
        print(f"  Personnel ID: {p.id}, x: {p.x}, y: {p.y}, z: {p.z}, speed_x: {p.speed_x}, speed_y: {p.speed_y}, speed_z: {p.speed_z}")
    print(f"Number of points in point cloud: {len(frame.point_cloud)}")
    for i, point in enumerate(frame.point_cloud[:100]): #print first 10 points
        print(f"  Point {i}: x: {point.x}, y: {point.y}, z: {point.z}, id: {point.id}")
'''
for frame in arr:
    print_frame_info(frame)
'''

#print the first 50 frames
for i in range(min(700, len(arr))):
    print(f"Frame {i}:")
    print_frame_info(arr[i])