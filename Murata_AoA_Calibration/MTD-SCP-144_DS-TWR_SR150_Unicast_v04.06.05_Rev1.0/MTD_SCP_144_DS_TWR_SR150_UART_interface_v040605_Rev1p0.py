# /*====================================================================================*/
# /*                                                                                    */
# /*                        Copyright 2022 NXP                                          */
# /*                                                                                    */
# /*   All rights are reserved. Reproduction in whole or in part is prohibited          */
# /*   without the written consent of the copyright owner.                              */
# /*                                                                                    */
# /*   NXP reserves the right to make changes without notice at any time. NXP makes     */
# /*   no warranty, expressed, implied or statutory, including but not limited to any   */
# /*   implied warranty of merchantability or fitness for any particular purpose,       */
# /*   or that the use will not infringe any third party patent, copyright or trademark.*/
# /*   NXP must not be liable for any loss or damage arising from its use.              */
# /*                                                                                    */
# /*====================================================================================*/
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import os
import queue
import serial
import signal
import sys
import time
import zmq
import re
from datetime import datetime
from threading import Thread, Event, Condition
from datetime import datetime

MAX_RETRY_NUMBER = 20
BAUDRATE = 3000000
meas_idx = 1 
#texte name for the radar plot
txt_name = ""
cir_data = False
# retry_counter for the device init command
retry_count = 0
# Flag for the session handle to get the function active until the handle is known
waitting_for_session_handle = True

UWB_EXT_READ_CALIB_DATA_XTAL_CAP_NTF = bytes([0x6A, 0x01, 0x00, 0x05])
UWB_EXT_READ_CALIB_DATA_TX_POWER_NTF = bytes([0x6A, 0x01, 0x00, 0x06])


log_file = None

def set_log_file(filepath):
    global log_file
    log_file = open(filepath, 'w')
    log_file.write("Timestamp,Sequence,NLoS,Distance_cm,Azimuth_deg,Elevation_deg,Azimuth_FOM,Elevation_FOM,RSSI,PDoA1,PDoA2\n")
    log_file.flush()

# Definition of the different element needed for the application
class UartInterface:
    last_session_started = [0x00, 0x00, 0x00, 0x00]
    session_handle_flag = False
    stop_write_thread = False
    stop_read_thread = False
    command_queue = queue.Queue(maxsize=100)
    go_stop = Event()
    write_wait = Condition()
    retry_cmd = False
    serial_port = serial.Serial()
    # To display plot of rframe data
    is_cir_plot  = False
    socket = None
    # Not draw when index is negative
    range_plot = {"index": -1, "valid": False, "nlos": 0, "distance": 0,
                "azimuth": 0, "elevation": 0, "avg_azimuth": 0, "avg_elevation": 0,
                "dest_azimuth": 0, "dest_elevation": 0, "avg_dest_azimuth": 0, "avg_dest_elevation": 0}
    # Not draw when number of measurement is zero
    cir_plot = {"nb_meas": 0, "mappings": [], "cir_samples": []}
    # To display plot of range data
    is_range_plot = False
    # Number of valid measurement before stop (0: no stop)
    nb_meas = 0
    session_handle = [0x00, 0x00, 0x00, 0x00]
    # Power offset
    power_offset = 0
    is_timestamp = False

def isCirPackage(cir):
    # only report if the hex string could possibly be a cir
    str_num_bytes = 0
    if cir[2] == '0':
        str_num_bytes = cir[6:8]
    else:
        str_num_bytes = cir[4:8]

    packetLength = int.from_bytes(bytes.fromhex(str_num_bytes), byteorder='little')

    if packetLength > 2052:
        return False

    if len(cir[8:])/2 != packetLength:
        print("Data lenght does not match given length: expected " + str(int.from_bytes(bytes.fromhex(str_num_bytes), byteorder='little')) + " bytes and received " + str(int(len(cir[8:])/2)) + " bytes.")
        print(cir)
        return False
    else:
        return True

def extractCir(logFileName, cirFolder):

    logfilereader = open(logFileName, mode='r', encoding="unicode_escape")

    text = "".join([str(l) for l in logfilereader])
    #text = "\n" + text

    CirLines = re.findall("[^A-F^a-f^0-9]{1,1}[67]9[A-Fa-f0-9]{11,4105}", text.replace(" ", "") )
    #CirLines = text
    CirLines = [l[1:] for l in CirLines]
    CirLines = [l for l in CirLines if isCirPackage(l)]

    newcirs = []
    message_block = False
    current_cir_lenght = -1
    current_cir_count = 0
    current_num_cirs = 0
    header1len = 28
    header2len = 8

    for l in CirLines:
        if not message_block and l.startswith("79"):
            newcirs.append(l[header1len:])
            current_num_cirs = int.from_bytes(bytes.fromhex(l[20:24]), byteorder='little')
            current_cir_lenght = int.from_bytes(bytes.fromhex(l[24:28]), byteorder='little') * 8
            current_cir_count = 0
            message_block = True
        elif message_block and (l.startswith("79") or l.startswith("69")):
            newcirs[-1] = newcirs[-1] + l[header2len:]
            while(current_cir_count < current_num_cirs - 1) and (len(newcirs[-1]) > current_cir_lenght):
                tmp = newcirs[-1][:current_cir_lenght]
                newcirs.append(newcirs[-1][current_cir_lenght:])
                newcirs[-2] = tmp
                current_cir_count += 1
            if(l.startswith("69")):
                message_block = False
    
    CirLines = newcirs

    # create the folder for the binaries of skip the folder if it already exists
    if not os.path.exists(cirFolder):
        os.mkdir(cirFolder)

    old_cirnumber = [-1, -1, -1, -1]
    cir_counter = [0, 0, 0, 0]

    for cir in CirLines:
        rx = 0
        try:
            rx = int(cir[32:34])
        except:
            print("Could not read Rx entry. Skipping File: " + str(cir))
            continue
        cir_counter[rx] += 1
        bincirn = bytes.fromhex(cir[0:8])
        cirnumber = int.from_bytes(bincirn, byteorder='little') - 2
        if old_cirnumber[rx] == -1 or old_cirnumber[rx] + 1 == cirnumber:
            old_cirnumber[rx] = cirnumber
        else:
            print("Cir index ist not continuos " + str(old_cirnumber[rx]) + " -> " + str(cirnumber))
            old_cirnumber[rx] = cirnumber
        
        cirfilename = cirFolder + "/cir_radar_rx" + str(rx) + "_" + str(cirnumber) +".bin"
        if os.path.exists(cirfilename):
            print("Writing a cir file that already exists. Are there multiple radar sessions in the log file. ( cirnumber: " + str(cirnumber) + ")")
        writer = open(cirfilename, 'wb')
        writer.write(bytes.fromhex(cir))
        writer.close()
    print("Checked " + str(cir_counter[1]) + " rx1 files and " + str(cir_counter[2]) + " rx2 files and ")

class SessionStates():
    def __init__(self):
        self.allow_config = Event()
        self.allow_start = Event()
        self.allow_stop = Event()
        self.allow_deinit = Event()
        self.allow_end = Event()
    
    def set(self, status):
        if (status == 0x00):
            # SESSION_STATE_INIT
            self.allow_config.set()
            self.allow_start.clear()
            self.allow_stop.clear()
            self.allow_deinit.set()
            self.allow_end.clear()
        
        if (status == 0x01):
            # SESSION_STATE_DEINIT
            self.allow_config.clear()
            self.allow_start.clear()
            self.allow_stop.clear()
            self.allow_deinit.clear()
            self.allow_end.set()
        
        if (status == 0x02):
            # SESSION_STATE_ACTIVE
            self.allow_config.clear()       # To force the stop of ranging before rewrite APP Configs
            self.allow_start.clear()
            self.allow_stop.set()
            self.allow_deinit.clear()       # To wait back to Idle state before deinit
            self.allow_end.clear()
        
        if (status == 0x03):
            # SESSION_STATE_IDLE
            self.allow_config.set()
            self.allow_start.set()
            self.allow_stop.clear()
            self.allow_deinit.set()
            self.allow_end.clear()
        
        if (status == 0xFF):
            # SESSION_ERROR
            self.allow_config.clear()
            self.allow_start.clear()
            self.allow_stop.clear()
            self.allow_deinit.clear()
            self.allow_end.clear()
    
    def set_all(self):
        self.allow_config.set()
        self.allow_start.set()
        self.allow_stop.set()
        self.allow_deinit.set()
        self.allow_end.set()

session_states = SessionStates()

class SIGINThandler():
    def __init__(self):
        self.sigint = False
    
    def signal_handler(self, signal, frame):
        print("You pressed Ctrl+C!")
        self.sigint = True

def write_to_serial_port(uart_interface):
    usb_out_packet = bytearray()
    output("Write to serial port started", uart_interface)
    while (not uart_interface.stop_write_thread):
        if (uart_interface.retry_cmd):
            uart_interface.retry_cmd = False
        else:
            uci_command = uart_interface.command_queue.get()
        
        if (uci_command[0] == 0xFF and uci_command[1] == 0xFF):
            break
        
        if (uci_command[0] == 0xFF and uci_command[1] == 0x00):
            time.sleep(uci_command[2])
            continue
            
        usb_out_packet.clear()
        usb_out_packet.append(0x01)
        usb_out_packet.append(int(len(uci_command) / 256))
        usb_out_packet.append(len(uci_command) % 256)
        usb_out_packet.extend(uci_command)
        if (uci_command[0] == 0x01):
            session_states.allow_stop.wait()
        if (uci_command[0] == 0x22 and uci_command[1] == 0x00):
            # Wait Session State Idle to start ranging
            session_states.allow_start.wait()           
            # Reset stop event
            uart_interface.go_stop.clear()
        
        if (uci_command[0] == 0x22 and uci_command[1] == 0x01):
            # Wait Session State Active
            session_states.allow_stop.wait()           
            # Wait reach number of measures to stop ranging
            uart_interface.go_stop.wait()
        
        if (uci_command[0] == 0x21 and uci_command[1] == 0x00):
            uart_interface.last_session_started = uci_command[4:8]
        if (uci_command[0] == 0x21 and uci_command[1] == 0x01):
            # Wait Session State Init or Idle
            session_states.allow_deinit.wait()
            
        uart_interface.write_wait.acquire()                          # Acquire Lock to avoid mixing in output
        if uart_interface.serial_port.isOpen():
            if (uart_interface.is_timestamp):
                output(datetime.now().isoformat(sep=" ", timespec="milliseconds") + " NXPUCIX => " + \
                      usb_out_packet[3:].hex(" ").upper(), uart_interface)
            else:
                output("NXPUCIX => " + usb_out_packet[3:].hex(" ").upper(), uart_interface)
            
            try:
                uart_interface.serial_port.write(serial.to_bytes(usb_out_packet))
            except:
                output("Fail to write on serial port", uart_interface)
            
            # Wait the reception of RSP or timeout of 0.25s before allowing send of new CMD
            notified = uart_interface.write_wait.wait(0.25)  
            if (not (notified)): 
                uart_interface.retry_cmd = True     # Repeat command if timeout
        uart_interface.write_wait.release()
    
    output("Write to serial port exited", uart_interface)


def read_from_serial_port(uart_interface): 
    global meas_idx
    global txt_name
    global cir_data
    range_data = bytearray()
    meas_nlos = 0
    meas_distance = 0
    meas_azimuth = 0
    meas_azimuth_fom = 0
    meas_elevation = 0
    meas_elevation_fom = 0
    meas_dest_azimuth = 0
    meas_dest_elevation = 0
    meas_rssi = 0
    meas_pdoa1 = 0
    meas_pdoa2 = 0
    avg_window_size = 10
    hist_distance = []
    hist_azimuth = []
    hist_elevation = []
    hist_dest_azimuth = []
    hist_dest_elevation = []
    rframe_session = ""
    rframe_nb = 0
    rframe_meas = bytearray()
    invalid_header = 0
    myString = []
    
    output("Read from serial port started", uart_interface)
    while (not uart_interface.stop_read_thread):
        if uart_interface.serial_port.isOpen():
            uci_hdr = uart_interface.serial_port.read(4)    # Read header of UCI frame
            uart_interface.write_wait.acquire()             # Acquire Lock to avoid mixing in output
            if len(uci_hdr) == 4:
                # Reset invalid header counter
                invalid_header = 0
                
                count = uci_hdr[3]
                if ((uci_hdr[1] & 0x80) == 0x80 or uci_hdr[0] == 0x02):
                    # Extended length
                    count = int((uci_hdr[3] << 8) + uci_hdr[2])
                if count > 0:
                    if uart_interface.serial_port.isOpen():
                        uci_payload = uart_interface.serial_port.read(count)    # Read payload of UCI frame
                        if (uart_interface.is_timestamp):
                            is_stored = output(datetime.now().isoformat(sep=" ", timespec="milliseconds") + \
                                    " NXPUCIR <= " + uci_hdr.hex(" ").upper() + " " + uci_payload.hex(" ").upper(), uart_interface)
                        else:
                            is_stored = output("NXPUCIR <= " + uci_hdr.hex(" ").upper() + " " + \
                                    uci_payload.hex(" ").upper(), uart_interface)
                        if len(uci_payload) == count:
                            if (uci_hdr[0] & 0xF0) == 0x40: uart_interface.write_wait.notify()      # Notify the reception of RSP
                            if (uart_interface.session_handle_flag == True):
                                if (uci_hdr[0] == 0x41 and uci_hdr[1] == 0x00):
                                    #uart_interface.session_handle =  uci_hdr[0:4] # temp value before session handle available
                                    uart_interface.session_handle =  uci_payload[1:]
                                    # Search in each command in the queue to replce Session ID to Session handle
                                    for command in uart_interface.command_queue.queue:
                                        if (command[0] == 0x21 or command[0] == 0x22 or (command[0] == 0x2F and command[1] == 0x00) or command[0] == 0x2D ):
                                            # If several session are in the list, on update the session handle to the corresponding session
                                            if(uart_interface.last_session_started == command[4:8]):
                                                command[4]= uart_interface.session_handle[0]
                                                command[5]= uart_interface.session_handle[1]
                                                command[6]= uart_interface.session_handle[2]
                                                command[7]= uart_interface.session_handle[3]
                            if (uci_hdr[0] == 0x60 and uci_hdr[1] == 0x07 and uci_hdr[3] == 0x01 and \
                                    uci_payload[0] == 0x0A):
                                uart_interface.write_wait.notify()
                                # Command retry without wait response
                                uart_interface.retry_cmd = True
                            if (uci_hdr[0] == 0x61 and uci_hdr[1] == 0x02 and uci_hdr[3] == 0x06):
                                # Change Session state
                                session_states.set(uci_payload[4])
                                
                                if (uci_payload[5] == 0x01):
                                    # Session termination on max RR Retry
                                    uart_interface.go_stop.set()
                                
                                elif (uci_payload[5] == 0x02):
                                    # Session termination on max number of measurements
                                    uart_interface.go_stop.set()
                                
                                elif (uci_payload[5] == 0x83):
                                    # Session termination on inband signal
                                    uart_interface.go_stop.set()

                                if (uart_interface.is_cir_plot):
                                    # Number of Rframe measurements
                                    uart_interface.cir_plot["nb_meas"] = rframe_nb
                                    
                                    # Delete previous Rframe measurements
                                    uart_interface.cir_plot["mappings"] = []
                                    uart_interface.cir_plot["cir_samples"] = []
                                    
                                    idx = 0
                                    for rframe_meas_idx in range(0, rframe_nb):
                                        uart_interface.cir_plot["mappings"].append(rframe_meas[idx])
                                        idx += 27
                                        uart_interface.cir_plot["cir_samples"].append(extract_cir(rframe_meas[idx:idx + 64]))
                                        idx += 64
                                
                                rframe_session = ""
                                rframe_nb = 0
                                rframe_meas.clear()
                            
                            if (uci_hdr[0] == 0x72 and uci_hdr[1] == 0x00):
                                # RANGE_DATA_NTF with PBF = 1
                                
                                # Concat segment
                                range_data.extend(uci_payload)
                            if (uci_hdr[0] == 0x62 and uci_hdr[1] == 0x00):
                                # RANGE_DATA_NTF
                                
                                range_data.extend(uci_payload);
                                
                                seq_cnt = extract_seq_cnt(range_data)
                                if (uci_hdr[3] > 0x1B ):
                                    # Check Status
                                    if (range_data[27] != 0x00 and range_data[27] != 0x1b):
                                        output("***** Ranging Error Detected ****", uart_interface)
                                        
                                        if (uart_interface.is_range_plot):
                                            # Store range data for plot
                                            uart_interface.range_plot["index"] = seq_cnt
                                            uart_interface.range_plot["valid"] = False
                                            uart_interface.range_plot["nlos"] = 0
                                            uart_interface.range_plot["distance"] = 0
                                            uart_interface.range_plot["azimuth"] = 0
                                            uart_interface.range_plot["elevation"] = 0
                                            uart_interface.range_plot["avg_azimuth"] = 0
                                            uart_interface.range_plot["avg_elevation"] = 0
                                            uart_interface.range_plot["dest_azimuth"] = 0
                                            uart_interface.range_plot["dest_elevation"] = 0
                                            uart_interface.range_plot["dest_avg_azimuth"] = 0
                                            uart_interface.range_plot["dest_avg_elevation"] = 0
                                    else:
                                        meas_nlos = (extract_nlos(range_data))
                                        meas_distance = (extract_distance(range_data))
                                        if (range_data[27] == 0x1b):
                                            meas_distance *= -1
                                        meas_azimuth = convert_qformat_to_float(extract_azimuth(range_data), 9, 7, 1)
                                        meas_azimuth_fom = (extract_azimuth_fom(range_data))
                                        meas_elevation = convert_qformat_to_float(extract_elevation(range_data), 9, 7, 1)
                                        meas_elevation_fom = (extract_elevation_fom(range_data))
                                        meas_dest_azimuth = convert_qformat_to_float(extract_dest_azimuth(range_data), 9, 7, 1)
                                        meas_dest_elevation = convert_qformat_to_float(extract_dest_elevation(range_data), 9, 7, 1)
                                        meas_rssi = extract_rssi(range_data) * -0.5
                                        meas_pdoa1 = convert_qformat_to_float(extract_pdoa1(range_data), 9, 7, 7)
                                        meas_pdoa2 = convert_qformat_to_float(extract_pdoa2(range_data), 9, 7, 7)
                                        hist_distance.append(meas_distance)
                                        hist_azimuth.append(meas_azimuth)
                                        hist_elevation.append(meas_elevation)
                                        hist_dest_azimuth.append(meas_dest_azimuth)
                                        hist_dest_elevation.append(meas_dest_elevation)
                                        
                                        if (len(hist_distance) > avg_window_size): hist_distance.pop(0)
                                        if (len(hist_azimuth) > avg_window_size): hist_azimuth.pop(0)
                                        if (len(hist_elevation) > avg_window_size): hist_elevation.pop(0)
                                        if (len(hist_dest_azimuth) > avg_window_size): hist_dest_azimuth.pop(0)
                                        if (len(hist_dest_elevation) > avg_window_size): hist_dest_elevation.pop(0)
                                        
                                        avg_distance = sum(hist_distance) / len(hist_distance)
                                        avg_azimuth = sum(hist_azimuth) / len(hist_azimuth)
                                        avg_elevation = sum(hist_elevation) / len(hist_elevation)
                                        avg_dest_azimuth = sum(hist_dest_azimuth) / len(hist_dest_azimuth)
                                        avg_dest_elevation = sum(hist_dest_elevation) / len(hist_dest_elevation)
                                        
                                        output("***(%d) NLos:%d   Dist:%d   Azimuth:%.1f (FOM:%d)   Elevation:%.1f (FOM:%d)" \
                                            % (seq_cnt, meas_nlos, meas_distance, meas_azimuth, meas_azimuth_fom, meas_elevation, meas_elevation_fom), uart_interface)
                                        output("***    RSSI:%.1f    PDoA1:%f   PDoA2:%f"\
                                            % (meas_rssi, meas_pdoa1, meas_pdoa2), uart_interface)
                                        output("***    Avg Dist:%d   Avg Azimuth:%.1f   Avg Elevation:%.1f" \
                                            % (avg_distance, avg_azimuth, avg_elevation), uart_interface)
                                        #output("***    Dest Azimuth:%.1f (Avg:%.1f)   Dest Elevation:%.1f (Avg:%.1f)" \
                                        #    % (meas_dest_azimuth, avg_dest_azimuth, meas_dest_elevation, avg_dest_elevation), uart_interface)
                                        
                                        #write measurements into log file
                                        global log_file
                                        if log_file is not None:
                                            log_file.write(f"{datetime.now().isoformat()},{seq_cnt},{meas_nlos},{meas_distance},{meas_azimuth},{meas_elevation},{meas_azimuth_fom},{meas_elevation_fom},{meas_rssi},{meas_pdoa1},{meas_pdoa2}\n")
                                            log_file.flush()

                                        if (uart_interface.is_range_plot):
                                            # Store range data for plot
                                            uart_interface.range_plot["index"] = seq_cnt
                                            uart_interface.range_plot["valid"] = True
                                            uart_interface.range_plot["nlos"] = meas_nlos
                                            uart_interface.range_plot["distance"] = meas_distance
                                            uart_interface.range_plot["azimuth"] = meas_azimuth
                                            uart_interface.range_plot["elevation"] = meas_elevation
                                            uart_interface.range_plot["avg_azimuth"] = avg_azimuth
                                            uart_interface.range_plot["avg_elevation"] = avg_elevation
                                            uart_interface.range_plot["dest_azimuth"] = meas_dest_azimuth
                                            uart_interface.range_plot["dest_elevation"] = meas_dest_elevation
                                            uart_interface.range_plot["avg_dest_azimuth"] = avg_dest_azimuth
                                            uart_interface.range_plot["avg_dest_elevation"] = avg_dest_elevation
                                    
                                        # Increment the number of valid measurements
                                        meas_idx += 1
                                        
                                        if (uart_interface.nb_meas > 0 and meas_idx > uart_interface.nb_meas):
                                            uart_interface.go_stop.set()
                                    
                                    range_data.clear()
                              
                            if (uci_hdr == UWB_EXT_READ_CALIB_DATA_TX_POWER_NTF):
                                # Search in each command in the queue to replce OTP read values
                                for command in uart_interface.command_queue.queue:
                                    if (command[0] == 0x2F and command[1] == 0x21 and command[5] == 0x04):
                                        command[11] = uci_payload[2] + uart_interface.power_offset + int((2.1-0.6+0.5)*4) # Murata EVK case: ANT+2.1dBi, trace loss 0.6dB 
                                        command[9] = uci_payload[3]
                                        #command[16] = uci_payload[4] + uart_interface.power_offset + int((2.1-0.6+0.5)*4)
                                        #command[14] = uci_payload[5]

                            if (uci_hdr == UWB_EXT_READ_CALIB_DATA_XTAL_CAP_NTF):
                                # Search in each command in the queue to replce OTP read values
                                for command in uart_interface.command_queue.queue:
                                    if (command[0] == 0x2F and command[1] == 0x21 and command[5] == 0x01):
                                        command[8]= uci_payload[2]
                                        command[10]= uci_payload[3]
                                        command[12]= uci_payload[4]
  
                        else:
                            output("\nExpected Payload bytes is " + str(count) + \
                                    ", Actual Paylod bytes received is " + str(len(uci_payload)), uart_interface)
                    else:
                        output("Port is not opened", uart_interface)
                else:
                    output("\nUCI Payload Size is Zero", uart_interface)
            else:
                # Increament invalid header counter
                invalid_header += 1
                if session_states.allow_stop.isSet() == False:
                    if (invalid_header > MAX_RETRY_NUMBER):
                        # Stop all threads
                        session_states.allow_end.set()
                    output("\nUCI Header is not valid", uart_interface)                    
            uart_interface.write_wait.release()
        else:
            output("Port is not opened (2)", uart_interface)    
    if uart_interface.serial_port.isOpen(): uart_interface.serial_port.close()
    
    output("Read from serial port exited", uart_interface)

def serial_port_configure(uart_interface, com_port):
    
    uart_interface.serial_port.baudrate = BAUDRATE
    uart_interface.serial_port.timeout = 1                 # To avoid endless blocking read
    uart_interface.serial_port.port = com_port
    
    if uart_interface.serial_port.isOpen(): uart_interface.serial_port.close()
    
    try:
        uart_interface.serial_port.open()
    except:
        output("#=> Fail to open " + com_port, uart_interface)

        sys.exit(1)

# Output string on STDOUT or store into file depending of IPC mode
# Return True is success to write string into file
def output(string, uart_interface):
    # Output string on STDOUT
    try:
        print(string)
    except:
        # Catch error in case pipe is closed
        pass 
    return False


def extract_seq_cnt(byte_array):
    return int((byte_array[3] << 24) + (byte_array[2] << 16) + (byte_array[1] << 8) + byte_array[0])


def extract_nlos(byte_array):
    return int(byte_array[28])


def extract_distance(byte_array):
    return int((byte_array[30] << 8) + byte_array[29])


def extract_azimuth(byte_array):
    return int((byte_array[32] << 8) + byte_array[31])


def extract_azimuth_fom(byte_array):
    return int(byte_array[33])


def extract_elevation(byte_array):
    return int((byte_array[35] << 8) + byte_array[34])


def extract_elevation_fom(byte_array):
    return int(byte_array[36])


def extract_dest_azimuth(byte_array):
    return int((byte_array[38] << 8) + byte_array[37])


def extract_dest_elevation(byte_array):
    return int((byte_array[41] << 8) + byte_array[40])


def extract_pdoa1(byte_array):
    return int((byte_array[71] << 8) + byte_array[70])
    
    
def extract_pdoa2(byte_array):
    return int((byte_array[77] << 8) + byte_array[76])


def extract_rssi(byte_array):
    return int(byte_array[44])


def extract_cir(byte_array):
    cir_raw = []
    
    for idx in range(0, len(byte_array), 4):
        cir_sample = byte_array[idx:idx + 4]
        
        real = twos_comp((cir_sample[1] << 8) + cir_sample[0], 16)
        imaginary = twos_comp((cir_sample[3] << 8) + cir_sample[2], 16)
        
        cir_raw.append(complex(real, imaginary))
    
    return np.abs(cir_raw)

def twos_comp(val, bits):
    # Compute the 2's complement of integer val with the width of bits
    if (val & (1 << (bits - 1))) != 0:           # If sign bit is set
        val = val - (1 << bits)                  # Compute negative value
    return val

def convert_qformat_to_float(q_in, n_ints, n_fracs, round_of=2):
    bits = n_ints + n_fracs
    
    # Compute the 2's complement of integer q_in with the width of n_ints + n_fracs
    if (q_in & (1 << (bits - 1))) != 0:          # If sign bit is set
        q_in = q_in - (1 << bits)                # Compute negative value
    
    # Divide by 2^n_fracs
    frac = q_in / (1 << n_fracs)
    
    # Return rounded value
    return round(frac, round_of)

def deg_to_rad(angle_deg):
    return (angle_deg * np.pi / 180)

def draw_distance(plot_dist, data):
    if (data["index"] == 0):
        # Clear plot and restore X axis
        plot_dist.lines.clear()
        plot_dist.set_xlim(1, 100)
    
    # Slide X axis when reach the right border
    xmin, xmax = plot_dist.get_xlim()
    
    if (data["index"] > xmax):
        plot_dist.set_xlim(data["index"] - 100, data["index"])
    
    # Increase Y axis if distance is greater than the max
    ymin, ymax = plot_dist.get_ylim()
    
    if (data["distance"] > ymax):
        plot_dist.set_ylim(0, data["distance"] + 50)
    
    # Set the color of the point
    if (data["nlos"] == 0):
        # LoS => point marker, blue
        coloredPoint = ".b"
    else:
        # NLoS or invalid => point marker, red
        coloredPoint = ".r"
    
    plot_dist.plot(data["index"], data["distance"], coloredPoint)

    
def draw_aoa(plot_aoa, angle, avg, dest_draw=False, dest_angle=0, dest_avg=0):
    # Remove previous arrow and cicle
    plot_aoa.lines.clear()
    
    # Draw new arrow (solid line style, blue)
    plot_aoa.plot([0, deg_to_rad(angle), deg_to_rad(angle - 10), deg_to_rad(angle),
                   deg_to_rad(angle + 10), deg_to_rad(angle)],
                  [0, 0.95, 0.9, 1, 0.9, 0.95], "-b")
    
    # Draw new cicle marker, blue
    plot_aoa.plot(deg_to_rad(avg), 1, "ob")

    if (dest_draw):
        # Draw new arrow (solid line style, green)
        plot_aoa.plot([deg_to_rad(dest_angle - 10), deg_to_rad(dest_angle), deg_to_rad(dest_angle + 10)],
                      [1, 0.8, 1], "-g")
        
        # Draw new cicle marker, green
        plot_aoa.plot(deg_to_rad(dest_avg), 1, "og")


def draw_cir(plot_cir, data):
    # Remove previous lines
    plot_cir.lines.clear()
    
    coloredLine = ""
    legend = ""
    
    # Store slot index of first measurement
    first_slot = data["mappings"][0] & 0x3F
    
    for data_idx in range(0, data["nb_meas"]):
        slot = data["mappings"][data_idx] & 0x3F
        
        # Set the style of the line
        if (slot == first_slot):
            # Solid line
            coloredLine = "-"
        else:
            # Dashed line
            coloredLine = "--"
        
        legend = "Slot "
        legend += format(slot)
        
        # Set the color of the line
        if (data["mappings"][data_idx] >= 128):
            # RX2 => Red
            coloredLine += "r"
            legend += " RX2"
        else:
            # RX1 => Green
            coloredLine += "g"
            legend += " RX1"
        
        plot_cir.plot(range(-8, 8), data["cir_samples"][data_idx], coloredLine, label=legend)
        plot_cir.legend(loc="upper left")


def init_plots(uart_interface):
    
    plt.ion()  # Interactive mode
    plt.rcParams["toolbar"] = "None"  # Remove toolbar
    
    # Define figure of all plots
    fig = plt.figure()
    fig.subplots_adjust(wspace=0.4, hspace=0.6)
    
    if (uart_interface.is_cir_plot):
        nb_row = 3
    else:
        nb_row = 2
    
    # Define distance plot
    plot_dist = fig.add_subplot(nb_row, 2, (1, 2))
    plot_dist.clear()
    plot_dist.set_title("Distance")
    plot_dist.set_xlabel("Sample #")
    plot_dist.set_xlim(1, 100)
    plot_dist.set_ylabel("cm")
    plot_dist.set_ylim(0, 1000)
    
    # Define Azimuth plot
    plot_azimuth = fig.add_subplot(nb_row, 2, 3, polar=True)
    plot_azimuth.clear()
    plot_azimuth.set_xlabel("Azimuth")
    plot_azimuth.set_theta_zero_location("N")
    plot_azimuth.set_theta_direction("clockwise")
    plot_azimuth.set_thetalim(deg_to_rad(-90), deg_to_rad(90))
    plot_azimuth.set_xticks([deg_to_rad(-90), deg_to_rad(-60), deg_to_rad(-30), 0,
                             deg_to_rad(30), deg_to_rad(60), deg_to_rad(90)])
    plot_azimuth.set_ylim(0, 1)
    plot_azimuth.set_yticks([])
    
    # Define Elevation plot
    plot_elevation = fig.add_subplot(nb_row, 2, 4, polar=True)
    plot_elevation.clear()
    plot_elevation.set_xlabel("Elevation")
    plot_elevation.set_theta_zero_location("E")
    plot_elevation.set_theta_direction("counterclockwise")
    plot_elevation.set_thetalim(deg_to_rad(-90), deg_to_rad(90))
    plot_elevation.set_xticks([deg_to_rad(-90), deg_to_rad(-60), deg_to_rad(-30), 0,
                               deg_to_rad(30), deg_to_rad(60), deg_to_rad(90)])
    plot_elevation.set_ylim(0, 1)
    plot_elevation.set_yticks([])
    
    if (nb_row == 3):
        # Define CIR plot
        plot_cir = fig.add_subplot(nb_row, 2, (5, 6))
        plot_cir.clear()
        plot_cir.set_title("Amplitude")
        plot_cir.set_xlabel("First Path Index")
        plot_cir.set_xlim(-8, 7)
        plot_cir.set_xticks(range(-8, 8, 2))
        plot_cir.set_ylim(0, 3000)
    else:
        plot_cir = None
    
    plt.show()  # Not blocking as Interactive mode
    plt.pause(0.01)  # Run the GUI event loop 10ms to draw the plots
    
    # Return plots for reference when drawing
    return (plot_dist, plot_azimuth, plot_elevation, plot_cir)

def start_processing(uart_interface):
    # Initialize plots
    if (uart_interface.is_range_plot):
        plot_dist, plot_azimuth, plot_elevation, plot_cir = init_plots(uart_interface)
    
    read_thread = Thread(target=read_from_serial_port, args=(uart_interface,))
    read_thread.start()
    
    uart_interface.stop_write_thread = False
    uart_interface.stop_read_thread = False
    write_thread = Thread(target=write_to_serial_port, args=(uart_interface,))
    write_thread.start() 
    
    handler = SIGINThandler()
    signal.signal(signal.SIGINT, handler.signal_handler)
    
    while (session_states.allow_end.is_set() == False):
        if handler.sigint:
            break
        
        if ((uart_interface.is_range_plot) and (plt.get_fignums())): # Check if figure is still open
            if (uart_interface.range_plot["index"] >= 0):
                # Plot new range data
                draw_distance(plot_dist, uart_interface.range_plot)
                draw_aoa(plot_azimuth, uart_interface.range_plot["azimuth"], uart_interface.range_plot["avg_azimuth"], \
                         True, uart_interface.range_plot["dest_azimuth"], uart_interface.range_plot["avg_dest_azimuth"])
                draw_aoa(plot_elevation, uart_interface.range_plot["elevation"], uart_interface.range_plot["avg_elevation"], \
                         True, uart_interface.range_plot["dest_elevation"], uart_interface.range_plot["avg_dest_elevation"])
                
                # Disable range data
                uart_interface.range_plot["index"] = -1
            
            if ((uart_interface.is_cir_plot) and (uart_interface.cir_plot["nb_meas"] > 0)):
                # Plot new rframe data
                draw_cir(plot_cir, uart_interface.cir_plot)
                
                # Disable rframe data
                uart_interface.cir_plot["nb_meas"] = 0
            
            # Update figure
            plt.draw()
            plt.pause(0.001)
        
    # End of processing
    uart_interface.stop_write_thread = True
    uart_interface.stop_read_thread = True
    uart_interface.stop_ipc_thread = True
    
    # Unblock the waiting in the write thread
    uart_interface.command_queue.put([0xFF, 0xFF])                   # End of write
    session_states.set_all()
    uart_interface.go_stop.set()
    
    # Close figure
    if (uart_interface.is_range_plot):
        plt.close('all')
        uart_interface.range_plot["index"] = -1

