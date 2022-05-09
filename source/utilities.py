import uuid
import json

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

