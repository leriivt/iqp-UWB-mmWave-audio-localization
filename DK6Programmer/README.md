use the DK6Programmer to flash the 2BPs

run: (make sure to change the COM port to the correct number)
```bash
.\DK6Programmer.exe -V 0 -P 1000000 -s COM12 -Y -p <BINARY_FILE_TO_BE_FLASHED>
```

pnp3MFW_Rhodes4_SR150-v04.08.01.bin file should flash the boards for pnp mode needed for calibration and directly found in the Rhodes SDK

RhodesV4_SE.bin was built using the MCUXpresso IDE while uncommenting the PNP demo line in UWBIOT_APP_BUILD.h, after applying the patch found in Type2BP_SDK_UWBIOT_SR150_v04.08.01_MCUx. (might not work as well)
