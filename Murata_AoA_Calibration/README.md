# Murata AoA calibration guide
## 1. Open Windows Powershell
## 2. Clone this repository
Run the following in Windows Powershell:
```bash
git clone git@github.com:leriivt/iqp-UWB-mmWave-audio-localization.git
```
## 3. Enter the Murata_AoA_Calibration directory
```bash
cd ~/iqp-UWB-mmWave-audio-localization/Murata_AoA_Calibration
```
## 4. Flash relevant UWB boards
To do AoA calibration, you will need to flash both UWB boards with the PnP (Plug-and-Play) firmware provided by Murata. To do this you will need to use DK6Programmer.exe and the relevant binary file found in the DK6Programmer directory.

Enter the DK6Programmer directory:
```bash
cd DK6Programmer
```
