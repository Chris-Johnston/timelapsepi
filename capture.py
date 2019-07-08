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

from invalidmethodexception import InvalidMethodException
from capture.capturemethod import CaptureMethod

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
    pass

def get_image_path() -> str:
    """
    Get Image Path

    Generates the path of the next image to save.
    """
    now = datetime.datetime.now()
    return os.path.join('images', f'{now.date().isoformat()}', f'{now.time().strftime("%H:%M:%S")}.jpg')

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

def sleep_next_capture():
    """
    Sleeps until the next image capture is ready.
    """
    # TODO: handle sunset/sunrise stuff, don't bother capturing when it's dark out
    # TODO: enable capture on startup
    # TODO: ensure that captures happen on the minute/on the hour
    time.sleep(5)


if __name__ == "__main__":
    # first-time setup
    modules = load_capture_types()

    # TODO: proper logging
    print('starting')

    # background daemon
    while True:
        sleep_next_capture()
        print('Starting webcam capture')

        path = get_image_path()
        # create directory if it doesn't exist
        create_path(path)

        print('Saving to file:', path)

        method = 'webcam'
        m = get_capture_method(modules, method)
        capture_image(path, m)
