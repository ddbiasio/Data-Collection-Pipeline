import uuid
import json

class recipe():
    """
    This class provides a means to store the recipe information whilst processing
    
 
    Attributes
    ----------
        recipe_id : str
            The unique name for the recipe obtained from the URL
        recipe_UUID : UUID
            The UUIDv4 generated for the recipe
        recipe_name : str
            The name of the recipe
        ingredients : list
            A list of the ingredients
        planning_info : dict
            Information on preparation and cooking times
        method : dict
            A dictionary of the method with keys Step1, Step2, .. Stepn as required
        nutritional_info : dict
            A dictionary of the nutritional info e.g. calories, fat, sugar etc.
        url : str
            The URL for the recipe page
        image_url : str
            The URL for the recipe image
        
    Methods
    -------
        get_recipe_ids(self, url) -> tuple(str, UUID)
            Returns the recipe unique name (from url) and a UUIDv4 for the recipe

    """

    def __init__(self):
        self.recipe_id = ""
        self.recipe_UUID = ""
        self.recipe_name = ""
        self.ingredients = []
        self.planning_info = {}
        self.method = {}
        self.nutritional_info = {}
        self.url = ""
        self.image_url = ""

    def get_recipe_ids(self, url: str):
    #def get_recipe_ids(self, url: str) -> tuple(str, uuid.UUID):
    #This throws an error when I add annotation and can't see why
    #various articles suggest other annotation e.g. Tuple[x, y] or tuple[x, y]
    #But Tuple is said to be deprecated and tuple[] shows as syntax error
        """
        Returns the recipe unique name (from url) and a UUIDv4 for the recipe

        Parameters
        ----------
        url : str
            The url for the recipe

        Returns
        -------
        tuple(str, str)
            The recipe name ID, and recipe UUIDv4
        """
        recipe_id = url.split('/')[-1]
        recipe_uuid = uuid.uuid4()
        return recipe_id, recipe_uuid
