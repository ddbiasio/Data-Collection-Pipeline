from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchElementException, StaleElementReferenceException, TimeoutException
from string import Template
import os

class locator:
    """
    This class allows an element locator to be defined as an object to pass to scraper find routines

    Attributes
    ----------
    locate_by: By
        A supported locator strategy e.g. XPATH, TAG_NAME etc.
    locate_value:
        Locator value for search result elements on the page e.g. the Xpath, the tag etc.
    
    """
    def __init__(self, locate_by: By, locate_value: str):
        self.locate_by = locate_by
        self.locate_value = locate_value



class scraper:

    """
    This class provides functions for web scraping

    ...
    Attributes
    ----------
        _driver : WebDriver
            The browser session used to scrape the website
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
        data_dicts: list
            A list of dictionaries for each item scraped
        image_links: list
            A list of dictionaries containing the URLS for item images


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

        get_element(self, parent: WebElement, locator: locator, is_list: bool) -> WebElement:
            Finds an element or elements using defined locator strategy and value, starting at parent if specified

        get_item_data(self, parent: WebElement, locator: locator) -> str:
            Returns text attribute using defined locator strategy and value, optional find within parent element

        get_data_as_list(self, parent: WebElement, 
                container_locator: locator, list_locator: locator) -> list:
            Returns a list of data items scraped from a list of elements 
            which may be located in a container element

        get_data_as_dict(self, parent: WebElement, container_locator: locator, 
                list_locator: locator, key_locator: locator, value_locator: locator) -> dict
            Returns a dictionary of data items scraped from a list of elements 
            which may be located in a container element
        
        get_image_url(self, parent: WebElement, locator: locator) -> str:
            Gets the URL associated with an image from the src attribute
    """
    def __init__(self, url: str) -> None:

        """
        Parameters
        ----------
        url: str
            The URL of the website to be scraped

        """
        self.base_url = url
        self.search_query_string = ""
        self.search_template = None
        self.results_template = None

        self.item_links = []
        self.data_dicts = []
        self.image_links = []
        self._driver = None

        try:
            # initiate the session
            self._driver = webdriver.Firefox()
            self._driver.get(self.base_url)
        except WebDriverException as e:
            # If something fails the close the driver and raise the exception
            self._driver.quit()
            raise RuntimeError(f"Failed to initialise scraper: {e.msg}") from e

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

        try:
            self._driver.get(search_url)
        except WebDriverException:
            raise RuntimeError("The search page could not be loaded")

        if no_results != None:
            try:               
                #if the no results div exists then search returned no results
                no_results_element = self._driver.find_element(by=By.XPATH, value=no_results)
                self._driver.quit()
                return False

            except NoSuchElementException:
                # if the no results div does not exist then search returned results
                return True
        else:
            return True

    def get_item_links(self, locator: locator) -> None:

        """
        Saves the URLs for each item in a page of the search results

        Parameters
        ----------
        locator: locator
            A supported locator strategy and value of the locator to find the element

        Returns
        -------
        None

        """
        # This assumes that results are displayed in a standard group of elements
        # and that each search result item will have an href attribute containing the link
        # to the item page

        #find all the search result items
        items = self.get_element(None, locator, True)

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

        except (TimeoutException, WebDriverException):
            raise RuntimeError(f"Unable to load page: {page_url}")


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
        except (TimeoutException, WebDriverException):
            raise RuntimeError(f"Unable to load page: {url}")

    def get_element(self, parent: WebElement, locator: locator, is_list: bool) -> WebElement:
        """
        Finds an element or elements using defined locator strategy and value, starting at parent if specified

        Parameters
        ----------
        locator: locator
            A supported locator strategy and value of the locator to find the element
        is_list: bool
            True when expecting a list of elements to be returned
        parent: 
            The parent web element
        
        Returns
        -------
        WebElement

        """
        search_in = self._driver if parent == None else parent

        try:
            if is_list:
                return search_in.find_elements(by=locator.locate_by, value=locator.locate_value)
            else:
                return search_in.find_element(by=locator.locate_by, value=locator.locate_value)
        except NoSuchElementException:
            raise RuntimeError(f"Element at {locator.locate_by} does not exist.")

    def get_item_data(self, parent: WebElement, locator: locator) -> str:
        """
        Returns text attribute using defined locator strategy and value, optional find within parent element

        Parameters
        ----------
        parent: 
            The parent web element        
        locator: locator
            A supported locator strategy and value of the locator to find the element

        
        Returns
        -------
        str

        """
        search_in = self._driver if parent == None else parent
        try:
            return search_in.find_element(by=locator.locate_by, value=locator.locate_value).text
        except NoSuchElementException:
            raise RuntimeError(f"Element at {locator.locate_by} does not exist.")

    def get_data_as_list(self, parent: WebElement, 
        container_locator: locator, list_locator: locator) -> list:
        """
        Returns a list of data items scraped from a list of elements 
        which may be located in a container element

        Parameters
        ----------
        container_locator: locator
            A supported locator strategy and value of the locator to find list container
        list_locator: locator
            A supported locator strategy and value of the locator to find the list

        Returns
        -------
        list

        """
        try:
            if container_locator == None:
                if parent == None:
                    container_locator = None
                else:
                    container_locator = parent
            else:
                list_container = self.get_element(parent, container_locator, False)
            
            list_items = self.get_element(list_container, list_locator, True)

            list_item_values = []
            for item in list_items:
                list_item_values.append(item.text)

            return list_item_values
            
        except NoSuchElementException:
            raise RuntimeError(f"Error getting list items: Element at {locator.locate_by} does not exist.")


    def get_data_as_dict(self, 
        parent: WebElement, 
        container_locator: locator, 
        list_locator: locator, 
        key_locator: locator,
        value_locator: locator) -> dict:
        """
        Returns a dictionary of data items scraped from a list of elements 
        which may be located in a container element

        Parameters
        ----------
        parent: WebElement
            The parent element of the image element
        container_locator: locator
            A supported locator strategy and value of the locator to find list container
        list_locator: locator
            A supported locator strategy and value of the locator to find the list
        key_locator: locator
            A supported locator strategy and value of the locator to find the elements for keys        
        value_locator: locator
            A supported locator strategy and value of the locator to find the elements for values        

        Returns
        -------
        dict

        """
        try:
            if container_locator == None:
                if parent == None:
                    list_container = None
                else:
                    list_container = parent
            else:
                list_container = self.get_element(parent, container_locator, False)
            
            list_items = self.get_element(list_container, list_locator, True)

            dict_item_values = {}
            for item in list_items:
                key_text = self.get_element(item, key_locator, False).text
                value_text = self.get_element(item, value_locator, False).text
            
                dict_item_values.update({key_text: value_text})

            return dict_item_values
            
        except NoSuchElementException:
            raise RuntimeError(f"Error getting dict items: Element at {locator.locate_by} does not exist.")

    def get_image_url(self, parent: WebElement, locator: locator) -> str:
        """
        Gets the URL associated with an image from the src attribute

        Parameters
        ----------
        parent: WebElement
            The parent element of the image element
        locator: locator
            A supported locator strategy and value of the locator to find the image element


        Returns
        -------
        str
        """

        search_in = self._driver if parent == None else parent
        try:
            return search_in.find_element(by=locator.locate_by, 
                value=locator.locate_value).get_attribute('src').split('?', 1)[0]

        except NoSuchElementException:
            raise RuntimeError(f"Error getting image: Element at {locator.locate_by} does not exist.")
