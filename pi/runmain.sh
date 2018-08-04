#! /bin/bash

# start gpsd so that python can access the adafruit GPS breakout over UART.
# There are some additional steps you must follow once, such as downloading gpsd
# and enabling serial communication, but once done should
# not have to be re-done. Everthing is from
# https://learn.adafruit.com/adafruit-ultimate-gps-on-the-raspberry-pi/using-uart-instead-of-usb
sudo systemctl stop serial-getty@ttyS0.service
sudo systemctl disable serial-getty@ttyS0.service
sudo killall gpsd
sudo gpsd /dev/ttyS0 -F /var/run/gpsd.sock

python3 ~/Documents/SmartSeiner/pi/main.py
