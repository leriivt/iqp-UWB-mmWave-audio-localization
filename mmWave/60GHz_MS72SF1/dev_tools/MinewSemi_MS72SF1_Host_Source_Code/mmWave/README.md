# Running mmWave.py on Raspberry Pi
# 1. Connect to the EDIC wifi
# 2. SSH into RPI
`ssh rpi0@______`

the raspberry pi password is the same as the hostname
# 3. Make sure the necessary libraries are installed
To make venv:
`python3 -m venv ~/venvs/MS72SF1`

To activate venv:
`source ~/venvs/MS72SF1/bin/activate`

Install necessary libraries:
`pip install Pillow matplotlib psutil`
# 4. Go do directory where mmWave.py is located and run
`cd ~/iqp-UWB-mmWave-audio-localization/mmWave/60GHz_MS72SF1/dev_tools/MinewSemi_MS72SF1_Host_Source_Code/mmWave`

`python3 mmWave.py`
