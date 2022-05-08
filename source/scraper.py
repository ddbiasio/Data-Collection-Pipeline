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

    Methods
    -------
        dismiss_popup(self, button_loc: str, 
                iframe_loc = None: str) -> None
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

        try:
            # initiate the session
            options = Options()
            options.add_argument("--headless")
            options.binary_location = '/usr/bin/google-chrome'
            driverService = Service('/usr/bin/chromedriver')
            self._driver = webdriver.Chrome(service=driverService, options=options)
            self._driver.get(url)

        except WebDriverException as e:
            # If something fails the close the driver and raise the exception
            # self._driver.quit()
            raise RuntimeError(f"Failed to initialise Scraper: {e.msg}") from e

    def dismiss_popup(
            self,
            button_loc: Locator,
            iframe_loc: Locator = None) -> None:
        """
        Locates a button within a frame and executes the click to accept cookies

        Parameters
        ----------
        button_loc: str
            Locator for the button which will clear the popup
        iframe_loc = None: str
            Locator for the frame where the buttons are displayed

        Returns
        -------
        None

        """
        try:
            if iframe_loc is not None:
                dismiss_frame = WebDriverWait(self._driver, 10).until(
                    EC.visibility_of_element_located(
                        (iframe_loc.locate_by, 
                        iframe_loc.locate_value)))
                self._driver.switch_to.frame(dismiss_frame)

            # This additional wait may be required to ensure 
            # the buttons are accessible
            try:
                button_loc = WebDriverWait(self._driver, 10).until(
                    EC.element_to_be_clickable(
                        (button_loc.locate_by, 
                        button_loc.locate_value)))
                button_loc.click()
            except TimeoutException:
                # already clicked
                pass

            self._driver.switch_to.default_content()

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
            button_loc = WebDriverWait(self._driver, 10).until(
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

        """
        try:
            self._driver.get(search_url)

            if no_results != None:
                try:               
                    # if the no results div exists then search returned no results
                    self._driver.find_element(
                        by=no_results.locate_by, value=no_results.locate_value)
                    return False

                except NoSuchElementException:
                    # if the no results div does not exist 
                    # then search returned results
                    return True
            else:
                return True
        except WebDriverException:
            raise RuntimeError("The search page could not be loaded")


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

    def go_to_page_url(self, url: str, invalid_page: Locator) -> bool:
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
            if invalid_page != None:
                try:
                    invalid_page_element = self._driver.find_element(
                                by=invalid_page.locate_by, value=invalid_page.locate_value)
                    return False
                except NoSuchElementException:
                    return True
            else:
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
            raise RuntimeError(f"Element at {loc.locate_value} does not exist.")

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
        list_items = self._driver.find_elements(
            by=loc.locate_by, value=loc.locate_value)
        if len(list_items) > 0:
            for item in list_items:
                list_values.append(item.text)
            return list_values
        else:
            raise RuntimeError(f"Elements at {loc.locate_value} does not exist.")
 
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

        list_items = self._driver.find_elements(by=list_loc.locate_by, value=list_loc.locate_value)
        if len(list_items) > 0:
            for item in list_items:
                try:
                    key_text = item.find_element(by=key_loc.locate_by, value=key_loc.locate_value).text
                except NoSuchElementException:         
                    raise RuntimeError(f"Element at {key_loc.locate_value} does not exist.")
                try:
                    value_text = item.find_element(by=value_loc.locate_by, value=value_loc.locate_value).text
                except NoSuchElementException:            
                    raise RuntimeError(f"Element at {value_loc.locate_value} does not exist.")
                dict_values.update({key_text: value_text})
            return dict_values
        else:
            raise RuntimeError(f"Elements at {list_loc.locate_value} does not exist.")
        

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
                                "Element at {loc.locate_value} does not exist."))
        finally:
            return image_urls

    def quit(self) -> None:
        self._driver.quit()
        self._driver = None
