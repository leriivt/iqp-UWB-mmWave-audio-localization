# Running mmWave.py on Raspberry Pi
## 1. Connect to the EDIC wifi
## 2. SSH into RPI with X11 forwarding enabled (the -X)
(make sure to start your X server if not on Linux; ie. Xming through XLaunch)

`ssh -X rpi0@wpiuwb`

the raspberry pi password is `wpiuwb`

If on Windows, make sure to point the DISPLAY variable to Xming (or whatever X server you are using)

Run:
`export DISPLAY=<YOUR_PC_IP>:0.0`
## 3. Make sure the necessary libraries are installed
To make venv:
`python3 -m venv ~/venvs/MS72SF1`

To activate venv:
`source ~/venvs/MS72SF1/bin/activate`

Install necessary libraries:
`pip install Pillow matplotlib psutil pyserial`
## 4. Go do directory where mmWave.py is located and run
`cd ~/iqp-UWB-mmWave-audio-localization/mmWave/60GHz_MS72SF1/dev_tools/MinewSemi_MS72SF1_Host_Source_Code/mmWave`

`python3 mmWave.py`



## If the graphical inferface isn't showing up on your local machine...
X11 forwarding might not be enabled on the raspberry pi
```bash
sudo nano /etc/ssh/sshd_config
```
Make sure these lines are present and uncommented:
```bash
X11Forwarding yes
X11DisplayOffset 10
```

Then restart ssh:
```bash
sudo systemctl restart ssh
```

