#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = "/home/pi/eink_explorations/pic"
libdir = "/e-Paper/RaspberryPi_JetsonNano/python/lib"
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5b_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("epd7in5b_V2 Demo")

    epd = epd7in5b_V2.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    Himage = Image.open(os.path.join(picdir, 'jane_b.bmp'))
    Himage_Other = Image.open(os.path.join(picdir, 'jane_r.bmp'))
    epd.display(epd.getbuffer(Himage),epd.getbuffer(Himage_Other))
    time.sleep(2)

    logging.info("Goto Sleep...")
    epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd7in5b_V2.epdconfig.module_exit()
    exit()
