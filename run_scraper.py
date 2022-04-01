from logging import root
import time
import os
import uuid
import json
import urllib.request
from scraper import scraper
from recipe import recipe

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

def init_scraper() -> scraper:
    """
    Initialises the scraper object, accept cookies and set url templates for search / navigate
    
    Parameters
    ----------
    None

    Returns
    -------
    scraper

    """

    # Set up variables to be passed to scraping methods
    xp_accept_button = "//button[(@class=' css-1x23ujx')]"

    my_scraper = scraper("https://www.bbcgoodfood.com/")
    my_scraper.accept_cookies(xp_accept_button)

    # Set search template based on https://www.bbcgoodfood.com/search?q=chicken
    # Multiple word searches should be separated by plus
    my_scraper.search_template = "https://www.bbcgoodfood.com/search?q=$searchwords"

    # Set results template based on https://www.bbcgoodfood.com/search/recipes/page/2/?q=chicken&sort=-relevance
    # Multiple word searches should be separated by plus
    my_scraper.results_template = "https://www.bbcgoodfood.com/search/recipes/page/$pagenum/?q=$searchwords&sort=-relevance"

    return my_scraper

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

    xp_no_results = "//div[(@class='col-12 template-search-universal__no-results')]"

    #Search for recipes    
    search_mappings = {'searchwords': keyword_search}
    return my_scraper.search(search_mappings, xp_no_results)

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

    xp_search_results_elements = "//a[(@class='body-copy-small standard-card-new__description')]"

    for page in range(1, 2):
        results_mappings = {'pagenum': page, 'searchwords': keyword_search}
        if my_scraper.go_to_page_num(results_mappings):
            my_scraper.get_item_links(xp_search_results_elements, page)

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

    for idx, link in enumerate(my_scraper.item_links):
        
        if idx == 2:                                   
            #adding a break here so not looping through all during dev/test cycle
            break

        my_scraper.go_to_page_url(link)
        recipe_object = recipe()

        #Get IDs and URL
        recipe_object.recipe_id, recipe_object.recipe_UUID = recipe_object.get_recipe_ids(link)
        recipe_object.url = link

        # Get main element which holds the recipe data
        xp_main_recipe_div = "//div[(@class='post recipe')]"
        recipe_div = my_scraper.get_element(xp_main_recipe_div)
        
        # Get the recipe name
        xp_recipe_header = ".//h1[(@class='heading-1')]"
        recipe_object.recipe_name = my_scraper.get_child_element(recipe_div, xp_recipe_header).text

        # Get the ingredients
        xp_ingreds_section = ".//section[(@class='recipe__ingredients col-12 mt-md col-lg-6')]"
        xp_ingred_list = ".//li[(@class='pb-xxs pt-xxs list-item list-item--separator')]" 
        
        ingredient_section = my_scraper.get_child_element(recipe_div, xp_ingreds_section)
        ingredients_list = my_scraper.get_child_elements(ingredient_section, xp_ingred_list)

        for ingredient in ingredients_list:
            recipe_object.ingredients.append(ingredient.text)

        # Get the recipe method
        xp_method_section = ".//section[(@class='recipe__method-steps mb-lg col-12 col-lg-6')]"
        xp_method_steps = ".//li[(@class='pb-xs pt-xs list-item')]"
        xp_method_step_num = "./span[(@class='mb-xxs heading-6')]"
        xp_method_step_info = "p"

        method_section = my_scraper.get_child_element(recipe_div, xp_method_section)
        method_steps = my_scraper.get_child_elements(method_section, xp_method_steps)

        for step in method_steps:
            step_num = my_scraper.get_child_element(step, xp_method_step_num).text
            step_details = my_scraper.get_child_element_bytag(step, xp_method_step_info)
        
            recipe_object.method.update({step_num: step_details.text})

        # Get the nutritional info
        xp_nutrition_items = ".//tr[(@class='key-value-blocks__item')]"
        xp_nutrition_key = "./td[(@class='key-value-blocks__key')]"
        xp_nutrition_value = "./td[(@class='key-value-blocks__value')]"
        nutrition_items = my_scraper.get_child_elements(recipe_div, xp_nutrition_items)
        
        for item in nutrition_items:
            nutrition_item = my_scraper.get_child_element(item, xp_nutrition_key).text
            nutrition_value = my_scraper.get_child_element(item, xp_nutrition_value).text

            recipe_object.nutritional_info.update({nutrition_item: nutrition_value})

        # Get the prep / cook time
        xp_planning_div = ".//div[(@class='icon-with-text time-range-list cook-and-prep-time post-header__cook-and-prep-time')]"
        xp_planning_items = ".//li[(@class='body-copy-small list-item')]"
        xp_planning_text = ".//span[(@class='body-copy-bold mr-xxs')]"
        xp_planning_time = ".//time"
        
        planning_div = my_scraper.get_child_element(recipe_div, xp_planning_div)
        planning_items = my_scraper.get_child_elements(planning_div, xp_planning_items)
        for planning_item in planning_items:
            planning_text = my_scraper.get_child_element(planning_item, xp_planning_text).text
            planning_time = my_scraper.get_child_element(planning_item, xp_planning_time).text
        
        recipe_object.planning_info.update({planning_text.replace(":", ""): planning_time})

        recipe_object.image_url = my_scraper.get_image_url(recipe_div, ".//img[(@class='image__img')]")
    
        recipe_id = recipe_object.__dict__['recipe_id']
        recipe_dict = {recipe_id: recipe_object.__dict__}
        my_scraper.data_dict.update(recipe_dict)

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

    # Setup folders
    root_folder = './raw_data'
    data_folder = f'{root_folder}/{keyword_search}'
    images_folder = f'{root_folder}/{keyword_search}/images'

    create_folder(root_folder)
    create_folder(data_folder)
    create_folder(images_folder)

    for key in my_scraper.data_dict:
        file_name = key
        image_url = my_scraper.data_dict[key]['image_url']

        # Download the file from `url` and save it locally under `file_name`:
        urllib.request.urlretrieve(image_url, f"{images_folder}/{file_name}.jpg")

    with open(f"{data_folder}/data.json", "w") as outfile:
        json.dump(my_scraper.data_dict, outfile, cls=UUIDEncoder, indent=4)


if __name__ == "__main__":

    # Put it all together and run the scraper for www.bbcgoodfood.com

    try:
        # Set the keyword search, multiple search items should be joined by '+'
        keyword_search = "chicken"

        # Set up the scraper
        my_scraper = init_scraper()

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

        my_scraper._driver.quit()
        
    except Exception as e:
        print(str(e))

