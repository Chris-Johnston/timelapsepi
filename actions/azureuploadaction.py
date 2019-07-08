"""
Azure Upload Action

Tries to upload the given file to Azure file storage.
If this action fails, queues the item and attempts
the upload when run again.
"""

from actions.action import Action

class AzureUploadAction(Action):
    def get_name(self):
        return 'azure-upload'

    def run(self):
        # todo
        pass