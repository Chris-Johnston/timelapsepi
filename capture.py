#/usr/bin/python3

"""
Capture script

saves the camera output if the image is within the
correct time limits

this should be run every 15 min in cron
"""

import datetime
import os

# relative to working dir
IMAGES_DIR = '/home/pi/images'

SUNRISE_HOUR = 5 # 5 am
SUNSET_HOUR = 21 # 9 pm

# HACK: do this in a less vulnerable way
# TODO: need to fix the webcam timeout bug
COMMAND = f'fswebcam "{IMAGES_DIR}/%Y-%m-%d_%T.jpg" -p YUYV -S 20'

# only run in the right hours
if SUNRISE_HOUR <= datetime.datetime.now().hour <= SUNSET_HOUR:
    # valid time, run the command to save
    os.system(COMMAND)
    print(f'saved image at time: {datetime.datetime.now()}')
else:
    print(f'skipped: {datetime.datetime.now()}')