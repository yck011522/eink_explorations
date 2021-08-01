#!/usr/bin/python
# -*- coding:utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import PIL
from datetime import datetime
import traceback
import time
import logging
import os
import sys

picdir = "/home/pi/eink_explorations/pic"
fontdir = "/home/pi/eink_explorations/font"
libdir = "/e-Paper/RaspberryPi_JetsonNano/python/lib"
if os.path.exists(libdir):
    sys.path.append(libdir)
    from waveshare_epd import epd7in5b_V2
else:
    logging.info("waveshare_epd cannot be loaded")
    print("waveshare_epd cannot be loaded")
    exit()

logging.basicConfig(level=logging.DEBUG)
logging.info(PIL.__version__)


# Loading fonts
font_a = ImageFont.truetype(os.path.join(fontdir, 'Helvetica-Bold.ttf'), 24)
font_b = ImageFont.truetype(os.path.join(fontdir, 'Helvetica-Bold.ttf'), 36)
font_c = ImageFont.truetype(os.path.join(fontdir, 'Helvetica-Bold.ttf'), 50)
font_label = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 10)


def rec_mid(x, y, width, height):
    return (x - width/2, y-height/2, x + width/2, y+height/2)


def offset(rectangle, amount):
    x1, y1, x2, y2 = rectangle
    return (x1-amount, y1-amount, x2+amount, y2+amount)


def set_x(rectangle, x1, x2):
    _, y1, _, y2 = rectangle
    return (x1, y1, x2, y2)


try:
    logging.info("Test to draw current date time on screen")
    # Setup eink target objects
    epd = epd7in5b_V2.EPD()
    epd.init()

    # Clearing the previous image
    # logging.info("Clearing previous image")
    # epd.Clear()

    # Create new vertical image
    # Our screen is 480 (wide) x 800 (tall)
    logging.info("Drawing Vertical Image")
    image_blk = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    image_red = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw_blk = ImageDraw.Draw(image_blk)
    draw_red = ImageDraw.Draw(image_red)

    # Drawing
    draw_blk.text((40, 85), 'Last Update Time:', font=font_a, anchor="ls", fill=0)
    draw_red.text((40, 135), datetime.now().strftime('%Y-%m-%d (%a)'), font=font_b, anchor="ls", fill=0)
    draw_red.text((40, 180), datetime.now().strftime('%H:%M:%S'), font=font_c, anchor="ls", fill=0)

    # Draw progress bar boundary
    width, height = 396, 40
    bar_rec = rec_mid(240, 234, width, height)  # (42, 214, 438, 254)
    x1, y1, x2, y2 = bar_rec
    draw_blk.rectangle(offset(bar_rec, 8), fill=0)
    draw_red.rectangle(set_x(offset(bar_rec, 8), 108, 306), fill=0)
    draw_blk.rectangle(offset(bar_rec, 4), fill=1)
    draw_red.rectangle(offset(bar_rec, 4), fill=1)

    # Progress bar constants
    starting_hour = 6
    ending_hour = 24

    # Labels
    for h in range(starting_hour, ending_hour + 1):
        x = x1 + (x2 - x1) / (ending_hour - starting_hour) * (h - starting_hour)
        draw_blk.rectangle((x - 1, y1 - 8, x + 1, y2 + 8), fill=1) # White
        draw_red.rectangle((x - 1, y1 - 8, x + 1, y2 + 8), fill=1) # White
        if h % 3 == 0 :
            draw_blk.text((x - 1, y2 + 9), str(h), font=font_label, anchor="mt", fill=0)

    # Draw filled progress bar
    draw_blk.rectangle(bar_rec, fill=0)
    draw_red.rectangle((108, y1, 306, y2), fill=0)

    # Unfill progress bar
    hours_since_start = datetime.now().hour + datetime.now().minute / 60 - starting_hour
    current_width = max(0, width / (ending_hour - starting_hour) * hours_since_start)
    bar_negative = x1 + current_width, y1, x2, y2
    draw_blk.rectangle(bar_negative, fill=1)
    draw_red.rectangle(bar_negative, fill=1)



    # for h in range(starting_hour, ending_hour, 3):
    #     x1 + (x2 - x1) / (ending_hour - starting_hour) * h
    # draw_blk.text((40, 85), 'Last Update Time:', font=font_a, anchor="ls", fill=0)

    # Compile buffer
    buffer_blk = epd.getbuffer(image_blk.rotate(180))
    buffer_red = epd.getbuffer(image_red.rotate(180))
    logging.info("Updating Display")
    epd.display(buffer_blk, buffer_red)
    time.sleep(2)

    # Going to sleep mode
    logging.info("Goto Sleep...")
    epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd7in5b_V2.epdconfig.module_exit()
    exit()
