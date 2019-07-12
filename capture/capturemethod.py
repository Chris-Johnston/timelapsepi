"""
Capture Method

Base class for different ways to capture images from cameras.
"""

from abc import ABC, abstractmethod

class CaptureMethod(ABC):
    @abstractmethod
    def get_name(self):
        """
        Get Name

        Gets the name of the capture method.
        """
        pass

    @abstractmethod
    def capture_image(self, path: str):
        """
        Capture Image

        Captures an image from a camera source, and saves it to the file.
        """
        pass