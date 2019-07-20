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
import urllib.request
import logging
logger = logging.getLogger(__name__)

config_file = 'config.yaml'

class AzureUploadAction(Action):
    def __init__(self):
        logger.info("Setting up Azure Blob Service.")
        self.setup()
        self.blob_service = BlockBlobService(account_name=self.account_name, account_key=self.account_key)

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
            urllib.request.urlopen('http://www.github.com', timeout=1)
            logger.debug("Internet connection is up.")
            return True
        except:
            logger.info("Internet connection is down.")
            return False

    def run(self, file: str) -> bool:
        logging.info(f"Uploading file {file} to Azure.")
        if self.check_online():
            try:
                self.blob_service.create_blob_from_path(self.blob_container, file, file, max_connections=1, timeout=self.timeout)
                logging.info(f"Uploaded to Azure.")
                return True
            except AzureException as ex:
                logging.warning(f"Error while uploading to Azure while online: {ex}")
                return False
        else:
            logging.warning("Didn't upload file because offline.")
            return False
