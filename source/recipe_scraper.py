from package.scraper.scraper import Scraper
from string import Template
import uuid
import recipe_constants as rc
import logging
from package.utils.logger import log_class

@log_class
class RecipeScraper(Scraper):

    logger = logging.getLogger(__name__)
    """
    This class extends the Scraper class with specific 
    details of the web site (www.bbcgoodfood.com) and uses
    the bases methods to extract the details of the pages
    to be scraped

    Attributes
    ----------
    page_data : list
        A list of dictionaries populated by the web scraper

    """

    def __init__(self):

        self.page_data = []

        # Set search template based on 
        # https://www.bbcgoodfood.com/search?q=chicken
        # Multiple word searches should be separated by plus

        self.__search_template = rc.SEARCH_URL_TEMPLATE
        # Set results template based on 
        # https://www.bbcgoodfood.com/search/recipes/page/2/?q=chicken&sort=-relevance
        # Multiple word searches should be separated by plus
        self.__results_template = rc.RESULTS_URL_TEMPLATE

        # initialise with the base website
        super().__init__(rc.WEBSITE_URL)
        self.dismiss_popup(rc.ACCEPT_BUTTON_LOC)

    def get_num_pages(self, num_pages: int) -> int:
        """Gets the number of results pages using the navigation control

        Parameters
        ----------
        num_pages : int
            The number of search pages to be scraped

        Returns
        -------
        int
            Returns with num_pages if set, or the total number of results pages
        """
        if num_pages == 0:
            # Get the total results pages so we know how many iterations
            # Mainly for the status bar as we could just keep going
            # until we hit a no results page!
            pages = self.get_elements(rc.PAGE_NUMBERS_LOC)
            if len(pages) == 0:
                # only one page and it is just text
                return 1
            else:
                # num_pages = self._Scraper__driver.execute_script("return arguments[0].textContent",  pages[-1])
                return int(pages[-1].text.split("\n")[-1]) + 1
        else:
            return num_pages

    def get_urls(self, keyword_search: str, page_num: int) -> list:
        """Gets the URLS for recipe pages from one page of results

        Parameters
        ----------
        keyword_search : str
            The word(s) used for the search (used to build results page URL)
        page_num : int
            The page number to go to (used to build results page URL)

        Returns
        -------
        list
            List of URLs
        """        
        page_urls = []
        # Sets the URL for results pages by page num
        results_mappings = {'pagenum': page_num, 'searchwords': keyword_search}
        results_page = Template(self.__results_template).substitute(**results_mappings)
        # Get the links from the recipe cards in search results   
        if self.go_to_page_url(results_page, rc.ERROR_PAGE_DIV_LOC):
            page_urls = self.get_item_links(rc.RESULT_CARDS_LOC)

        return page_urls

    def get_page_data(self, url: str) -> dict:
        """Returns data from a single page in dictionary format

        Parameters
        ----------
        url : str
            URL of the page to scrape

        Returns
        -------
        dict
            Dictionary of the data scraped from the page
        """
        try:
            page_dict = {}
            # go to the URL
            if self.go_to_page_url(url, rc.ERROR_PAGE_DIV_LOC):                
                # populate dictionary from the page
                # Dictionary which provides the structure for the output dictionary
                # key = output dictionary key
                # value = locator details for output dictionary values
                page_dict = {
                    "recipe_name": self.get_element_text(rc.RECIPE_NAME_LOC),
                    "ingredients": self.get_elements_list("ingredient", rc.INGREDIENTS_LOC),
                    "method": self.get_elements_dict(
                        rc.METHOD_STEPS_LOC,
                        method_step=rc.METHOD_STEP_KEY_LOC, 
                        method_instructions=rc.METHOD_STEP_DETAIL),
                    "nutritional_info":  self.get_elements_dict(
                        rc.NUTRITIONAL_LIST_LOC, 
                        nutritional_info=rc.NUTRITIONAL_INFO_LOC, 
                        nutritional_value=rc.NUTRITIONAL_VALUE_LOC),
                    "planning_info":  self.get_elements_dict(
                        rc.PLANNING_LIST_LOC, 
                        prep_stage=rc.PLANNING_LIST_TASK, 
                        prep_time=rc.PLANNING_LIST_TIME)
                }
                page_dict.update({"item_id": url.rsplit('/', 1)[-1]})
                page_dict.update({"item_UUID": uuid.uuid4()})
                page_dict.update({"image_urls": self.get_image_url(rc.IMAGES_LOC)})
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
        if self.search(search_url, rc.RESULT_CARDS_LOC):
            return self.get_num_pages(num_pages)
        else:
            return 0
