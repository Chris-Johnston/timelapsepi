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

from invalidmethodexception import InvalidMethodException
from capture.capturemethod import CaptureMethod
from actions.action import Action

config_file = 'config.yaml'

def load_config():
    with open(config_file, "r") as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)
    return config

# all of the modules to load that implement CaptureMethod
# these are the various ways to capture from the webcam
capture_methods = ['capture.webcamcapture']

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

def sleep_next_capture(interval: int):
    """
    Sleeps until the next image capture is ready.
    """
    # TODO: handle sunset/sunrise stuff, don't bother capturing when it's dark out
    # TODO: enable capture on startup
    # TODO: ensure that captures happen on the minute/on the hour
    time.sleep(interval)


if __name__ == "__main__":
    # first-time setup
    modules = load_capture_types()
    actions = load_action_types()
    config = load_config()

    # TODO: proper logging
    print('starting')

    # background daemon
    while True:
        print('waiting for next capture')
        sleep_next_capture(config["interval"])
        print('Starting webcam capture')

        path = get_image_path(config["capture_directory"])
        # create directory if it doesn't exist
        create_path(path)

        print('Saving to file:', path)

        # capture the image using the preferred method
        method = config["capture_method"]
        m = get_capture_method(modules, method)
        capture_image(path, m)

        # run each action in order on the file
        for action in config["post_capture_methods"]:
            a = actions[action]
            a.run(path)