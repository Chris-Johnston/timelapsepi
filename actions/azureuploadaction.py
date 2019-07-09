"""
Azure Upload Action

Tries to upload the given file to Azure file storage.
If this action fails, queues the item and attempts
the upload when run again.
"""

from actions.action import Action
from azure.storage.blob import BlockBlobService
import yaml
import os

config_file = 'config.yaml'

class AzureUploadAction(Action):
    def __init__(self):
        self.setup()
        self.blob_service = BlockBlobService(account_name=self.account_name, account_key=self.account_key)

    def setup(self):
        with open(config_file, "r") as ymlfile:
            config = yaml.load(ymlfile, Loader=yaml.FullLoader)

        self.account_name = config['azure_upload']['account_name']
        self.account_key = config['azure_upload']['account_key']
        self.blob_container = config['azure_upload']['blob_container']

    def get_name(self):
        return 'azure_upload'

    def run(self, file: str):
        print("azure upload action: ", file)
        # TODO: handle internet disconnected and queueing
        self.blob_service.create_blob_from_path(self.blob_container, file, file)