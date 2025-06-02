
python3 /home/pi/.arduino15/packages/esp8266/hardware/esp8266/2.7.1/tools/upload.py --chip esp8266 --port $1 --baud 921600 erase_flash --before default_reset --after hard_reset write_flash 0x0 $2