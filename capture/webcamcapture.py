"""
Webcam Capture

Runs a command to capture from the webcam
"""

from capture.capturemethod import CaptureMethod
import os
import logging

logger = logging.getLogger(__name__)

class WebcamCapture(CaptureMethod):
    def get_name(self) -> str:
        return "webcam"

    def capture_image(self, path: str):
        logger.info("Starting webcam capture.")
        # this is a hack, we won't actually use the usb webcam when deployed
        command = f'fswebcam -p YUYV -S 20 --no-banner --resolution 1920x1080 --quiet {path}'
        logger.debug(f"Running capture command: {command}")
        os.system(command)
