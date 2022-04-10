import os
from typing import Union
import uuid
import json
import urllib.request
from scraper import scraper, locator
from recipe import Recipe
from selenium.webdriver.common.by import By

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

def init_scraper() -> Union[scraper, None]:
    """
    Initialises the scraper object, accept cookies and set url templates for search / navigate

    Parameters
    ----------
    None

    Returns
    -------
    scraper

    """
    try:

        # Set up variables to be passed to scraping methods
        xp_accept_button = "//button[(@class=' css-1x23ujx')]"

        my_scraper = scraper("https://www.bbcgoodfood.com/")

        if my_scraper is not None:
            my_scraper.accept_cookies(xp_accept_button)

            # Set search template based on https://www.bbcgoodfood.com/search?q=chicken
            # Multiple word searches should be separated by plus
            my_scraper.search_template = "https://www.bbcgoodfood.com/search?q=$searchwords"

            # Set results template based on https://www.bbcgoodfood.com/search/recipes/page/2/?q=chicken&sort=-relevance
            # Multiple word searches should be separated by plus
            my_scraper.results_template = "https://www.bbcgoodfood.com/search/recipes/page/$pagenum/?q=$searchwords&sort=-relevance"

        return my_scraper

    except Exception as e:
        print(str(e))
        return None

def run_search(my_scraper: scraper, keyword_search: str):
    """
    Runs the scraper search method using the defined keyword(s)

    Parameters
    ----------
    keyword_search: str
        Search keyword or words (must be joined by '+' character)

    Returns
    -------
    bool

    """
    try:
        xp_no_results = "//div[(@class='col-12 template-search-universal__no-results')]"

        #Search for recipes    
        search_mappings = {'searchwords': keyword_search}
        return my_scraper.search(search_mappings, xp_no_results)
    except Exception as e:
        print(str(e))

def create_folder(folder_name: str):
    """
    Creates a folder if it doesn't exist already

    Parameters
    ----------
    folder_name: str
        The name of the folder to create (full path should be provided)

    """
    #create folder
    if not os.path.exists(folder_name):
            os.mkdir(folder_name)

def set_links(my_scraper: scraper):
    """
    Populates the item_links attribute from the recipe card elements in search results

    Parameters
    ----------
    my_scraper: scraper
        A scraper object initialised for the BBC Good Food website after a successful search

    Returns
    -------
    None

    """
    try:
        search_results_locator = locator(By.XPATH, 
            "//a[(@class='body-copy-small standard-card-new__description')]")

        for page in range(1, 2):
            results_mappings = {'pagenum': page, 'searchwords': keyword_search}
            if my_scraper.go_to_page_num(results_mappings):
                my_scraper.get_item_links(search_results_locator)

    except RuntimeError as e:
        print(str(e))

def get_data(my_scraper: scraper):

    """
    Populates the data_dict attribute with recipe information from the URLS in item_links list

    Parameters
    my_scraper: scraper
        A scraper object with its item_links list populated with recipe page URLs

    Returns
    -------
    None
    """
    try:
        for idx, link in enumerate(my_scraper.item_links):          
            if idx == 2:                                   
                #adding a break here so not looping through all during dev/test cycle
                break
            my_scraper.go_to_page_url(link)
            # Instantiate the recipe object which will then fill the properties with recipe data
            this_recipe = Recipe(link, my_scraper)              
            # Add the recipe dictionary and images to the relevant scraper lists
            my_scraper.data_dicts.append(dict(this_recipe.__dict__))
            my_scraper.image_links.append({this_recipe.__dict__['recipe_id']: this_recipe.image_url})

    except RuntimeError as e:
        print(str(e))

def save_data(my_scraper: scraper):

    """
    Saves the recipe data in json format and downloads and saves each associated image

    Parameters
    ----------
    my_scraper: scraper
        A scraper object that has successfully populated the data_dict with recipe information

    Returns
    -------
    None

    """
    try:
        # Setup folders
        root_folder = './raw_data'
        data_folder = f'{root_folder}/{keyword_search}'
        images_folder = f'{root_folder}/{keyword_search}/images'

        create_folder(root_folder)
        create_folder(data_folder)
        create_folder(images_folder)

        for idx, recipe_dict in enumerate(my_scraper.data_dicts):
            file_name = f"{recipe_dict['recipe_id']}.json"
            with open(f"{data_folder}/{file_name}", "w") as outfile:
                json.dump(my_scraper.data_dicts[idx], outfile, cls=UUIDEncoder, indent=4)

        for item in my_scraper.image_links:

            for key, value in item.items():
                file_name = key
                image_url = value
                # Download the file from `url` and save it locally under `file_name`:
                urllib.request.urlretrieve(image_url, f"{images_folder}/{file_name}.jpg")

        my_scraper.quit()
        
    except RuntimeError as e:
        print(str(e))

if __name__ == "__main__":

    # Put it all together and run the scraper for www.bbcgoodfood.com

    try:
        # Set the keyword search, multiple search items should be joined by '+'
        keyword_search = "chicken"

        # Set up the scraper
        my_scraper = init_scraper()

        # If init failed we won't have a scraper object
        if my_scraper is not None:

            # Run the search and it it returns results then get the data from the associated web pages
            if run_search(my_scraper, keyword_search):
                # Getting the recipe page urls
                set_links(my_scraper)
                # Getting the data for each recipe and putting it in the dictionary
                get_data(my_scraper)
                # Saving the dictionary (in json format) and images locally
                save_data(my_scraper)

        else:
            print("No recipes found")

    except Exception as e:
        print(str(e))

