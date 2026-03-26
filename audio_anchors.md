# how to setup rpis to do localization w/audio

- ssh into rpi

- cd into the uwb-localization-mesh directory

- run the following command to do localization and audio at the same time:
  ```bash
  uv run python Anchor_bring_up.py --anchor-id 0 --broker <YOUR_LAPTOP_IP> & uv run python packages/audio_mqtt_client/synchronized_audio_player_rpi.py --id 0 --broker <YOUR_LAPTOP_IP>
  ```
