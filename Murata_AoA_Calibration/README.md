# Murata AoA calibration guide
## 0. Pre-reqs:
Install Python: https://www.python.org/downloads/
## 1. Clone this repository
Run the following in Windows Powershell:
```bash
git clone git@github.com:leriivt/iqp-UWB-mmWave-audio-localization.git
```
## 2. Enter the Murata_AoA_Calibration directory
```bash
cd ~/iqp-UWB-mmWave-audio-localization/Murata_AoA_Calibration
```
## 2. Install FTDI Drivers
Run
```bash
./CDM2123620_Setup.exe
```
## 4. Flash relevant UWB boards
To do AoA calibration, you will need to flash both UWB boards with the PnP (Plug-and-Play) firmware provided by Murata. To do this you will need to use DK6Programmer.exe and the relevant binary file found in the DK6Programmer directory.

Enter the DK6Programmer directory:
```bash
cd DK6Programmer
```

Plug your laptop into the UWB board.

Check the COM port of the UWB board by searching "device manager" in Windows start and open the application.

Should see the COM port listed under the Ports section




## 5. Running the measurement gathering code
The python files that you need to run can be found in
