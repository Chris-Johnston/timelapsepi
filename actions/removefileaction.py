"""
Remove File Action

Deletes the file. This should be executed after all other steps.
"""

from actions.action import Action
import os

class RemoveFileAction(Action):
    def get_name(self):
        return "remove"
    
    def run(self, file: str):
        # TODO: proper logging
        print("removefileaction: ", file)
        os.remove(file)
    