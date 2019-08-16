#!/usr/bin/python3
"""
Timelapse Capture Daemon

Runs as a service and automatically captures files from the webcam.

Uploads the files to Azure when there is an internet connection.
"""

import datetime
import importlib
import inspect
import os
import time
import datetime
import yaml
import logging
from logging.handlers import RotatingFileHandler
import json

from invalidmethodexception import InvalidMethodException
from capture.capturemethod import CaptureMethod
from actions.action import Action

log_format = '%(asctime)s %(levelname)s: %(message)s'
config_file = 'config.yaml'

def load_config():
    with open(config_file, "r") as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)
    return config

config = load_config()

# setup logging
numeric_log_level = getattr(logging, config["log_level"].upper(), logging.DEBUG)
logging.basicConfig(filename=config["logs"], level=numeric_log_level, format=log_format)

# log to console window and log file
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logging.Formatter(log_format))
logging.getLogger().addHandler(consoleHandler)

# limit the size of the log files to 2gb
file_handler = RotatingFileHandler(config["logs"], maxBytes=2147483648, backupCount=2)
logging.getLogger().addHandler(file_handler)

logger = logging.getLogger(__name__)
logger.info("Starting timelapse application.")

# all of the modules to load that implement CaptureMethod
# these are the various ways to capture from the webcam
capture_methods = ['capture.webcamcapture', 'capture.picapture']

load_actions = ['actions.azureuploadaction', 'actions.removefileaction']

def load_capture_types() -> dict:
    """
    Load Capture Types

    Loads and instanitates all of the CaptureMethod types specified by
    capture_methods.
    """
    modules = {}
    for m in capture_methods:
        mod = importlib.import_module(m)
        # get subclasses of module
        for name, obj in inspect.getmembers(mod):
            if obj is not CaptureMethod and isinstance(obj, type) and issubclass(obj, CaptureMethod):
                instance = obj()
                name = instance.get_name()
                logger.debug(f"Loaded capture method {name}")
                modules[name] = instance 
    return modules

def load_action_types() -> dict:
    """
    Load action modules

    Loads all of the Action types.
    """
    actions = {}
    for a in load_actions:
        mod = importlib.import_module(a)
        for name, obj in inspect.getmembers(mod):
            if obj is not Action and isinstance(obj, type) and issubclass(obj, Action):
                instance = obj()
                name = instance.get_name()
                logger.debug(f"Loaded action type {name}")
                actions[name] = instance
    return actions

def get_image_path(directory: str) -> str:
    """
    Get Image Path

    Generates the path of the next image to save.
    """
    now = datetime.datetime.now()
    return os.path.join(directory, f'{now.date().isoformat()}', f'{now.time().strftime("%H:%M:%S")}.jpg')

def create_path(path: str):
    """
    Creates a path for a file if it does not already exist.
    """
    directory = os.path.dirname(os.path.abspath(path))
    if not os.path.exists(directory):
        logger.info(f"Creating path {directory} because it did not yet exist.")
        os.makedirs(directory)

def get_capture_method(modules: dict, method: str) -> CaptureMethod:
    """
    Get Capture Method

    Gets the method used to capture an image.
    """
    if method in modules:
        return modules[method]
    raise InvalidMethodException(f"The capture method {method} could not be found.")

def capture_image(path: str, method: CaptureMethod):
    """
    Captures an image using the method provided.
    """
    method.capture_image(path)

def sleep_next_capture(interval: int, min_time: int, max_time: int):
    """
    Sleeps until the next image capture is ready.
    """
    # get the current second in the day
    current_time = datetime.datetime.now().time()
    day_second = (current_time.microsecond / 1000000.0) + current_time.second + (60 * current_time.minute) + (3600 * current_time.hour)
    
    if day_second < min_time:
        logger.info(f"Current time {day_second}, waiting until {min_time} (less than min time {min_time}). {min_time - day_second}")
        # if before min, sleep until then
        time.sleep(min_time - day_second)
    elif day_second > max_time:
        logger.info(f"Current time {day_second}, waiting until {min_time} (greater than max time {max_time}). {min_time + (24 * 3600) - day_second}")
        # if after max, wait remaining duration of day + min time
        time.sleep(min_time + (24 * 3600) - day_second)
    
    actual_delay = interval - (day_second % interval)
    logger.info(f"Starting sleep interval of {interval} for {actual_delay}.")
    time.sleep(day_second % interval)

def run_actions_on_file(file: str, actions: dict, config) -> bool:
    """
    Run Actions on File
    """
    for action in config["post_capture_methods"]:
        a = actions[action]
        result = a.run(file)
        if not result:
            logger.info(f"Action '{a.get_name()}' failed on file: {file}")
            return False
    return True

def write_action_queue(file: str, queue: list):
    """
    Writes the queue of actions to json.
    """
    # create a new file if doesn't already exist
    try:
        with open(file, "w") as f:
            logger.debug(f"Writing the action queue to file: {file}")
            json.dump(queue, f)
    except Exception as e:
        logger.error(f"Exception when saving action queue to file: {e}")

def load_action_queue(file: str) -> list:
    """
    loads the action queue from json.
    if the file does not exist, returns an empty list.
    """
    if os.path.exists(file):
        # open the file, load the queue
        logger.debug("Loading the action queue.")
        with open(file, "r") as f:
            # assumption that this will be in the right format
            return json.load(f)
    else:
        logger.info("Action queue file did not yet exist, so the queue is empty.")
        return []
    


if __name__ == "__main__":
    # first-time setup
    modules = load_capture_types()
    actions = load_action_types()
    # queue of all files to process
    # if one step fails, then requeue it and retry all steps in order
    action_queue = load_action_queue(config["queue"])

    # background daemon
    while True:
        # before anything else, process the queue
        while action_queue:
            f = action_queue.pop()
            logging.info(f"Processing item {f} in queue.")

            # ensure that the file exists before trying to process it
            if not os.path.exists(f):
                logger.warning(f"Item {f} in queue did not exist. Skipping.")
                continue

            # run each action in order on the file
            result = run_actions_on_file(f, actions, config)
            # on fail, queue
            if not result:
                logger.info(f"Actions for file {f} failed, adding to queue.")
                logger.debug(f"Queue: {' '.join(action_queue)}")
                action_queue.append(f)
                break
        # pass or fail, write the updated queue
        write_action_queue(config["queue"], action_queue)

        # after queue, start capturing
        logger.info("Waiting for next capture.")
        sleep_next_capture(config["interval"], config["limit"]["min_time_seconds"], config["limit"]["max_time_seconds"])
        logger.info("Starting next capture.")

        # re-load the queue
        action_queue = load_action_queue(config["queue"])

        path = get_image_path(config["capture_directory"])
        # create directory if it doesn't exist
        create_path(path)
        logger.info(f"Saving next image to path: {path}")

        # capture the image using the preferred method
        method = config["capture_method"]
        m = get_capture_method(modules, method)
        logger.info(f"Capturing image using {method} method to file {path}")
        capture_image(path, m)
        action_queue.append(path)
        
        # write updated config before executing the queue
        write_action_queue(config["queue"], action_queue)
