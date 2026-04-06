# Murata AoA calibration guide
## 0. Pre-reqs:
Install Python: https://www.python.org/downloads/

Make sure the necessary libraries are installed to a virtual environment:

To make venv, open **Windows Powershell** and run:
`python3 -m venv ~/venvs/AoA_calibration`

To activate venv:
`./~/venvs/AoA_calibration/Scripts/Activate.ps1`
>When trying to acitvate the venv you may get an error due to restricted Script exection. If so, run the following and try activating again:
>```bash
>Set-ExecutionPolicy Unrestricted -Scope Process
>```

Install necessary libraries:
`pip zmq pyserial matplotlib numpy pycryptodome PyYAML`
## 1. Clone this repository
Run the following in Windows Powershell:
```bash
git clone https://github.com/leriivt/iqp-UWB-mmWave-audio-localization.git
```

>If you don't have have git installed, you could alternatively download the repo from the web as a zip file or use [VSCode](https://www.jcchouinard.com/git-clone-github-repository-vscode/)
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

**Check the COM port of the UWB board by searching "device manager" in Windows start and open the application.**

Should see the COM port listed under the *Ports* section as *Universal Serial Port*.

run: (make sure to change the COM port to the correct number)
```bash
.\DK6Programmer.exe -V 0 -P 1000000 -s COM12 -Y -p pnp3MFW_Rhodes4_SR150-v04.08.01.bin
```

`pnp3MFW_Rhodes4_SR150-v04.08.01.bin` file should flash the boards for pnp mode needed for calibration and directly found in the Rhodes SDK

Successful flashing ends with the message: `Memory Programmed Sucessfully`

## 5. Running the measurement gathering code
The python files that you need to run can be found in the `/MTD-SCP-144_DS-TWR_SR150_Unicast_v04.06.05_Rev1.0` directory.

```bash
cd ~/iqp-UWB-mmWave-audio-localization/Murata_AoA_Calibration/MTD-SCP-144_DS-TWR_SR150_Unicast_v04.06.05_Rev1.0
```

During calibration there will be an **initiator** and a **responder**. The **initiator** is the board being calibrated (ceiling) and the **responder** is the accompanying board.

For the **initiatior**, run (make sure to replace <COM_NUMBER>):
```bash
python3 MTD-SCP-144_DS-TWR_SR150_Unicast_v040605_Rev1p0.py i <COM_NUMBER> 30
```

For the **responder**, run (make sure to replace <COM_NUMBER>):
```bash
python3 MTD-SCP-144_DS-TWR_SR150_Unicast_v040605_Rev1p0.py r <COM_NUMBER> 30
```

Note: the `30` tells the code to run for 30 valid measurements

The measurements taken by the board during calibration should get stored in CSV files that are labeled in the format `ranging_<role>_<date>_<time>.csv` (ex: `ranging_Initiator_20260406_143022.csv`)

CSVs are stored in `./Murata_AoA_Calibration/MTD-SCP-144_DS-TWR_SR150_Unicast_v04.06.05_Rev1.0/test_data`
