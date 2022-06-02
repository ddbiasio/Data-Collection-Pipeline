import uuid
import json

class UUIDEncoder(json.JSONEncoder):
    """
    Contains a function to make UUID in dictionary serializable

    Methods
    -------
    default(obj : object) -> hex
        If the object is a UUID then return it in hex format

    """

    def default(self, obj: object) -> str:
        """Returns UUID as Hex

        Parameters
        ----------
        obj : object
            Any object

        Returns
        -------
        str
           Returns obj (as hex str when obj is a UUID object)
        """        
        if isinstance(obj, uuid.UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)

