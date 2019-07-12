"""
Raspberry Pi Camera Capture

"""

from capture.capturemethod import CaptureMethod
import time
import yaml

config_file = 'config.yaml'

ATTR_PI = 'pi_camera'

class PiCapture(CaptureMethod):
    def __init__(self):
        print('setting up pi camera')
        # hack, this gets around picamera not available for hosts that aren't Pis
        # so only import and set up on first use
        self.is_setup = False
    
    def setup(self):
        import picamera
        with open(config_file, "r") as ymlfile:
            config = yaml.load(ymlfile, Loader=yaml.FullLoader)
        x = config[ATTR_PI]['x']
        y = config[ATTR_PI]['y']
        self.dimensions = (x, y)
        self.iso = config[ATTR_PI]['iso']
        self.delay = config[ATTR_PI]['delay']
        # only create this once, memory issues
        self.c = picamera.PiCamera(resolution=self.dimensions)
        # led off while not capturing
        self.c.led = False
        self.is_setup = True

    def get_name(self) -> str:
        return "picam"

    def capture_image(self, path: str):
        # do first-time setup
        if not self.is_setup:
            self.setup()
        self.c.led = True
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