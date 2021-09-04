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
font_weather = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 20)
font_label = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 10)


def rec_mid(x, y, width, height):
    return (x - width/2, y-height/2, x + width/2, y+height/2)


def offset(rectangle, amount):
    x1, y1, x2, y2 = rectangle
    return (x1-amount, y1-amount, x2+amount, y2+amount)


def set_x(rectangle, x1, x2):
    _, y1, _, y2 = rectangle
    return (x1, y1, x2, y2)


def init_eink():
    # Setup eink target objects
    epd = epd7in5b_V2.EPD()

    # Create new vertical image
    # Our screen is 480 (wide) x 800 (tall)
    logging.info("Drawing Vertical Image")
    image_blk = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    image_red = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw_blk = ImageDraw.Draw(image_blk)
    draw_red = ImageDraw.Draw(image_red)
    eink = {
        'image_blk': image_blk,
        'image_red': image_red,
        'draw_blk': draw_blk,
        'draw_red': draw_red,
    }
    return eink


def finalize_eink(eink):
    epd = epd7in5b_V2.EPD()
    epd.init()
    # Compile buffer
    buffer_blk = epd.getbuffer(eink['image_blk'].rotate(180))
    buffer_red = epd.getbuffer(eink['image_red'].rotate(180))
    logging.info("Updating Display")
    # Sending to display
    epd.display(buffer_blk, buffer_red)
    time.sleep(2)
    # Going to sleep mode
    logging.info("Goto Sleep...")
    epd.sleep()


def draw_time_of_day(eink):
    # Drawing title
    eink['draw_blk'].text((40, 85), 'Last Update Time:', font=font_a, anchor="ls", fill=0)
    eink['draw_red'].text((40, 135), datetime.now().strftime('%Y-%m-%d (%a)'), font=font_b, anchor="ls", fill=0)
    eink['draw_red'].text((40, 180), datetime.now().strftime('%H:%M:%S'), font=font_c, anchor="ls", fill=0)

    # Draw progress bar boundary
    width, height = 396, 40
    bar_rec = rec_mid(240, 234, width, height)  # (42, 214, 438, 254)
    x1, y1, x2, y2 = bar_rec
    eink['draw_blk'].rectangle(offset(bar_rec, 8), fill=0)
    eink['draw_red'].rectangle(set_x(offset(bar_rec, 8), 108, 306), fill=0)
    eink['draw_blk'].rectangle(offset(bar_rec, 4), fill=1)
    eink['draw_red'].rectangle(offset(bar_rec, 4), fill=1)

    # Progress bar constants
    starting_hour = 6
    ending_hour = 24

    # Labels
    for h in range(starting_hour, ending_hour + 1):
        x = x1 + (x2 - x1) / (ending_hour - starting_hour) * (h - starting_hour)
        eink['draw_blk'].rectangle((x - 1, y1 - 8, x + 1, y2 + 8), fill=1)  # White
        eink['draw_red'].rectangle((x - 1, y1 - 8, x + 1, y2 + 8), fill=1)  # White
        if h % 3 == 0:
            eink['draw_blk'].text((x - 1, y2 + 9), str(h), font=font_label, anchor="mt", fill=0)

    # Draw filled progress bar
    eink['draw_blk'].rectangle(bar_rec, fill=0)
    eink['draw_red'].rectangle((108, y1, 306, y2), fill=0)

    # Unfill progress bar
    hours_since_start = datetime.now().hour + datetime.now().minute / 60 - starting_hour
    current_width = max(0, width / (ending_hour - starting_hour) * hours_since_start)
    bar_negative = x1 + current_width, y1, x2, y2
    eink['draw_blk'].rectangle(bar_negative, fill=1)
    eink['draw_red'].rectangle(bar_negative, fill=1)
    # for h in range(starting_hour, ending_hour, 3):
    #     x1 + (x2 - x1) / (ending_hour - starting_hour) * h


def draw_weather(eink, state):
    if 'weather_24h_history' not in state:
        return
    weather = state

    # Printing Historial Data
    eink['draw_blk'].text((40, 300), 'Historic', font=font_a, anchor="ls", fill=0)
    if 'weather_24h_history' in weather:
        x = 40
        y = 330
        y_space = 24
        for i, observation in enumerate(weather['weather_24h_history']):
            text = "%s : %s%s" % (
                datetime.fromtimestamp(observation['EpochTime']).strftime("%a %H:%M"),
                observation['Temperature']['Metric']['Value'],
                observation['Temperature']['Metric']['Unit']
            )
            eink['draw_blk'].text((x, y + y_space * i), text, font=font_weather, anchor="ls", fill=0)

    # 5 Day Forecast
    eink['draw_blk'].text((240, 300), '5-Days', font=font_a, anchor="ls", fill=0)
    if 'weather_5d_forecast' in weather:
        for i, observation in enumerate(weather['weather_5d_forecast']['DailyForecasts']):
            x = 240
            y = 330
            y_space = 24
            text="%s : %s%s to %s%s" % (
                datetime.fromtimestamp(observation['EpochDate']).strftime("%a"),
                observation['Temperature']['Minimum']['Value'],
                observation['Temperature']['Minimum']['Unit'],
                observation['Temperature']['Maximum']['Value'],
                observation['Temperature']['Maximum']['Unit'],
            )
            eink['draw_blk'].text((x, y + y_space * i), text, font=font_weather, anchor="ls", fill=0)

    # Printing Hourly Forecast
    eink['draw_blk'].text((240, 470), 'Forecast', font=font_a, anchor="ls", fill=0)
    if 'weather_24h_history' in weather:
        x = 240
        y = 500
        y_space = 24
        for i, observation in enumerate(weather['weather_12h_forecast']):
            text = "%s : %s%s" % (
                datetime.fromtimestamp(observation['EpochDateTime']).strftime("%a %H:%M"),
                observation['Temperature']['Value'],
                observation['Temperature']['Unit']
            )
            eink['draw_blk'].text((x, y + y_space * i), text, font=font_weather, anchor="ls", fill=0)




def draw_and_update_display(state):
    try:
        eink = init_eink()

        logging.info("Test to draw current date time on screen")
        draw_time_of_day(eink)

        draw_weather(eink, state)
        finalize_eink(eink)

    except IOError as e:
        logging.info(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd7in5b_V2.epdconfig.module_exit()
        # exit()


if __name__ == "__main__":
    from get_weather import retrieve_all_weather
    weather = retrieve_all_weather({})
    draw_and_update_display(weather)
