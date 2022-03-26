from re import S, search
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

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

        def get_recipe_links(self, page_num): -> list
            Gets the URLs for each recipe on a given page

        def get_recipe_data(self, url): -> dict
            Gets the ingredients, method and other information for a single recipe
        
        store_data_from_page() -> none
            Stores scraped data in the data dictionary

        go_to_page_num() -> bool
            Navigates to the page in search results by page number
        
        go_to_page_url() -> bool
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

        self.get_data(search_string)
    
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

    def get_data(self, search_string: str):
        """
        Main function to load the site and scrap recipe data based on a keyword search

        Parameters
        ----------
        search_string : str
            The ingredient, meal type or other relevant key word for the recipe search

        """
        try:

            #initiate the session and accept cookies
            self._driver = webdriver.Firefox()
            self._driver.get(self._base_url)
            self.accept_cookies()

            #execute the search
            if self.search_recipes(search_string):
                
                #initialise the list for the recipe URLs
                recipe_list = []

                for page in range(1, 3):
                    recipe_list += self.get_recipe_links(page)
                    #loop through items on page
                    #go to each item and scrape data

                print(f"Found {len(recipe_list)} recipes relating to {search_string}")
                print(recipe_list)
            else:
                print(f"There were no recipes relating to {search_string}")
           
        except Exception as e:
            print(str(e))

        self._driver.close()

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

    def get_recipe_links(self, page_num) -> list:

        """
        Returns the URLs for each recipe on a given page

        Parameters
        ----------
        page_num : str
            The page number within the search results pages to scrape links from

        Returns
        -------
        recipe_list : list
            A list of all the URLs from the page

        """
        if self.go_to_page_num(page_num):

            #find all the recipe cards
            recipes = self._driver.find_elements(
                    by=By.XPATH, value='//a[(@class="body-copy-small standard-card-new__description")]'
                    )

            recipe_links = []

            for idx, recipe in enumerate(recipes):
                #go to each recipe and get the link and add to list
                recipe_url = recipe.get_attribute("href")
                recipe_links.append(recipe_url)

            return recipe_links
        else:
            print(f"Unable to navigate to page {page_num} of search results")

    def get_recipe_data(self, url: str):
        """
        Gets the ingredients, method and other information for a single recipe

        Parameters
        ----------
        url : str
            The URL of the recipe

        Returns:
            Dictionary containing the recipe data

        """

    def store_data_from_page(self):
        """
        Stores scraped data in the data dictionary

        Parameters
        ----------
        None

        Returns
        -------
        None
        
        """
        pass

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

if __name__ == "__main__":
    my_scraper = recipe_collector("chicken")