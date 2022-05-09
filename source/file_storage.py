import json
from utilities import UUIDEncoder
import os
from urllib import request

class FileStorage:

    def __init__(self,
            root_folder: str):

        self.create_folder(root_folder)
        self.root_folder = root_folder
        
    def create_folder(self, folder_name: str):
        """
        Creates a folder if it doesn't exist already

        Parameters
        ----------
        folder_name: str
            The name of the folder to create (full path should be provided)

        """
        # create folder
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

    def dict_to_json_file(self,
            dict_to_save: dict,
            folder: str,
            file: str):
        """
        Creates a file in JSON format from a dictionary

        Parameters
        ----------
        dict_to_save: dict
            The dictionary object to be written to file
        filename: str
            The filename of the JSON file to be created
        """
        with open(f"{folder}/{file}", "w") as outfile:
            json.dump(
                dict_to_save,
                outfile,
                cls=UUIDEncoder,
                indent=4)

    def save_image(self,
            url: str,
            folder: str,
            file: str):

        # Download the file from `url` and save it locally under `file_name`:
        request.urlretrieve(url, f"{folder}/{file}")