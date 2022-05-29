import json
from logging import root
from .utilities import UUIDEncoder
import os
from urllib import request
from .storage import Storage
# TODO Need test functions for this
class FileStorage(Storage):
    """
    A class to manage operating system file operations

    Attributes
    ----------
    root_folder: str
        The root folder under which all operation will take place
    
    Methods
    -------
    create_folder(folder: str)
    list_files(folder: str) -> list
    dict_to_json_file(dict_to_save: dict, folder: str, file: str)
    save_image(url: str, folder: str, file: str)
    read_json_file(file: str) -> str

    """
    def __init__(self,
            root_folder: str,
            data_folder: str,
            images_folder: str):
        """
        Creates an instance of the FileStorage class

        Parameters
        ----------
        root_folder: str
            The root folder under which all operation will take place
        data_folder : str
            Name of the data folder to create on initialisation
        images_folder : str
            Name of the image folder to create on initialisation
        """
        self.root_folder = root_folder
        self.data_folder = data_folder
        self.images_folder = images_folder
        self.__create_folder(root_folder)
        self.__create_folder(data_folder)
        self.__create_folder(images_folder)
        
    def __create_folder(self, folder: str):
        """
        Creates a folder if it doesn't exist already

        Parameters
        ----------
        folder: str
            The name of the folder to create (full path should be provided)

        """
        # create folder
        if not os.path.exists(folder):
            os.mkdir(folder)
    
    def list_files(self,
            folder: str,
            file_type: str = None) -> list:
        """
        Lists all files in a given folder (filtered optionally by file type)
        
        Parameters
        ----------
        folder: str
            The name of the folder where the files are (full path should be provided)
        file_type : str, optional
            A valid file type extension, by default None

        Returns
        -------
        list:
            A list of file names (full paths) in the folder
        """
        files = []
        for path in os.listdir(folder):
            # get the full path
            full_path = os.path.join(folder, path)
            # exclude directories
            if os.path.isfile(full_path):
                if file_type is None or file_type == full_path.rsplit('.', 1)[-1]:
                    files.append(full_path)
        return files

    def save_json_file(self,
            dict_to_save: dict,
            folder: str,
            file: str):
        """Saves a dictionary to json file

        Parameters
        ----------
        dict_to_save : dict
            The dictionary to be saved as JSON file
        folder : str
            The folder where the file will be saved
        file : str
            The name of the file
        """
        # Open a file to write to and save json string to the file
        with open(f"{folder}/{file}.json", "w") as outfile:
            json.dump(
                dict_to_save,
                outfile,
                cls=UUIDEncoder,
                indent=4)

    def save_image(self,
            url: str,
            folder: str,
            file: str):
        """
        Retrieves an image from a URL and saves it

        Parameters
        ----------
        url: str
            The url of the image to be downloaded
        folder : str
            The folder where the file will be saved
        file: str
            The name of the file to save as
        """
        # Download the file from `url` and save it locally under `file_name`:
        request.urlretrieve(url, f"{folder}/{file}")
    
    def read_json_file(self,
            file: str) -> str:
        """
        Reads a json file and returns as string in json format

        Parameters
        ----------
        file : str
            The name of the file to be opened (full path)

        Returns
        -------
        str
            A string in json format
        """
        # Open a file for reading and load json into str
        with open(f"{file}", "r") as jsonfile: 
            return json.load(jsonfile)