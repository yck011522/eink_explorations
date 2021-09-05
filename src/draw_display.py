#!/usr/bin/python
# -*- coding:utf-8 -*-
import logging
import os
import sys
import time
import traceback
from datetime import datetime
from math import ceil, floor

import PIL
from PIL import Image, ImageDraw, ImageFont

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
font_hel_16 = ImageFont.truetype(os.path.join(fontdir, 'Helvetica-Bold.ttf'), 16)
font_hel_20 = ImageFont.truetype(os.path.join(fontdir, 'Helvetica-Bold.ttf'), 20)
font_hel_24 = ImageFont.truetype(os.path.join(fontdir, 'Helvetica-Bold.ttf'), 24)
font_hel_28 = ImageFont.truetype(os.path.join(fontdir, 'Helvetica-Bold.ttf'), 28)
font_hel_36 = ImageFont.truetype(os.path.join(fontdir, 'Helvetica-Bold.ttf'), 36)
font_hel_50 = ImageFont.truetype(os.path.join(fontdir, 'Helvetica-Bold.ttf'), 50)
font_base_20 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 20)
font_base_12 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 12)


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
    now = datetime.now()
    date_color = 'draw_red' if now.weekday() > 4 else 'draw_blk'
    eink[date_color].text((42, 130), now.strftime('%Y-%m-%d (%a)'), font=font_hel_36, anchor="ls", fill=0)
    eink['draw_blk'].text((40, 180), now.strftime('%H:%M:%S'), font=font_hel_50, anchor="ls", fill=0)

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
            eink['draw_blk'].text((x - 1, y2 + 10), str(h), font=font_base_12, anchor="mt", fill=0)

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


def draw_weather_old(eink, state):
    if 'weather_24h_history' not in state:
        return
    weather = state

    # Printing Historial Data
    eink['draw_blk'].text((40, 300), 'Historic', font=font_hel_24, anchor="ls", fill=0)
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
            eink['draw_blk'].text((x, y + y_space * i), text, font=font_base_20, anchor="ls", fill=0)

    # 5 Day Forecast
    eink['draw_blk'].text((240, 300), '5-Days', font=font_hel_24, anchor="ls", fill=0)
    if 'weather_5d_forecast' in weather:
        for i, observation in enumerate(weather['weather_5d_forecast']['DailyForecasts']):
            x = 240
            y = 330
            y_space = 24
            text = "%s : %s%s to %s%s" % (
                datetime.fromtimestamp(observation['EpochDate']).strftime("%a"),
                observation['Temperature']['Minimum']['Value'],
                observation['Temperature']['Minimum']['Unit'],
                observation['Temperature']['Maximum']['Value'],
                observation['Temperature']['Maximum']['Unit'],
            )
            eink['draw_blk'].text((x, y + y_space * i), text, font=font_base_20, anchor="ls", fill=0)

    # Printing Hourly Forecast
    eink['draw_blk'].text((240, 470), 'Forecast', font=font_hel_24, anchor="ls", fill=0)
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
            eink['draw_blk'].text((x, y + y_space * i), text, font=font_base_20, anchor="ls", fill=0)


def draw_weather(eink, state):
    if 'weather_24h_history' not in state:
        return
    data = state['daily_temp_plot']

    # Draw chart boundary
    anchor_x, anchor_y = 240, 288  # Anchor at top mid point
    width, height = 396, 80
    bar_rec = rec_mid(anchor_x, anchor_y + height / 2, width, height)  # (42, 214, 438, 254)
    x1, y1, x2, y2 = bar_rec
    eink['draw_blk'].rectangle(offset(bar_rec, 8), fill=0)
    # eink['draw_red'].rectangle(set_x(offset(bar_rec, 8), 108, 306), fill=0)
    eink['draw_blk'].rectangle(offset(bar_rec, 4), fill=1)
    # eink['draw_red'].rectangle(offset(bar_rec, 4), fill=1)

    # Progress bar constants
    starting_hour = 6
    ending_hour = 24

    # Estimate temp min max
    temp_min = None
    temp_max = None
    for h in range(starting_hour, ending_hour):
        if data[str(h)]['historic'] is not None:
            temp = data[str(h)]['historic']
        elif data[str(h)]['forecast'] is not None:
            temp = data[str(h)]['forecast']
        else:
            continue
        temp_min = temp if temp_min is None else min(temp, temp_min)
        temp_max = temp if temp_max is None else max(temp, temp_max)
    temp_min = temp_min
    temp_max = temp_max

    # Draw Temp Plots (Historic + Forecast)
    for h in range(starting_hour, ending_hour):
        # Grap points / Skip through empty point
        if data[str(h)]['historic'] is not None:
            temp = data[str(h)]['historic']
        elif data[str(h)]['forecast'] is not None:
            temp = data[str(h)]['forecast']
        else:
            continue

        # Plot Point
        x = x1 + (x2 - x1) / (ending_hour - starting_hour) * (h - starting_hour)
        y = y2 - (temp - floor(temp_min)) / (ceil(temp_max) - floor(temp_min)) * height
        rectangle = rec_mid(x, y, 3, 3)
        eink['draw_blk'].rectangle(rectangle, fill=0)

        # Draw minima maxima tag with a white box bg
        padding = 8
        if temp == temp_min:
            rectangle = rec_mid(x, y-padding - 8, 40, 18)
            eink['draw_blk'].rectangle(rectangle, fill=1)
            eink['draw_blk'].text((x, y-padding), '%.1f' % temp_min, font=font_base_20, anchor="mb", fill=0)
        if temp == temp_max:
            rectangle = rec_mid(x, y+padding + 8, 40, 18)
            eink['draw_blk'].rectangle(rectangle, fill=1)
            eink['draw_blk'].text((x, y+padding), '%.1f' % temp_max, font=font_base_20, anchor="mt", fill=0)

    # Draw 5 Day forecast
    x_border = 40
    y = 410
    for i, observation in enumerate(weather['weather_5d_forecast']['DailyForecasts']):
        if i > 4:
            break
        x = x_border + (480 - (2*x_border)) / 10 * (i * 2 + 1)
        d = datetime.fromtimestamp(observation['EpochDate'])
        date_color = 'draw_red' if d.weekday() > 4 else 'draw_blk'
        eink[date_color].text((x, y), d.strftime("%d"), font=font_hel_28, anchor="mb", fill=0)
        eink[date_color].text((x, y+17), d.strftime("%a"), font=font_base_20, anchor="mb", fill=0)
        # Temperature range
        temp_string = "%.0f" % (
            observation['Temperature']['Maximum']['Value'],
        )
        eink['draw_blk'].text((x, y+45), temp_string, font=font_hel_28, anchor="mb", fill=0)
        temp_string = "%.0f" % (
            observation['Temperature']['Minimum']['Value'],
        )
        eink['draw_blk'].text((x, y+77), temp_string, font=font_hel_28, anchor="mb", fill=0)
        # Separator
        rectangle = rec_mid(x, y+52, 40, 1)
        eink['draw_blk'].rectangle(rectangle, fill=0)

    eink['draw_blk'].text((480-x_border + 4, y+55), '\u00b0C', font=font_hel_28, anchor="mb", fill=0)
    eink['draw_blk'].text((x_border, y+45), 'Hi', font=font_hel_20, anchor="rb", fill=0)
    eink['draw_blk'].text((x_border, y+77), 'Lo', font=font_hel_20, anchor="rb", fill=0)


def draw_and_update_display(state):
    try:
        eink = init_eink()

        logging.info("Test to draw current date time on screen")
        draw_time_of_day(eink)

        # draw_weather_old(eink, state)
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
