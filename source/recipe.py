from typing import Dict, List
import uuid
from scraper import scraper
from scraper import locator
from selenium.webdriver.common.by import By

class Recipe():
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
        self.ingredients: List[str] = []
        self.planning_info: Dict[str, str] = {}
        self.method: Dict[str, str] = {}
        self.nutritional_info: Dict[str, str] = {}
        self.url: str = url
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
        recipe_div = recipe_scraper.get_element(main_recipe)
        
        # Get the recipe name
        recipe_header = locator(By.XPATH,".//h1[(@class='heading-1')]")
        self.recipe_name = recipe_scraper.get_child_element(recipe_div, recipe_header).text

        # Get the ingredients
        ingreds_section_loc = locator(By.XPATH, ".//section[(@class='recipe__ingredients col-12 mt-md col-lg-6')]")
        ingred_list_loc = locator(By.XPATH, ".//li[(@class='pb-xxs pt-xxs list-item list-item--separator')]")
        
        ingred_section = recipe_scraper.get_child_element(recipe_div, ingreds_section_loc)
        ingred_list = recipe_scraper.get_child_elements(ingred_section, ingred_list_loc)
        
        for ingredient in ingred_list:
            self.ingredients.append(ingredient.text)

        # Get the recipe method
        method_section_loc = locator(By.XPATH, ".//section[(@class='recipe__method-steps mb-lg col-12 col-lg-6')]")
        method_steps_loc = locator(By.XPATH, ".//li[(@class='pb-xs pt-xs list-item')]")
        method_step_num_loc = locator(By.XPATH, "./span[(@class='mb-xxs heading-6')]")
        method_step_info_loc = locator(By.TAG_NAME, "p")
        
        method_section = recipe_scraper.get_child_element(recipe_div, method_section_loc)
        method_steps = recipe_scraper.get_child_elements(method_section, method_steps_loc)

        for step in method_steps:
            method_step_num = recipe_scraper.get_child_element(step, method_step_num_loc).text
            method_step_info = recipe_scraper.get_child_element(step, method_step_info_loc).text
            self.method.update({method_step_num: method_step_info})

        # Get the nutritional info
        nutrition_items_loc = locator(By.XPATH, ".//tr[(@class='key-value-blocks__item')]")
        nutrition_key_loc = locator(By.XPATH, "./td[(@class='key-value-blocks__key')]")
        nutrition_value_loc = locator(By.XPATH, "./td[(@class='key-value-blocks__value')]")

        nutrition_items = recipe_scraper.get_child_elements(recipe_div, nutrition_items_loc)

        for item in nutrition_items:
            nutrition_key = recipe_scraper.get_child_element(item, nutrition_key_loc).text
            nutrition_value = recipe_scraper.get_child_element(item, nutrition_value_loc).text
            self.nutritional_info.update({nutrition_key: nutrition_value})

        # Get the prep / cook time
        planning_div_loc = locator(By.XPATH, ".//div[(@class='icon-with-text time-range-list cook-and-prep-time post-header__cook-and-prep-time')]")
        planning_items_loc = locator(By.XPATH, ".//li[(@class='body-copy-small list-item')]")
        planning_text_loc = locator(By.XPATH, ".//span[(@class='body-copy-bold mr-xxs')]")
        planning_time_loc = locator(By.XPATH, ".//time")

        planning_div = recipe_scraper.get_child_element(recipe_div, planning_div_loc)
        planning_items = recipe_scraper.get_child_elements(planning_div, planning_div_loc)

        for plan_item in planning_items:
            planning_text = recipe_scraper.get_child_element(plan_item, planning_text_loc).text
            planning_time = recipe_scraper.get_child_element(plan_item, planning_time_loc).text
            self.planning_info.update({planning_text: planning_time})

        # Get the recipe image
        image_locator = locator(By.XPATH, ".//img[(@class='image__img')]")
        self.image_url = recipe_scraper.get_image_url(recipe_div, image_locator)
