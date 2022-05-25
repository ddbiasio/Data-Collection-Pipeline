from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import logging

class Locator:
    """
    This class allows an element Locator to be defined 
    as an object to pass to Scraper methods to find elements

    """
    def __init__(self, locate_by: By, locate_value: str):
        """Create a new instance of the Locator class

        Parameters
        ----------
        locate_by : str
            A supported Locator strategy e.g. XPATH, TAG_NAME etc.
        locate_value : str
            Locator value for search result elements on the page 
            e.g. the Xpath, the tag etc.
        """
        try:
            self.locate_by = locate_by
            self.locate_value = locate_value
        except TypeError as e:
            logging.ERROR("Error instantiating Locator object.")

class Scraper:

    """
    This class provides generic functions for web scraping

    Methods:
        dismiss_popup(button_loc: str, iframe_loc = None: str) -> None
        search(search_url: str, no_results: str = None) -> bool
        get_item_links(loc: Locator) -> list
        go_to_page_url(url: str) -> bool
        get_element_text(loc: Locator) -> str
        get_element_list(loc: Locator) -> list[str]
        get_element_dict(get_elements_dict(self, list_loc: Locator, key_loc: Locator, value_loc: Locator) -> dict
        get_page_data(page_definition: dict) -> dict
        get_image_url(parent: WebElement, loc: Locator) -> str
        quit()

    """
    def __init__(self, 
                url: str) -> None:

        """
        Parameters
        ----------
        url: str
            The URL of the website to be scraped
        Returns
        -------
        None
        """

        try:
            # initiate the session
            options = Options()
            options.add_argument("--headless")
            # These settings required otherwise initialisation of driver slow
            options.add_argument('--no-proxy-server')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.binary_location = '/usr/bin/google-chrome'
            driverService = Service('/usr/bin/chromedriver')
            self.__driver = webdriver.Chrome(service=driverService, options=options)
            self.__driver.get(url)
            logging.info("Successfully initiated driver and loaded website")

        except WebDriverException as e:
            # If something fails the close the driver and raise the exception
            # self.__driver.quit()
            raise RuntimeError(f"Failed to initialise Scraper: {e.msg}") from e

    def dismiss_popup(
            self,
            button_loc: Locator,
            iframe_loc: Locator = None) -> None:
        """
        Locates a button within a frame and executes the click to accept cookies

        Parameters
        ----------
        button_loc : Locator
            Locator for the button which will clear the popup
        iframe_loc : Locator = None
            Locator for the frame where the buttons are displayed
        """
        try:
            if iframe_loc is not None:
                dismiss_frame = WebDriverWait(self.__driver, 10).until(
                    EC.visibility_of_element_located(
                        (iframe_loc.locate_by, 
                        iframe_loc.locate_value)))
                self.__driver.switch_to.frame(dismiss_frame)

            # This additional wait may be required to ensure 
            # the buttons are accessible
            try:
                dismiss_button = WebDriverWait(self.__driver, 10).until(
                    EC.element_to_be_clickable(
                        (button_loc.locate_by, 
                        button_loc.locate_value)))
                dismiss_button.click()
            except TimeoutException:
                # already clicked
                pass

            self.__driver.switch_to.default_content()

        except TimeoutException:
            # already clicked / not there
            pass

        except NoSuchElementException:
            # If the element is not there then cookies must have been 
            # accepted before
            return

        except StaleElementReferenceException:
            # This is being thrown intermittently
            # There is no other navigation etc.
            # which would case this so maybe something in page load.  
            # Retry when this occurs
            button_loc = WebDriverWait(self.__driver, 10).until(
                EC.element_to_be_clickable(
                    (button_loc.locate_by, 
                    button_loc.locate_value)))
            button_loc.click()

    def search(self, search_url: str, no_results: Locator = None) -> bool:

        """
        Executes a search with a search URL which should
        be in the correct format for the web site being scraped

        Parameters
        ----------
        search_url: str
            The URL which executes a search on the website
        no_results: Locator
            Locator strategy and value for the element displaying no results message

        Returns
        -------
        bool
            True when search results are found, otherwise False

        """
        try:
            self.__driver.get(search_url)

            if no_results != None:
                try:               
                    # if the no results div exists then search returned no results
                    return len(self.__driver.find_elements(
                        by=no_results.locate_by, value=no_results.locate_value)) == 0

                except NoSuchElementException:
                    # if the no results div does not exist 
                    # then search returned results
                    return True
            else:
                return True
        except WebDriverException:
            raise RuntimeError("The search page could not be loaded")

    def get_item_links(self, 
            loc: Locator, 
            no_results_loc: Locator) -> list:

        """
        Returns a list of URLs for each item in a page of the search results

        Parameters
        ----------
        loc: Locator
            A supported Locator strategy and value of the Locator 
            to find the elements which have URL data for pages to be scraped

        Returns
        -------
        None

        """
        # This assumes that results are displayed in a standard group of elements
        # and that each search result item will have an href attribute 
        # containing the link to the item page

        # find all the search result items
        url_list = []
        # Only get links if page has results
        if len(self.__driver.find_elements(
                        by=no_results_loc.locate_by, 
                        value=no_results_loc.locate_value)) == 0:
            
            items = WebDriverWait(self.__driver, 10).until(
                EC.presence_of_all_elements_located(
                    (loc.locate_by, 
                    loc.locate_value)))
            # items = self.__driver.find_elements(
            #     by=loc.locate_by, value=loc.locate_value)

            for item in items:
                # go to each recipe and get the link and add to list
                item_url = item.get_attribute("href")
                url_list.append(item_url)
        return url_list

    def go_to_page_url(self, 
        url: str, 
        invalid_page: Locator) -> bool:
        """
        Navigates to the web page identified by 'url'

        Parameters
        ----------
        url: str
            The URL of the page to navigate to
        invalid_page: Locator
            A supported Locator strategy and value of the Locator 
            which defines an element which will be displayed if page does not 
            exist on the site
        Returns
        -------
        bool
            True when page navigation successful, False otherwise

        """
        try:
            self.__driver.get(url)
            if invalid_page != None:
                return len(self.__driver.find_elements(
                            by=invalid_page.locate_by, 
                            value=invalid_page.locate_value)) == 0
            else:
                return True
        except (TimeoutException, WebDriverException):
            raise RuntimeError(f"Unable to load page: {url}")

    def get_element(self, loc: Locator) -> WebElement:
        """
        Returns an element using the defined Locator

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
            The web element
        """
        try:
            return self.__driver.find_element(by=loc.locate_by,
                                            value=loc.locate_value)

        except NoSuchElementException:
            # raise RuntimeError(f"Element at {loc.locate_value} does not exist.")
            return None

    def get_elements(self, loc: Locator) -> list:
        """
        Returns an element using the defined Locator

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
            A list of web elements
        """
        try:
            return self.__driver.find_elements(by=loc.locate_by,
                                            value=loc.locate_value)

        except NoSuchElementException:
            # raise RuntimeError(f"Elements at {loc.locate_value} does not exist.")
            return None

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
        str
            The text property of the web element

        """
        try:
            return self.__driver.find_element(by=loc.locate_by,
                                            value=loc.locate_value).text

        except NoSuchElementException:
            # raise RuntimeError(f"Element at {loc.locate_value} does not exist.")
            return None

    def get_element_list(self, list_def: tuple) -> list[dict]:
        """
        Finds a list of elements using the defined Locator
        and returns the text of each in a list

        Parameters
        ----------
        list_def: tuple
            A tuple defining the key to store values against
            and a supported locator strategy to get the value for
            each list item to be stored in the dictionary

        Returns
        -------
        list[dict]:
            A list of dictionaries with a single key: value
            pair in each dictionary

        """
        key, loc = list_def
        list_values = []
        list_items = self.__driver.find_elements(
            by=loc.locate_by, value=loc.locate_value)
        if len(list_items) > 0:
            for item in list_items:
                list_dict = {key: item.text}
                list_values.append(list_dict)
            return list_values
        else:
            # raise RuntimeError(f"Elements at {loc.locate_value} does not exist.")
            return []
 
    def get_elements_dict(
            self, 
            list_loc: Locator,
            dict_keys: list,
            dict_values: list) -> list[dict]:
        """
        Finds a list of elements, and then finds multiple values
        as specified by locator details in 'values' which corresponds to 
        items specified in 'keys' and creates a dictionary item
        for each key / value pair
        
        Parameters
        ----------
        list_loc: Locator
            A supported Locator strategy and value of the 
            Locator to find the list elements
        keys: list
            A list of key values for each dictionary item
        values: list
            A list of supported Locator strategy sorresponding to
            the elements which contain the data for each key in keys
        Returns
        -------
        list[dict]
            A list of dictionaries with key / value pairs

        """
        dict_list = []

        list_items = self.__driver.find_elements(by=list_loc.locate_by, value=list_loc.locate_value)
        if len(list_items) > 0:     
            for item in list_items:     
                item_dict = {}
                try:
                    for idx, key in enumerate(dict_keys):
                        key_text = key
                        key_value = item.find_element(by=dict_values[idx].locate_by, value=dict_values[idx].locate_value).text
                        item_dict.update({key_text: key_value})
                except NoSuchElementException:         
                    raise RuntimeError(f"Element at {dict_values[idx].locate_value} does not exist.")
                dict_list.append(item_dict)
            return dict_list
        else:
            # raise RuntimeError(f"Elements at {list_loc.locate_value} does not exist.")
            return []

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
            {key: [Locator]} - returns list of dictionaries from a list of elements
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
                # The list should be of format key: list_loc
                page_dict.update({key: self.get_element_list(*value)})
            else:
                # Dictionary item is a dictionary of values
                page_dict.update({key: self.get_elements_dict(**value)})

        return page_dict

    def get_image_url(self, loc: Locator) -> list:
        """
        Gets the URL associated with an image / images from the src attribute

        Parameters
        ----------
        loc: Locator
            A supported Locator strategy and value of the 
            Locator to find the image element(s)

        Returns
        -------
        list
            A list of image URLS
        """
        image_urls = []
        try:
            images = self.__driver.find_elements(by=loc.locate_by,
                value=loc.locate_value)
            for image in images:
                # image_urls.append(image.get_attribute('src').split('?', 1)[0])
                image_urls.append(image.get_attribute('src'))

        except NoSuchElementException:
            raise RuntimeError((f"Error getting image: "
                                "Element at {loc.locate_value} does not exist."))
        finally:
            return image_urls

    def quit(self) -> None:
        """Closes the browser session"""
        self.__driver.quit()
        self.__driver = None
