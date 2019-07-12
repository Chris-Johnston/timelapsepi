"""
Azure Upload Action

Tries to upload the given file to Azure file storage.
If this action fails, queues the item and attempts
the upload when run again.
"""

from actions.action import Action
from azure.common import AzureException
from azure.storage.blob import BlockBlobService
import yaml
import os
import urllib

config_file = 'config.yaml'

class AzureUploadAction(Action):
    def __init__(self):
        self.setup()
        print("setting up azure blob service")
        self.blob_service = BlockBlobService(account_name=self.account_name, account_key=self.account_key)
        self.upload_queue = []

    def setup(self):
        with open(config_file, "r") as ymlfile:
            config = yaml.load(ymlfile, Loader=yaml.FullLoader)

        self.account_name = config['azure_upload']['account_name']
        self.account_key = config['azure_upload']['account_key']
        self.blob_container = config['azure_upload']['blob_container']
        self.timeout = config['azure_upload']['timeout']

    def get_name(self):
        return 'azure_upload'
    
    def check_online(self):
        """
        Checks if the internet connection is up
        """
        try:
            urllib.request.urlopen('http://microsoft.com')
            return True
        except:
            return False

    def run(self, file: str) -> bool:
        print("azure upload action: ", file)
        # queue up the next file to upload
        self.upload_queue.append(file)

        # keep uploading while there is internet
        while self.upload_queue:
            f = self.upload_queue.pop()
            print('processing file', f)

            # check if connected before attempting upload
            if self.check_online():
                try:
                    print('uploaded file', f)
                    self.blob_service.create_blob_from_path(self.blob_container, f, f, max_connections=1, timeout=self.timeout)
                except AzureException:
                    print('error while uploading, likely not connected. queueing file and dealing with it later.')
                    # likely not connected to the internet, add this to the queue
                    # and stop processing the queue
                    self.upload_queue.append(f)
                    return False
            else:
                print('not connected, queueing.')
                # not connected, so just add to the queue
                self.upload_queue.append(f)
                return False
        return True
