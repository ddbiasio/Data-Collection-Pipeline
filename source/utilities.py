import os
import uuid
import json
import urllib.request

class UUIDEncoder(json.JSONEncoder):
    """
    Contains a function to make UUID in dictionary serializable

    Attributes
    ----------
    None

    Methods
    -------
    default(obj : object) -> hex
        If the object is a UUID then return it in hex format

    """

    def default(self, obj: object) -> str:
        if isinstance(obj, uuid.UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)

class file_ops:

    @staticmethod
    def create_folder(folder_name: str):
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

    @staticmethod
    def dict_to_json_file(dict_to_save: dict, filename: str):
        """
        Creates a file in JSON format from a dictionary

        Parameters
        ----------
        dict_to_save: dict
            The dictionary object to be written to file
        filename: str
            The filename of the JSON file to be created
        """
        with open(f"{filename}", "w") as outfile:
            json.dump(
                dict_to_save,
                outfile,
                cls=UUIDEncoder,
                indent=4)

    @staticmethod
    def get_image(url: str, file_name: str):

        # Download the file from `url` and save it locally under `file_name`:
        urllib.request.urlretrieve(url, f"{file_name}.jpg")
