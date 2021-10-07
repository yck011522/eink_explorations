# eink_explorations
Having some fun with waveshare 7.5inch e-ink panel and Raspberry Pi

# Hardware

## Raspberry Pi 3 Model B+ Revision03

https://www.raspberrypi.org/products/raspberry-pi-3-model-b-plus/

- Broadcom BCM2837B0, Cortex-A53 (ARMv8) 64-bit SoC @ 1.4GHz
- 1024MB LPDDR2 SDRAM
- 2.4GHz and 5GHz IEEE 802.11.b/g/n/ac wireless LAN, Bluetooth 4.2, BLE
- Full-size HDMI (Good for debug / dev monitor)
- Power supply: +5 V @ 2.5 A via microUSB jack
- Dimensions: 85 x 56 x 17 mm
- 4 USB 2.0 ports

### Dimensions

![raspberry_pi_model_b_plus_dimentions](references/raspberry_pi_model_b_plus_dimentions.png)

### Pin Out

![raspberry_pi_model_b_plus_gpio](references/raspberry_pi_model_b_plus_gpio.png)

### RPi Installation guide:

[Installing OS on RPi](https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up)

[Setting up a Raspberry Pi WiFi headless](https://www.raspberrypi.org/documentation/configuration/wireless/headless.md) (`wpa_supplicant.conf` in boot)

[Enabling SSH on Raspberry Pi Without a Screen](https://linuxize.com/post/how-to-enable-ssh-on-raspberry-pi/) (empty file named `ssh` in boot)

### Finding RPi in Network

[Using MMAP to find the RPi on same network](https://www.raspberrypi.org/documentation/remote-access/ip-address.md) (`nmap -sn 192.168.88.0/24`)

Connect via SSH:  `ssh pi@192.168.88.63`

The default user is **pi** , and the password is **~~raspberry~~** .

[Keep RPi connected to WiFi](https://francisuniverse.wordpress.com/2018/01/07/how-to-automatically-reconnect-raspberry-pi-to-wifi/) (Following the second method by installing `ifplugd` )

```
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

In the following format:

```
network={
    ssid="HomeOneSSID"
    psk="passwordOne"
    priority=1
    id_str="homeOne"
}

network={
    ssid="HomeTwoSSID"
    psk="passwordTwo"
    priority=2
    id_str="homeTwo"
}
```



### Linux Commands

List USB Devices: `lsusb `

System Log: `dmesg`





## Waveshare 800 x 480 RBW tricolour 7.5 inch e-ink panel

[7.5inch E-Paper E-Ink Display HAT (B) For Raspberry Pi, 800×480, Red / Black / White, SPI](https://www.waveshare.com/product/displays/e-paper/epaper-1/7.5inch-e-paper-hat-b.htm)

![7.5inch-e-Paper-HAT-B-details-3](references/7.5inch-e-Paper-HAT-B-details-3.jpg)

- power supply 3.3V/5V
- 3-wire SPI, 4-wire SPI
- external dimension 170.2 × 111.2mm
- Display size 163.2 × 97.92mm
- Dot Pitch 0.205 × 0.204mm
- Greyscale 2
- Refresh 16s

### Dimension

![7.5inch-e-Paper-B-details-size](references/7.5inch-e-Paper-B-details-size.jpg)

![e-Paper-Driver-HAT-details-size](references/e-Paper-Driver-HAT-details-size.jpg)

### Library Setup Guide

[e-paper hat wiki](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_(B))

```
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.60.tar.gz
tar zxvf bcm2835-1.60.tar.gz 
cd bcm2835-1.60/
sudo ./configure
sudo make
sudo make check
sudo make install
```

Install library for using Rpi GPIO

```
sudo apt-get install wiringpi
cd /tmp
wget https://project-downloads.drogon.net/wiringpi-latest.deb
sudo dpkg -i wiringpi-latest.deb
gpio -v
```

Install Python Dependency and Git

```
#python3
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install python3-pil
sudo apt-get install python3-numpy
sudo pip3 install RPi.GPIO
sudo pip3 install spidev
sudo apt-get install git -y
```

Update Pillow to latest version (Has more drawing effects)

```
python3 -m pip install --upgrade Pillow
```

Clone Waveshare Examples and E-Ink Library. 

```
# Examples Python
sudo git clone https://github.com/waveshare/e-Paper

cd /e-Paper/RaspberryPi_JetsonNano/python/examples/
sudo python3 epd_7in5b_V2_test.py
```

The e-ink library at `/e-Paper/RaspberryPi_JetsonNano/python/lib`is not installed into the python path, but dynamically added to `sys.path` when the actual file is run:

```
import os
import sys
libdir = "/e-Paper/RaspberryPi_JetsonNano/python/lib"
if os.path.exists(libdir):
    sys.path.append(libdir)
from waveshare_epd import epd7in5b_V2
```

### Case Design

RPi 3 B 3D Model

https://grabcad.com/library/raspberry-pi-3-model-b-reference-design-solidworks-cad-raspberry-pi-raspberrypi-rpi-1

# Software 

## Coding and editing via VSCode

[Guide for setting up VSCode to connect remotely to RPi](https://www.raspberrypi.org/blog/coding-on-raspberry-pi-remotely-with-visual-studio-code/) (Install **Remote Development** extension)

[Workaround](https://stackoverflow.com/a/65156180/3199029) - Changing the repo folder for SSH read write permission for default account:``sudo setfacl -R -m u:pi:rwx ~/eink_explorations/ ``

## Functional Python Example File

https://github.com/waveshare/e-Paper/blob/master/RaspberryPi_JetsonNano/python/examples/epd_7in5_V2_test.py

Python file location

```
cd ~/eink_explorations/src/main.py
```

`waveshare_epd` Library location

```
```

## Task Scheduling

In order to minimize changes to the system configuration as I add more features. All the regularly updated routines are called by `main.py` in the repo which is triggered to [run by cron job](https://www.raspberrypi.org/documentation/linux/usage/cron.md) in a regular 10 minute interval. Actual routines may have a different update frequency (less than the cron frequency) and are managed by `main.py`. These tasks manages its own run / skip with their own logic:

- Fetching weather from online sources (Last successful data fetch > expiry time)
- Drawing and Updating eink display (Within a certain time of the day)

## Cron Setup

The cron setting file is done on the user 'pi' (no `sudo` permissions granted):

````
crontab -e
````

The following line runs `main.py` on reboot and output `stdout` is routed to `log.txt`. 

```
@reboot python3 /home/pi/eink_explorations/src/main.py > /home/pi/eink_explorations/log.txt
```

The following line runs the same file every 10 mins

```
0,59/10 * * * * python3 /home/pi/eink_explorations/src/main.py > /home/pi/eink_explorations/log.txt
```

Last run log can be seen in:

```
nano ~/eink_explorations/log.txt
```

Boot log can be seen in:

```
grep cron /var/log/syslog
```

# Interfacing with Arduino via USB

https://roboticsbackend.com/raspberry-pi-arduino-serial-communication/#Detect_the_Arduino_board

```
python3 -m pip install pyserial
```



# Reading Weather (AccuWeather API)

api key is written in ymal file

Install ymal for python

```
python3 -m pip install  pyyaml
```

