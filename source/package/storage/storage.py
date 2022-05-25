from abc import ABC, abstractmethod

class Storage(ABC):

    @abstractmethod
    def list_files(self,
            folder: str,
            file_type: str = None) -> list:        
        pass

    @abstractmethod
    def save_json_file(self,
            dict_to_save: dict,
            folder: str,
            file: str):
        pass

    @abstractmethod
    def save_image(self,
            url: str,
            folder: str,
            file: str):
        pass

    @abstractmethod        
    def read_json_file(self,
            file: str) -> str:
        pass