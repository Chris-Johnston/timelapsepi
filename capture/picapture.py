"""
Raspberry Pi Camera Capture

"""

from capture.capturemethod import CaptureMethod
import picamera
import time
import yaml

config_file = 'config.yaml'

ATTR_PI = 'pi_camera'

class PiCapture(CaptureMethod):
    def __init__(self):
        print('setting up pi camera')
        self.setup()

    def setup(self):
        with open(config_file, "r") as ymlfile:
            config = yaml.load(ymlfile, Loader=yaml.FullLoader)
        x = config[ATTR_PI]['x']
        y = config[ATTR_PI]['y']
        self.dimensions = (x, y)
        self.iso = config[ATTR_PI]['iso']
        self.delay = config[ATTR_PI]['delay']
        self.c = picamera.PiCamera(resolution=self.dimensions)

    def get_name(self) -> str:
        return "picam"

    def capture_image(self, path: str):
        # TODO: proper logging
        self.c.iso = self.iso
        time.sleep(self.delay)
        
        # fix settings so images are more consistent
        # https://picamera.readthedocs.io/en/release-1.13/recipes1.html#capturing-consistent-images
        self.c.shutter_speed = self.c.exposure_speed
        self.c.exposure_mode = 'off'
        g = self.c.awb_gains
        self.c.awb_mode = 'off'
        self.c.awb_gains = g
        self.c.led = False

        # capture the image to the file
        self.c.capture(path)