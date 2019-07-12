"""
Webcam Capture

"""

from capture.capturemethod import CaptureMethod
import os

class WebcamCapture(CaptureMethod):
    def get_name(self) -> str:
        return "webcam"

    def capture_image(self, path: str):
        # TODO: proper logging
        print("webcamcapture: capturing")
        # this is a hack, we won't actually use the usb webcam when deployed
        command = f'fswebcam -p YUYV -S 20 --no-banner --resolution 1920x1080 --quiet {path}'
        print('running', command)
        os.system(command)
