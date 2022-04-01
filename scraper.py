from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from string import Template
from recipe import recipe
import os

class scraper:

    """
    This class provides functions for web scraping

    ...
    Attributes
    ----------
        base_url : str
            The initial url to be loaded as starting point for web scraping
        search_url: str
            The url for executing a search
        search_template: str
            A string providing a template for the search URL
        results_template: str
            A string providing a template for the search results URL
        item_links: list
            A list of URLS obtained from the website search
        data_dict: dict
            A dictionary containing data from each item page scraped

        _driver : WebDriver
            The 

    Methods
    -------
        accept_cookies(self, consent_button: str, consent_iframe = None: str) -> None
            Locates a button within a frame (optional) and executes the click to accept cookies

        search(self, search_subs: dict, no_results: str = None) -> bool
            Executes a search using the defined search url

        get_item_links(self, search_items: str) -> None
            Saves the URLs for each item in a page of the search results

        go_to_page_num(self, results_subs: dict) -> bool
             Navigates to a page generated from url template and substitute values

        go_to_page_url(self, url: str) -> bool
            Navigates to the url for a selected item

        get_element(self, element_xpath: str) -> WebElement
            Finds an element using its XPATH

        get_child_element(self, element_xpath: str) -> WebElement
            Finds a child element of an element using its XPATH

        get_elements(self, element_xpath: str) -> list:
            Finds a list of elements using its XPATH

        get_child_elements(self, parent: WebElement, element_xpath: str) -> WebElement:
            Finds a list of child elements of an element using their XPATH

        get_child_element_bytag(self, parent: WebElement, element_tag: str) -> WebElement
            Finds child element using its tag name

        get_element_bytag(self, element_tag: str) -> WebElement
            Finds an element using its tag name
    """
    def __init__(self, url: str) -> None:

        """
        Parameters
        ----------
        None

        """
        self.base_url = url
        self.search_query_string = ""
        self.search_template = None
        self.results_template = None

        self.item_links = []
        self.data_dict = {}
        self._driver = None

        # initiate the session
        self._driver = webdriver.Firefox()
        self._driver.get(self.base_url)

    def accept_cookies(self, consent_button: str, consent_iframe: str = None) -> None:
        """
        Locates a button within a frame (optional) and executes the click to accept cookies

        Parameters
        ----------
        consent_button: str
            XPATH for the Accept Cookies button
        consent_iframe = None: str
            ID for the frame where consent buttons are displayed

        Returns
        -------
        None

        """
        try:
            if consent_iframe != None:
                consent_frame = WebDriverWait(self._driver, 10).until(EC.visibility_of_element_located((By.ID, consent_iframe)))
                self._driver.switch_to.frame(consent_frame)

            # This additional wait may be required to ensure the buttons are accessible
            accept_button = WebDriverWait(self._driver, 10).until(EC.element_to_be_clickable((By.XPATH, consent_button)))
            accept_button.click()

            self._driver.switch_to.default_content()

        except NoSuchElementException:
            # If the element is not there then cookies must have been accepted before
            return

        except StaleElementReferenceException:
            # This is being thrown intermittently - there is no other navigation etc.
            # which would case this so maybe something in page load.  Retry when this occurs
            accept_button = WebDriverWait(self._driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//button[(@class=' css-1x23ujx')]")))
            accept_button.click()     

    def search(self, search_subs: dict, no_results: str = None) -> bool:
        
        """
        Executes a search the a search URL generated from url template and substitute values
        
        Parameters
        ----------
        search_subs: dict
            A dictionary of mappings of {searchwords: str} to substitute in the search URL template
        no_results: str
            XPATH for the element displaying no results message

        Returns
        -------
        bool

        """
        search_url=Template(self.search_template).substitute(**search_subs)

        self._driver.get(search_url)

        if no_results != None:
            try:               
                #if the no results div exists then search returned no results
                no_results_element = self._driver.find_element(by=By.XPATH, value=no_results)
                return False

            except NoSuchElementException:
                # if the no results div does not exist then search returned results
                return True
        else:
            return True

    def get_item_links(self, search_items: str) -> None:

        """
        Saves the URLs for each item in a page of the search results

        Parameters
        ----------
        search_items:
            XPATH for the search result elements on the page

        Returns
        -------
        None

        """
        # This assumes that results are displayed in a standard group of elements
        # and that each search result item will have an href attribute containing the link
        # to the item page

        #find all the search result items
        items = self._driver.find_elements(by=By.XPATH, value=search_items)

        for idx, item in enumerate(items):
            #go to each recipe and get the link and add to list
            item_url = item.get_attribute("href")
            self.item_links.append(item_url)

    def go_to_page_num(self, results_subs: dict) -> bool:
        """
        Navigates to a page generated from url template and substitute values
 
        Parameters
        ----------
        results_subs : dict
            A dictionary of values {pagenum: int, searchwords: str} to substitute in the page URL template

        Returns
        -------
        bool
               
        """
        try:
            page_url = Template(self.results_template).substitute(**results_subs)

            self._driver.get(page_url)
            return True

        except TimeoutException:
            return False

    def go_to_page_url(self, url: str) -> bool:
        """
        Navigates to the url for a selected item


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
        except TimeoutException:
            return False

    def get_element(self, element_xpath: str) -> WebElement:
        """
        Finds an element using its XPATH

        Parameters
        ----------
        element_xpath: str
            The XPATH of the element to find
        
        Returns
        -------
        WebElement

        """

        return self._driver.find_element(by=By.XPATH, value=element_xpath)

    def get_child_element(self, parent: WebElement, element_xpath: str) -> WebElement:

        """
        Finds a child element of an element using its XPATH

        Parameters
        ----------
        parent: WebElement
            The parent element
        element_xpath: str
            The XPATH of the element to find
        
        Returns
        -------
        WebElement

        """

        return parent.find_element(by=By.XPATH, value=element_xpath)

    def get_elements(self, element_xpath: str) -> list:
        """
        Finds a list of elements using its XPATH

        Parameters
        ----------
        element_xpath: str
            The XPATH of the element to find
        
        Returns
        -------
        list

        """

        return self._driver.find_elements(by=By.XPATH, value=element_xpath)

    def get_child_elements(self, parent: WebElement, element_xpath: str) -> WebElement:
        """
        Finds a list of child elements of an element using their XPATH

        Parameters
        ----------
        parent: WebElement
            The parent element
        element_xpath: str
            The XPATH relative)(of the elements to find
        
        Returns
        -------
        list
        
        """

        return parent.find_elements(by=By.XPATH, value=element_xpath)
    
    def get_child_element_bytag(self, parent: WebElement, element_tag: str) -> WebElement:

        """
        Finds child element using its tag name

        Parameters
        ----------
        parent: WebElement
            The parent element
        element_xpath: str
            The tag of the element to find
        
        Returns
        -------
        WebElement

        """
        return parent.find_element(by=By.TAG_NAME, value=element_tag)

    def get_element_bytag(self, element_tag: str) -> WebElement:

        """
        Finds an element using its tag name

        Parameters
        ----------
        element_xpath: str
            The tag of the element to find
        
        Returns
        -------
        WebElement

        """
        return self._driver.find_element(by=By.TAG_NAME, value=element_tag)

    def get_image_url(self, parent: WebElement, image_xpath: str) -> str:
        """
        Gets the URL associated with an image

        Parameters
        ----------
        parent: WebElement
            The parent element of the image element
        image_xpath: str
            The XPATH of the image element

        Returns
        -------
        str
        """
        return parent.find_element(by=By.XPATH, 
        value=image_xpath).get_attribute('src').split('?', 1)[0]

