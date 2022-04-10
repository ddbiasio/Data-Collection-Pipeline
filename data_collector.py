from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
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
    def default(self, obj: object) -> hex:
        if isinstance(obj, uuid.UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)

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

class recipe_collector():

    """
    This class will scrape recipe information from the BBC Good Food website

    ...
    Attributes
    ----------
        _base_url : str
            The initial url to be loaded as starting point for web scraping
        data_dictionary : dict
            The data scraped from the website in dictionary format
        _driver : Driver
        
    Methods
    -------
        accept_cookies(none):
            Locates the Accept Cookies button and clicks it

        get_data(search_string : str)
            Main function to retrieve, navigate and scrape recipe data based on a key word search

        search_recipes(search_string : str) -> bool
            Executes a search for recipes on the home page

        get_recipes(url : str) -> dict
            Retrieves data from the specified URL

        get_recipe_links(self, page_num: int): -> list
            Gets the URLs for each recipe on a given page

        get_recipe_data(self, url: str): -> dict
            Gets the ingredients, method and other information for a single recipe
        
        go_to_page_num(self, page_num: int): -> bool
            Navigates to the page in search results by page number
        
        go_to_page_url(self, url: str) -> bool
            Navigates to a page by its URL (usually for a specific recipe)

    """
    def __init__(self, search_string: str) -> None:

        """
        Parameters
        ----------
        None

        """
        self._base_url = "https://www.bbcgoodfood.com/"
        self.data_dictionary = {}
        self._driver = None
        self.recipe_urls = []

        #initiate the session and accept cookies
        self._driver = webdriver.Firefox()
        self._driver.get(self._base_url)
        self.accept_cookies()
    
    def accept_cookies(self) -> None:
        """
        Locates the Accept Cookies button and clicks it

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        try:
            accept_button = WebDriverWait(self._driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//button[(@class=' css-1x23ujx')]")))
            accept_button.click()

        except NoSuchElementException:
            #if the element is not there then cookies must have been accepted before
            return

        except TimeoutError:
            #if timeout to get the button then cookies must have been accepted before
            return

        except StaleElementReferenceException:
            #This is being thrown intermittently - there is not other navigation etc.
            #which would case this so maybe something in page load.  Retry whrn this occurs
            accept_button = WebDriverWait(self._driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//button[(@class=' css-1x23ujx')]")))
            accept_button.click()     

    def search_recipes(self, search_string: str) -> bool:
        
        """
        Executes a search for recipes on the home page
        
        Parameters
        ----------
        search_string : str
            The keyword e.g. ingredient or meal type to search for

        Returns
        -------
        bool

        """
        # Multi word searches use a + between words
        search_string = search_string.replace(" ", "_")

        search_url = f"https://www.bbcgoodfood.com/search?q={search_string}"
        self._driver.get(search_url)

        try:
            #if the no results div exists then search returned no results
            no_results = self._driver.find_element(by=By.XPATH, value="//div[(@class='col-12 template-search-universal__no-results')]")
            return False

        except NoSuchElementException:
            #if the no results div does not exist then search returned results
            return True

    def get_recipe_links(self, page_num) -> None:

        """
        Returns the URLs for each recipe on a given page

        Parameters
        ----------
        page_num : str
            The page number within the search results pages to scrape links from

        Returns
        -------
        None

        """
        if self.go_to_page_num(page_num):

            #find all the recipe cards
            recipes = self._driver.find_elements(
                    by=By.XPATH, value='//a[(@class="body-copy-small standard-card-new__description")]'
                    )

            for idx, recipe in enumerate(recipes):
                #go to each recipe and get the link and add to list
                recipe_url = recipe.get_attribute("href")
                self.recipe_urls.append(recipe_url)

        else:
            print(f"Unable to navigate to page {page_num} of search results")

    def get_recipe_data(self, url: str) -> None:
        """
        Gets the ingredients, method and other information for a single recipe

        Parameters
        ----------
        url : str
            The URL of the recipe

        Returns:
            None

        """
        self._driver.get(url)
        recipe_object = recipe()

        recipe_div = self._driver.find_element(by=By.XPATH, value="//div[(@class='post recipe')]")

        recipe_object.recipe_id, recipe_object.recipe_UUID = recipe_object.get_recipe_ids(url)

        recipe_name = recipe_div.find_element(by=By.XPATH, value=".//h1[(@class='heading-1')]")

        ingredient_section = recipe_div.find_element(by=By.XPATH, value=".//section[(@class='recipe__ingredients col-12 mt-md col-lg-6')]")
        ingredients_list = ingredient_section.find_elements(by=By.XPATH, value=".//li[(@class='pb-xxs pt-xxs list-item list-item--separator')]")
        
        for ingredient in ingredients_list:
            recipe_object.ingredients.append(ingredient.text)
        
        method_section = recipe_div.find_element(by=By.XPATH, value=".//section[(@class='recipe__method-steps mb-lg col-12 col-lg-6')]")
        method_steps = method_section.find_elements(by=By.XPATH, value=".//li[(@class='pb-xs pt-xs list-item')]")

        for step in method_steps:
            step_num = step.find_element(by=By.XPATH, value="./span[(@class='mb-xxs heading-6')]")
            step_details = step.find_element(by=By.TAG_NAME, value="p")
        
            recipe_object.method.update({step_num.text: step_details.text})
        
        nutrition_items = recipe_div.find_elements(by=By.XPATH, value=".//tr[(@class='key-value-blocks__item')]")
        
        for item in nutrition_items:
            nutrition_item = item.find_element(by=By.XPATH, value="./td[(@class='key-value-blocks__key')]").text
            nutrition_value = item.find_element(by=By.XPATH, value="./td[(@class='key-value-blocks__value')]").text

            recipe_object.nutritional_info.update({nutrition_item: nutrition_value})

        planning_list = recipe_div.find_element(by=By.XPATH, value=".//div[(@class='icon-with-text time-range-list cook-and-prep-time post-header__cook-and-prep-time')]")

        planning_items = planning_list.find_elements(by=By.XPATH, value=".//li[(@class='body-copy-small list-item')]")
        for planning_item in planning_items:
            planning_text = planning_item.find_element(by=By.XPATH, value=".//span[(@class='body-copy-bold mr-xxs')]").text
            planning_time = planning_item.find_element(by=By.XPATH, value=".//time").text

            recipe_object.planning_info.update({planning_text.replace(":", ""): planning_time})

        recipe_object.url = url

        recipe_object.image_url = recipe_div.find_element(by=By.XPATH, 
            value=".//img[(@class='image__img')]").get_attribute('src').split('?', 1)[0]

        return recipe_object.__dict__

    def go_to_page_num(self, page_num: int) -> bool:
        """
        Navigates to the page in search results by page number
 
        Parameters
        ----------
        page_num : int
            The page number within search results to navigate to

        Returns
        -------
        bool
               
        """
        try:
            page_url = f"https://www.bbcgoodfood.com/search/recipes/page/{page_num}/?q=chicken&sort=-relevance"
            self._driver.get(page_url)
            return True

        except TimeoutError:
            return False

    def go_to_page_url(self, url: str) -> bool:
        """
        Navigates to the page for a selected item


        Parameters
        ----------
        url : str
            The URL of the page to navigate to

        Returns
        -------
        bool
            
        """
        try:
            self._driver.get(url)
            return True
        except TimeoutError:
            return False

    def close_session(self) -> None:
        self._driver.quit()


def run_the_scraper(search_string: str):
    """
    Main function to load the site and scrap recipe data based on a keyword search

    Parameters
    ----------
    search_string : str
        The ingredient, meal type or other relevant key word for the recipe search

    """ 
    my_scraper = recipe_collector(search_string)

    try:

        #execute the search
        if my_scraper.search_recipes(search_string):
            
            for page in range(1, 2):
                my_scraper.get_recipe_links(page)
                #loop through urls gathered to get recipe details
                #go to each item and scrape data

            print(f"Found {len(my_scraper.recipe_urls)} recipes relating to {search_string}")

            #create raw data folder
            if not os.path.exists('raw_data'):
                    os.mkdir('raw_data')

            #create sub-folder for this search
            data_folder = f'./raw_data/{search_string}'
            if not os.path.exists(data_folder):
                    os.mkdir(data_folder)

            images_folder = f'./raw_data/{search_string}/images'
            #create sub-folder for images
            if not os.path.exists(images_folder):
                    os.mkdir(images_folder)

            all_recipes = {}

            for idx, url in enumerate(my_scraper.recipe_urls):

                if idx == 2:                                   
                    #adding a break here so not looping through all during dev/test cycle
                    break

                recipe_dict = my_scraper.get_recipe_data(url)
                all_recipes.update(recipe_dict)

                file_name = recipe_dict['recipe_id']
                image_url = recipe_dict['image_url']

                # Download the file from `url` and save it locally under `file_name`:
                urllib.request.urlretrieve(image_url, f"{images_folder}/{file_name}.jpg")

            with open(f"{data_folder}/data.json", "w") as outfile:
                json.dump(all_recipes, outfile, cls=UUIDEncoder, indent=4)

        else:
            print(f"There were no recipes relating to {search_string}")
        
    except Exception as e:
        print(str(e))

    my_scraper.close_session()

if __name__ == "__main__":
    run_the_scraper("chicken")
