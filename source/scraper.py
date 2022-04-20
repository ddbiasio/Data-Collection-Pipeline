from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from typing import List, Union
from utilities import UUIDEncoder
from utilities import file_ops
import uuid

class Locator:
    """
    This class allows an element Locator to be defined 
    as an object to pass to Scraper find routines

    Attributes
    ----------
    locate_by: str
        A supported Locator strategy e.g. XPATH, TAG_NAME etc.
    locate_value:
        Locator value for search result elements on the page 
        e.g. the Xpath, the tag etc.

    """
    def __init__(self, locate_by: str, locate_value: str):
        self.locate_by = locate_by
        self.locate_value = locate_value


class Scraper:

    """
    This class provides functions for web scraping

    ...
    Attributes
    ----------
        _driver : WebDriver
            The browser session used to -scrape the website
        base_url: str
            The initial url to be loaded as starting point for web scraping

    Methods
    -------
        accept_cookies(self, consent_button: str, 
                consent_iframe = None: str) -> None
            Locates a button within a frame (optional) 
            and executes the click to accept cookies

        search(self, search_url: str, no_results: str = None) -> bool
            Executes a search using the defined search url

        get_item_links(self, loc: Locator) -> list:
            Returns list of URLs for each item in a page of the search results

        go_to_page_url(self, url: str) -> bool
            Navigates to the web page identified by 'url'

        get_element_text(self, loc: Locator) -> str:
            Returns an element's text using the defined Locator

        get_element_list(self, loc: Locator) -> list[str]:
            Finds a list of elements using the defined Locator
            and returns the text of each in a list

        get_element_dict(get_elements_dict(
                self, 
                list_loc: Locator,
                key_loc: Locator,
                value_loc: Locator) -> dict:
            Finds a list of elements, and then finds key / value
            elements within each element and returns their values in
            a dictionary

        get_page_data(self, page_definition: dict) -> dict:
            Uses the page_definition to scrape a page for the
            data items described in the dictionary, where each key is a 
            data item for the page data

        get_image_url(self, parent: WebElement, loc: Locator) -> str
            Gets the URL associated with an image from the src attribute

        quit(self):
            Quits the session

    """
    def __init__(self, 
                url: str) -> None:

        """
        Parameters
        ----------
        url: str
            The URL of the website to be scraped

        """
        self.base_url = url

        try:
            # initiate the session
            self._driver = webdriver.Firefox()
            self._driver.get(self.base_url)

        except WebDriverException as e:
            # If something fails the close the driver and raise the exception
            # self._driver.quit()
            raise RuntimeError(f"Failed to initialise Scraper: {e.msg}") from e

    def accept_cookies(
            self,
            consent_button: Locator,
            consent_iframe: Locator = None) -> None:
        """
        Locates a button within a frame and executes the click to accept cookies

        Parameters
        ----------
        consent_button: str
            Locator for the Accept Cookies button
        consent_iframe = None: str
            Locator for the frame where consent buttons are displayed

        Returns
        -------
        None

        """
        try:
            if consent_iframe is not None:
                consent_frame = WebDriverWait(self._driver, 10).until(
                    EC.visibility_of_element_located(
                        (consent_iframe.locate_by, 
                        consent_iframe.locate_value)))
                self._driver.switch_to.frame(consent_frame)

            # This additional wait may be required to ensure 
            # the buttons are accessible
            accept_button = WebDriverWait(self._driver, 10).until(
                EC.element_to_be_clickable(
                    (consent_button.locate_by, 
                    consent_button.locate_value)))
            accept_button.click()

            self._driver.switch_to.default_content()

        except NoSuchElementException:
            # If the element is not there then cookies must have been 
            # accepted before
            return

        except StaleElementReferenceException:
            # This is being thrown intermittently
            # There is no other navigation etc.
            # which would case this so maybe something in page load.  
            # Retry when this occurs
            accept_button = WebDriverWait(self._driver, 30).until(
                EC.element_to_be_clickable(
                (By.XPATH, "//button[(@class=' css-1x23ujx')]")))
            accept_button.click()     

    def search(self, search_url: str, no_results: str = None) -> bool:

        """
        Executes a search with a search URL which should
        be in the correct format for the web site being scraped

        Parameters
        ----------
        search_url: str
            The URL which executes a search on the website
        no_results: str
            XPATH for the element displaying no results message

        Returns
        -------
        bool

        """
        try:
            self._driver.get(search_url)

            if not no_results:
                try:               
                    # if the no results div exists then search returned no results
                    no_results_element = self._driver.find_element(
                        by=By.XPATH, value=no_results)
                    self._driver.quit()
                    return False

                except NoSuchElementException:
                    # if the no results div does not exist 
                    # then search returned results
                    return True

        except WebDriverException:
            raise RuntimeError("The search page could not be loaded")
        else:
            return True

    def get_item_links(self, loc: Locator) -> list:

        """
        Returns a list of URLs for each item in a page of the search results

        Parameters
        ----------
        loc: Locator
            A supported Locator strategy and value of the Locator 
            to find the element

        Returns
        -------
        None

        """
        # This assumes that results are displayed in a standard group of elements
        # and that each search result item will have an href attribute 
        # containing the link to the item page

        # find all the search result items
        url_list = []
        items = self._driver.find_elements(
            by=loc.locate_by, value=loc.locate_value)

        for item in items:
            # go to each recipe and get the link and add to list
            item_url = item.get_attribute("href")
            url_list.append(item_url)
        return url_list

    def go_to_page_url(self, url: str) -> bool:
        """
        Navigates to the web page identified by 'url'


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

    def get_element_text(self, loc: Locator) -> str:
        """
        Returns an element's text using the defined Locator

        Parameters
        ----------
        parent:
            The parent web element
        loc: Locator
            A supported Locator strategy and value of the 
            Locator to find the element

        Returns
        -------
        WebElement

        """
        try:
            return self._driver.find_element(by=loc.locate_by,
                                            value=loc.locate_value).text

        except NoSuchElementException:
            raise RuntimeError(f"Element at {loc.locate_by} does not exist.")

    def get_element_list(self, loc: Locator) -> list[str]:
        """
        Finds a list of elements using the defined Locator
        and returns the text of each in a list

        Parameters
        ----------
        loc: Locator
            A supported Locator strategy and value of the 
            Locator to find the element

        Returns
        -------
        list[str]

        """
        list_values = []
        try:
            list_items = self._driver.find_elements(
                by=loc.locate_by, value=loc.locate_value)
            for item in list_items:
                list_values.append(item.text)
        except NoSuchElementException:
            raise RuntimeError(f"Elements at {loc.locate_by} does not exist.")
        finally:
            return list_values

    def get_elements_dict(
            self, 
            list_loc: Locator,
            key_loc: Locator,
            value_loc: Locator) -> dict:
        """
        Finds a list of elements, and then finds key / value
        elements within each element and returns their values in
        a dictionary
        Parameters
        ----------
        list_loc: Locator
            A supported Locator strategy and value of the 
            Locator to find the list elements
        key_loc: Locator
            A supported Locator strategy and value of the 
            Locator to find the key element
        value_loc: Locator
            A supported Locator strategy and value of the 
            Locator to find the value element
        Returns
        -------
        list[str]

        """
        dict_values = {}
        try:
            list_items = self._driver.find_elements(by=list_loc.locate_by, value=list_loc.locate_value)
            for item in list_items:
                try:
                    key_text = item.find_element(by=key_loc.locate_by, value=key_loc.locate_value).text
                except NoSuchElementException:         
                    raise RuntimeError(f"Element at {key_loc.locate_by} does not exist.")
                try:
                    value_text = item.find_element(by=value_loc.locate_by, value=value_loc.locate_value).text
                except NoSuchElementException:            
                    raise RuntimeError(f"Element at {value_loc.locate_by} does not exist.")
                dict_values.update({key_text: value_text})
        except NoSuchElementException:
            raise RuntimeError(f"Elements at {list_loc.locate_by} does not exist.")
        finally:
            return dict_values

    def get_page_data(self, page_definition: dict) -> dict:
        """
        Uses the page_definition to scrape a page for the
        data items described in the dictionary, where each key is a 
        data item for the page data

        Parameters
        ----------
        page_defintion: dict
            A dicitonary defining how page data will be located
            {key: Locator} - returns a text value from an element
            {key: [Locator]} - returns text from a list of elements in list format
            {key: {list_loc: Locator}, {key_loc: Locator}, {value_loc: Locator}} - 
                returns a dictionary of key / value pairs from a list of elements
        
        Returns
        -------
        dict 
            A dictionary of items containing information scraped from the page
        """

        page_dict = {}
        for key, value in page_definition.items():
            if type(value) is Locator:
                # Dictionary item is a single element text value
                page_dict.update({key: self.get_element_text(value)})
            elif type(value) is list:
                # Dictionary item is a list of values
                page_dict.update({key: self.get_element_list(*value)})
            else:
                # Dictionary item is a dictionary of values
                page_dict.update({key: self.get_elements_dict(**value)})
        return page_dict

    def scrape_pages(
        self,
        item_links: list,
        page_def: dict, 
        image_loc: Locator,
        num_pages: int,
        data_folder: str,
        image_folder: str) -> None:

        """
        Scrapes a list of URLS in range to num_pages
        using the page definition dictionary provided
        and saves each page as a JSON file
        """
        for idx, link in enumerate(item_links):

            if idx == num_pages - 1:
                break

            self.go_to_page_url(link)
            page_dict = self.get_page_data(page_def)
            item_id = link.rsplit('/', 1)[-1]
            page_dict.update({"item_id": link.rsplit('/', 1)[-1]})
            page_dict.update({"item_UUID": uuid.uuid4()})
            page_dict.update({"image_urls": self.get_image_url(image_loc)})
            file_ops.dict_to_json_file(page_dict, f"{data_folder}/{item_id}.json")
            for url in page_dict["image_urls"]:
                file_ops.get_image(url, f"{image_folder}/{item_id}.json")

    def get_image_url(self, loc: Locator) -> list:
        """
        Gets the URL associated with an image from the src attribute

        Parameters
        ----------
        loc: Locator
            A supported Locator strategy and value of the 
            Locator to find the image element

        Returns
        -------
        str
        """
        image_urls = []
        try:
            images = self._driver.find_elements(by=loc.locate_by,
                value=loc.locate_value)
            for image in images:
                image_urls.append(image.get_attribute('src').split('?', 1)[0])

        except NoSuchElementException:
            raise RuntimeError((f"Error getting image: "
                                "Element at {loc.locate_by} does not exist."))
        finally:
            return image_urls

    def quit(self) -> None:
        self._driver.quit()
