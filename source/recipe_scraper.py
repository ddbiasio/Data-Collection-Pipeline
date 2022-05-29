import configparser
from package.scraper.scraper import Locator
from package.scraper.scraper import Scraper
from package.storage.db_storage import DBStorage
from selenium.webdriver.common.by import By 
from string import Template
import uuid
import recipe_constants as rc
import logging

class RecipeScraper(Scraper):
    """
    This class extends the Scraper class with specific 
    details of the web site (www.bbcgoodfood.com) and uses
    the bases methods to extract the details of the pages
    to be scraped

    Attributes
    ----------
    page_data : list
        A list of dictionaries populated by the web scraper
    
    Methods
    -------
    scrape_pages(item_links: list, page_def: dict, image_loc: Locator) -> None
    get_recipe_data(keyword_search: str, num_pages: int) -> None

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
    
        # XPATH details for pagination control
        self.__page_numbers_loc = rc.PAGE_NUMBERS_LOC

        # initialise with the base website
        super().__init__(rc.WEBSITE_URL)
        self.dismiss_popup(self.__xp_accept_button)

    def get_num_pages(self, num_pages):

        if num_pages == 0:
            # Get the total results pages so we know how many iterations
            # Mainly for the status bar as we could just keep going
            # until we hit a no results page!
            pages = self.get_elements(self.__page_numbers_loc)
            if len(pages) == 0:
                # only one page and it is just text
                return 1
            else:
                # num_pages = self._Scraper__driver.execute_script("return arguments[0].textContent",  pages[-1])
                return int(pages[-1].text.split("\n")[-1]) + 1
        else:
            return num_pages

    def get_urls(self, keyword_search: str, page_num: int) -> list:
        

        page_urls = []
        # Sets the URL for results pages by page num
        results_mappings = {'pagenum': page_num, 'searchwords': keyword_search}
        results_page = Template(self.__results_template).substitute(**results_mappings)
        # Get the links from the recipe cards in search results   
        if self.go_to_page_url(results_page, self.__invalid_page):
            page_urls = self.get_item_links( self.__results_loc)

        return page_urls

    def scrape_page(self, url: str) -> dict:
        """_summary_

        Parameters
        ----------
        url : str
            URL of the page to scrape
        item_id : str
            The item ID of the page

        Returns
        -------
        dict
            Dictionary of the data scraped from the page
        """
        try:
            page_dict = {}
            # go to the URL
            if self.go_to_page_url(url, self.__invalid_page):                
                # populate dictionary from the page
                page_dict = self.get_page_data(self.__recipe_dict)
                page_dict.update({"item_id": url.rsplit('/', 1)[-1]})
                page_dict.update({"item_UUID": uuid.uuid4()})
                page_dict.update({"image_urls": self.get_image_url(self.__images)})
                return page_dict
            else:
                logging.warning(f"Page not found: {url}")
        except RuntimeError as e:
            print(f"Error scraping page {url} {e.args[0]}")
        finally:
            # return the dictionary
            return page_dict

    def search_recipes(
            self,
            keyword_search: str,
            num_pages: int) -> int:

        """
        Executes a recipe search using `keyword_search`

        Parameters
        ----------
        keyword_search : str
            The keywords to search for recipes, multiple words should be concatenated with +

        """
        # Search for recipes    
        search_mappings = {'searchwords': keyword_search}
        search_url = Template(self.__search_template).substitute(**search_mappings)
        if self.search(search_url, self.__results_loc):
            return self.get_num_pages(num_pages)
        else:
            return 0
