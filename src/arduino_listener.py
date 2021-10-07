#!/usr/bin/env python3
import serial
import os
import time

def connect_to_usbdevice(name):
    ser = serial.Serial(name, 115200, timeout=1)
    ser.flush()
    print("Serial Available: %s"%ser.name)
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)
            # Trigger screen update if the * key is pressed
            if line.startswith('*'):
                os.system ("python3 /home/pi/eink_explorations/src/main.py >> /home/pi/eink_explorations/keyboard_log.txt")
        else:
            time.sleep(0.1)


# The script will run forever to listen for keyboard input
if __name__ == '__main__':
    while True:
        for usb_name in ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2']:
            print("Trying to connect to: %s" % usb_name)
            try:
                connect_to_usbdevice(usb_name)
            except:
                    # ignore serial errors which may happen if the serial device was
                    # hot-unplugged.
                    time.sleep(1)
                    pass
