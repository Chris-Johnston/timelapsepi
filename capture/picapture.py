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

    def get_name(self) -> str:
        return "picam"

    def capture_image(self, path: str):
        # TODO: proper logging
        c = picamera.PiCamera(resolution=self.dimensions)
        c.iso = self.iso
        time.sleep(self.delay)
        
        # fix settings so images are more consistent
        # https://picamera.readthedocs.io/en/release-1.13/recipes1.html#capturing-consistent-images
        c.shutter_speed = c.exposure_speed
        c.exposure_mode = 'off'
        g = c.awb_gains
        c.awb_mode = 'off'
        c.awb_gains = g
        c.led = False

        # capture the image to the file
        c.capture(path)