import configparser
from .scraper import Locator
from .scraper import Scraper
from selenium.webdriver.common.by import By 
from string import Template
import uuid
from . import recipe_constants as rc

class RecipeScraper(Scraper):
    """
    This class extends the Scraper class with specific 
    details of the web site (www.bbcgoodfood.com) and uses
    the bases methods to extract the details of the pages
    to be scraped

    Attributes
    ----------
    __recipe_dict: dict
        A dictionary which provides the structure for the output dictionary
    page_data: list
        A list of dictionaries popukated with recipe data from the website
    
    

    """


    def __init__(self):

        # Dictionary which provides the structure for the output dictionary
        # key = output dictionary key
        # value = locator details for output dictionary values
        self.__recipe_dict = {
            "recipe_name": rc.RECIPE_NAME_LOC,
            "ingredients": [("ingredient", rc.INGREDIENTS_LOC)],
            "method": {
                "list_loc": rc.METHOD_STEPS_LOC,
                "dict_keys": ["method_step", "method_instructions"],
                "dict_values": [rc.METHOD_STEP_KEY_LOC,rc.METHOD_STEP_DETAIL]
            },
            "nutritional_info": {
                "list_loc": rc.NUTRITIONAL_LIST_LOC,
                "dict_keys": ["nutritional_info", "nutritional_value"],
                "dict_values": [rc.NUTRITIONAL_INFO_LOC,rc.NUTRITIONAL_VALUE_LOC]     
                },
            "planning_info": {
                "list_loc": rc.PLANNING_LIST_LOC,            
                "dict_keys": ["prep_stage", "prep_time"],
                "dict_values": [rc.PLANNING_LIST_TASK,rc.PLANNING_LIST_TIME]     
                  }
        }

        self.page_data = []

        # Set up variables to be passed to scraping methods
        self.__xp_accept_button = rc.ACCEPT_BUTTON_LOC

        self.__dismiss_sign_in_button = rc.DISMISS_SIGN_IN_LOC
        self.__dismiss_sign_in_iframe = rc.SIGN_IN_IFRAME_LOC

        # Set search template based on 
        # https://www.bbcgoodfood.com/search?q=chicken
        # Multiple word searches should be separated by plus
        self.__search_template = rc.SEARCH_URL_TEMPLATE

        # Set results template based on 
        # https://www.bbcgoodfood.com/search/recipes/page/2/?q=chicken&sort=-relevance
        # Multiple word searches should be separated by plus
        self.__results_template = rc.RESULTS_URL_TEMPLATE
    
        self.__results_loc = rc.RESULT_CARDS_LOC
        # XPATH details for the no results element
        self.__xp_no_results = rc.NO_RESULTS_DIV_LOC

        self.__images = rc.IMAGES_LOC

        # XPATH details for the invalid page content
        self.__invalid_page = rc.ERROR_PAGE_DIV_LOC

        # initialise with the base website
        super().__init__(rc.WEBSITE_URL)
        self.dismiss_popup(self.__xp_accept_button)

    def scrape_pages(
        self,
        item_links: list,
        page_def: dict, 
        image_loc: Locator) -> None:

        """
        Scrapes a list of URLS in range to num_pages
        using the page definition dictionary provided
        and saves each page as a JSON file
        """
        for link in item_links:

            self.go_to_page_url(link, self.__invalid_page)
            page_dict = self.get_page_data(page_def)
            item_id = link.rsplit('/', 1)[-1]
            page_dict.update({"item_id": link.rsplit('/', 1)[-1]})
            page_dict.update({"item_UUID": uuid.uuid4()})
            page_dict.update({"image_urls": self.get_image_url(image_loc)})

            self.page_data.append(page_dict)
            
            break

    def get_recipe_data(
            self, 
            keyword_search: str, 
            num_pages: int):

        try:
            # Search for recipes    
            search_mappings = {'searchwords': keyword_search}
            search_url = Template(self.__search_template).substitute(**search_mappings)
            if self.search(search_url, self.__xp_no_results):

                # Get the links from the recipe cards in search results
                search_results_locator = self.__results_loc

                # Get the first page of links- already on this page
                # and only loop from p2 onwards
                urls = self.get_item_links(search_results_locator)
                for page in range(2, num_pages + 1):
                    # Sets the URL for results pages by page num
                    results_mappings = {'pagenum': page, 'searchwords': keyword_search}
                    results_page = Template(self.__results_template).substitute(**results_mappings)
                
                    if self.go_to_page_url(results_page, self.__invalid_page):
                        urls = self.get_item_links(search_results_locator)
                
                if len(urls) > 1:
                    # Iterate through the page URLS n times and scrape the data
                    # Writing the files to the defined data folder
                    self.scrape_pages(
                        urls, 
                        self.__recipe_dict, 
                        self.__images)
            else:
                print(f"No results for {keyword_search}")
        finally:
            self.quit()