"""
Action

Represents an action to be done on a file after it is captured.
"""

from abc import ABC, abstractmethod

class Action(ABC):
    @abstractmethod
    def get_name(self) -> str:
        """
        Gets the name of the action.
        """
        pass

    @abstractmethod
    def run(self, file_path: str):
        """
        Run

        Runs this action on the supplied file.
        """
        pass
