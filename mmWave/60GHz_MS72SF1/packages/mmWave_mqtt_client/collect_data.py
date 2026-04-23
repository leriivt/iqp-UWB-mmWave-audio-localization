import threading
import time
import sys

from mmWave_hardware import *
import numpy as np
import csv
from enum import Enum, auto
import pickle

from mmWave_visualizer_Qt6 import *
from mock_hardware_interface import *


class State(Enum):
    GET_PERSONNEL_ID  = auto()
    COLLECTING_FRAMES = auto()
    VALIDATE_FRAMES   = auto()
    SAVE_OR_RETAKE    = auto()
    SAVE_FRAMES       = auto()
    DONE              = auto()

class CollectionInterface:
    def __init__(self, hardware_interface, reference_csv: str):
        self.hardware_interface = hardware_interface
        self.frames_threshold = 100
        #self.is_new_frame = True
        self.new_frame_event = threading.Event()

        self.reference_csv = reference_csv
        self.test_points = self._extract_reference_csv()
        #start output csv named using dynamic timestamp
        self.output_csv = self._start_output_csv(f"collected_data_{int(time.time())}.csv")
        self.output_pickle = f"collected_frames_{int(time.time())}.pkl"

        self.current_frame = None
        self.a_previous_frame = None

        self.frame_list = []
        self.collection_thread = threading.Thread(target=self._collection_loop)
        self.collection_thread.daemon = True

        self.lock = threading.Lock() #lock for accessing the last frame

    #turns the reference csv into a list of dicts with keys containing test positions
    def _extract_reference_csv(self):
        #read the reference csv file and return a dict of timestamp to reference position
        with open(self.reference_csv, "r") as f:
            reader = csv.DictReader(f)
            self.test_points = list(reader)
        return self.test_points

    def _start_output_csv(self, filename: str):
        #create a csv file with headers including those originally in the reference csv plus the mmWave frame data (id, x, y, z, speed_x, speed_y, speed_z)
        #extract the old headers from the reference csv based on self.test_points
        old_headers = self.test_points[0].keys()
        new_headers = ["id", "x", "y", "z", "speed_x", "speed_y", "speed_z"]
        self.headers = list(old_headers) + new_headers
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writeheader()
        return filename
        


    def start(self):
        self.collection_thread.start()
    '''
    def _collection_loop(self):
        for test_point in self.test_points:
            print(f"Collecting data for test point: {test_point}")
            personnel_id = input("Please enter id of desired personnel: ")
            while not self.check_valid_id(personnel_id):
                personnel_id = input("Invalid id. Please enter id of desired personnel: ")

            #at this point we have a valid personnel id for the current frame
            print(f"Collecting data for personnel id {personnel_id} at test point {test_point}")
            #collect 100 frames of data for this personnel id
            collected_frames = 0
            while collected_frames < self.frames_threshold:
                if self.last_frame is self.is_new_frame:
                    with self.lock:
                        self.frame_list.append(self.last_frame)
                        self.is_new_frame = False
                    collected_frames += 1
            
            valid_frames = self.validate_frames(personnel_id)
            print(f"Collected {len(valid_frames)} valid frames for personnel id {personnel_id}")
            save_choice = input("Type y to save frames or n to discard and retake data for this test point: ")
            if save_choice == "y":
                save_frames_to_file(valid_frames)
            else if save_choice == "n":
                print("Discarding frames and retaking data for this test point.")
            else:
                print("Invalid choice. Please enter 'y' or 'n'.")
    '''
    def _collection_loop(self):
        for test_point in self.test_points:
            print(f"Collecting data for test point: {test_point}")

            state        = State.GET_PERSONNEL_ID
            personnel_id = None
            valid_frames = None

            while state != State.DONE:

                if state == State.GET_PERSONNEL_ID:
                    personnel_id = input("Please enter id of desired personnel: ")
                    if self.check_valid_id(personnel_id):
                        state = State.COLLECTING_FRAMES
                    else:
                        print("Invalid id.")

                elif state == State.COLLECTING_FRAMES:
                    self.frame_list.clear()

                    print(f"Collecting data for personnel id {personnel_id} at test point {test_point}")
                    collected_frames = 0
                    while collected_frames < self.frames_threshold:
                        #if self.is_new_frame:   # new frame arrived
                        if self.new_frame_event.wait(timeout=1.0):
                            with self.lock:
                                self.frame_list.append(self.current_frame)
                                self.new_frame_event.clear()
                                #self.is_new_frame = False
                            collected_frames += 1
                            
                        else:
                            #time.sleep(0.01) #sleep briefly to avoid busy waiting
                            print("Warning reached timeout, retrying...") #will keep retrying, timeout just to let you know its taking longer than usual
                            break
                    state = State.VALIDATE_FRAMES

                elif state == State.VALIDATE_FRAMES:
                    valid_frames = self.validate_frames(personnel_id)
                    print(f"Collected {len(valid_frames)} valid frames for personnel id {personnel_id}")
                    state = State.SAVE_OR_RETAKE

                elif state == State.SAVE_OR_RETAKE:
                    save_choice = input("Type y to save or n to discard and retake: ")
                    if save_choice == "y":
                        state = State.SAVE_FRAMES
                    elif save_choice == "n":
                        print("Discarding frames and retaking data for this test point.")
                        self.frame_list.clear() 
                        state = State.GET_PERSONNEL_ID  # loop back
                    else:
                        print("Invalid choice. Please enter 'y' or 'n'.")
                        # stay in SAVE_OR_RETAKE

                elif state == State.SAVE_FRAMES:
                    self.save_frames_to_csv(test_point, valid_frames, personnel_id)
                    self.save_frames_to_pkl(valid_frames)
                    self.frame_list.clear()
                    state = State.DONE
        print("Collection complete! You may close out of visualizer")       


    def check_valid_id(self, personnel_id: str):
        #check if the personnel id is valid for the current frame
        with self.lock:
            if self.current_frame is None:
                print("No frame received yet")
                return False
            for p in self.current_frame.personnel:
                if str(p.id) == personnel_id:
                    return True
        print(f"Personnel id {personnel_id} not found in current frame")
        return False

    def validate_frames(self, personnel_id: str):
        #check if the collected frames have the desired personnel id
        valid_frames = []
        for frame in self.frame_list:
            for p in frame.personnel:
                if str(p.id) == personnel_id:
                    valid_frames.append(frame)
                    break
        return valid_frames

    #callback function to update the last frame
    def update_current_frame(self, frame: mmWaveFrame):
        with self.lock:
            self.current_frame = frame
            #self.is_new_frame = True
        self.new_frame_event.set()

    def save_frames_to_csv(self, test_point: dict, frames: list, personnel_id: str):
        #save the frames to the output csv file with the test point info and personnel id
        with open(self.output_csv, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            for frame in frames:
                for p in frame.personnel:
                    if str(p.id) == personnel_id:
                        row = {**test_point, "id": p.id, "x": p.x, "y": p.y, "z": p.z, "speed_x": p.speed_x, "speed_y": p.speed_y, "speed_z": p.speed_z}
                        writer.writerow(row)
                        break

    def save_frames_to_pkl(self, frames: list):
        #save the frames to a pickle file
        with open(self.output_pickle, "ab") as f:
            pickle.dump(frames, f)
        print(f"Saved {len(frames)} frames to {self.output_pickle}")

def combine_callbacks(app_window: mmWaveVisualizer, collection_interface: CollectionInterface):
    def combined(frame: mmWaveFrame):
        app_window.feed_frame(frame)
        collection_interface.update_current_frame(frame)
    return combined

#whenever get a new mmWave frame, both visualizer and collection_interface will update
def integrate_hardware_visualizer_collection(hardware_interface, app_window: mmWaveVisualizer, collection_interface: CollectionInterface):
    callback = combine_callbacks(app_window, collection_interface)
    hardware_interface.set_measurement_callback(callback)


if __name__ == "__main__":
    
    config = mmWaveConfig()
    hardware_interface = mmWaveHardwareInterface(config)
    
    app = QApplication(sys.argv)
    window = mmWaveVisualizer(is_ceiling=False)

    collection_interface = CollectionInterface(hardware_interface, "wall_reference.csv")

    integrate_hardware_visualizer_collection(hardware_interface, window, collection_interface)   # hardware_interface is your mmWaveHardwareInterface

    hardware_interface.start()
    window.show()
    collection_interface.start()

    sys.exit(app.exec())
    
    '''
    #below this is for validating if this code works
    mock_hardware_interface = MockHardwareInterface()

    app = QApplication(sys.argv)
    window = mmWaveVisualizer(is_ceiling=False)

    collection_interface = CollectionInterface(mock_hardware_interface, "wall_reference.csv")

    integrate_hardware_visualizer_collection(mock_hardware_interface, window, collection_interface)   # hardware_interface is your mmWaveHardwareInterface

    mock_hardware_interface.start()
    window.show()
    collection_interface.start()

    sys.exit(app.exec())
    '''
    
