"""
Remove File Action

Deletes the file. This should be executed after all other steps.
"""

from actions.action import Action
import os
import logging

logger = logging.getLogger(__name__)

class RemoveFileAction(Action):
    def get_name(self):
        return "remove"
    
    def run(self, file: str) -> bool:
        logger.info(f"Removing file {file}")
        os.remove(file)
        return True
    