import uuid
import json
from scraper import scraper
from scraper import locator
from selenium.webdriver.common.by import By

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

    def __init__(self, url: str, recipe_scraper: scraper):
        self.recipe_id = ""
        self.recipe_UUID = None
        self.recipe_name = ""
        self.ingredients = []
        self.planning_info = {}
        self.method = {}
        self.nutritional_info = {}
        self.url = url
        self.image_url = ""
        
        self.recipe_id, self.recipe_UUID = self.get_recipe_ids(url)
        self.get_data(recipe_scraper)

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

    def get_data(self, recipe_scraper: scraper):

            # Get main element which holds the recipe data
        main_recipe = locator(By.XPATH, "//div[(@class='post recipe')]")
        recipe_div = recipe_scraper.get_element(None, main_recipe, False)
        
        # Get the recipe name
        recipe_header = locator(By.XPATH,".//h1[(@class='heading-1')]")
        self.recipe_name = recipe_scraper.get_item_data(recipe_div, recipe_header)

        # Get the ingredients
        ingreds_section = locator(By.XPATH, ".//section[(@class='recipe__ingredients col-12 mt-md col-lg-6')]")
        ingred_list = locator(By.XPATH, ".//li[(@class='pb-xxs pt-xxs list-item list-item--separator')]")
        
        self.ingredients = recipe_scraper.get_data_as_list(recipe_div, 
                                    ingreds_section, ingred_list)
        

        # Get the recipe method
        method_section = locator(By.XPATH, ".//section[(@class='recipe__method-steps mb-lg col-12 col-lg-6')]")
        method_steps = locator(By.XPATH, ".//li[(@class='pb-xs pt-xs list-item')]")
        method_step_num = locator(By.XPATH, "./span[(@class='mb-xxs heading-6')]")
        method_step_info = locator(By.TAG_NAME, "p")
        
        self.method=recipe_scraper.get_data_as_dict(recipe_div, method_section,
            method_steps, method_step_num, method_step_info)

        # Get the nutritional info
        nutrition_items = locator(By.XPATH, ".//tr[(@class='key-value-blocks__item')]")
        nutrition_key = locator(By.XPATH, "./td[(@class='key-value-blocks__key')]")
        nutrition_value = locator(By.XPATH, "./td[(@class='key-value-blocks__value')]")

        self.nutritional_info=recipe_scraper.get_data_as_dict(recipe_div, None, 
            nutrition_items, 
            nutrition_key, 
            nutrition_value)

        # Get the prep / cook time
        planning_div = locator(By.XPATH, ".//div[(@class='icon-with-text time-range-list cook-and-prep-time post-header__cook-and-prep-time')]")
        planning_items = locator(By.XPATH, ".//li[(@class='body-copy-small list-item')]")
        planning_text = locator(By.XPATH, ".//span[(@class='body-copy-bold mr-xxs')]")
        planning_time = locator(By.XPATH, ".//time")

        self.planning_info = self.nutritional_info=recipe_scraper.get_data_as_dict(
            recipe_div, planning_div, planning_items, planning_text, planning_time)

        # Get the recipe image
        image_locator = locator(By.XPATH, ".//img[(@class='image__img')]")
        self.image_url = recipe_scraper.get_image_url(recipe_div, image_locator)
