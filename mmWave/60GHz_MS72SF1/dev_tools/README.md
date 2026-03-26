# MS72SF1 setup
Refer to the Devlopment Guide, TLDR is as follows:

1. You will need to install a CH340 chip driver for your PC. The CH340 is the chip on the USB to TTL device that you plug into your PC and handles USB to UART communication. The download is found at <https://www.wch.cn/downloads/CH341SER_EXE.html>.
2. You will need to install some sort of serial terminal software to send serial command to the MS72SF1 to configure it. The Development Guide uses SSCOM which is found at www.daxia.com.
3. You will need to use the tell the MS72SF1 to enter learning mode to acquire data from its new environment. To do this send the commands AT+RESTORE\n to restore the module's configuration, then send AT+STUDY\n to enter learning mode. The module will output 55 AA 06 00 B1 B7 if it detects a new environment and will start learning.
4. Wait 10 min (!!!????) for the module to learn.
5. Send AT+RESTORE\n to restore the module. At this point, the environmental information has been saved to flash.
6. Next will need to set height and room environmental conditions:
   |Environmental Condition       |  Command (edit the num)          |
   |------------------------------|----------------------------------|
   | Default Radial Distance:     |  AT+RANGE=300\n                  |
   | Default Installation Height: |  AT+HEIGHT=270\n                 |
   | Default Detection Height:    |  AT+HEIGHTD=270\n                |
   | Set X-Negative Boundary:     |  AT+XNegaD=-300\n                |
   | Set X-Positive Boundary:     |  AT+XPosiD=300\n                 |
   | Set Y-Negative Boundary:     |  AT+YNegaD=-300\n                |
   | Set Y-Positive Boundary:     |  AT+YPosiD=300\n                 |  




