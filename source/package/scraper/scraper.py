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
from functools import wraps

# class Locator:
#     """
#     This class allows an element Locator to be defined 
#     as an object to pass to Scraper methods to find elements

#     """
#     def __init__(self, locate_by: str, locate_value: str):
#         """Create a new instance of the Locator class

#         Parameters
#         ----------
#         locate_by : str
#             A supported Locator strategy e.g. XPATH, TAG_NAME etc.
#         locate_value : str
#             Locator value for search result elements on the page 
#             e.g. the Xpath, the tag etc.
#         """
#         try:
#             self.locate_by = locate_by
#             self.locate_value = locate_value
#         except TypeError as e:
#             logging.ERROR("Error instantiating Locator object.")

class Scraper:

    """
    This class provides generic functions for web scraping

    """
    def exception_handler(func):
        @wraps(func)
        def inner_function(*args, **kwargs):
            try:
                args_repr = [repr(a) for a in args]
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                signature = ", ".join(args_repr + kwargs_repr)
                response = func(*args, **kwargs)
            except WebDriverException as e:
                raise RuntimeError(f"WebDriverException in {func.__name__}({signature}): {e.msg}") from e
            except TimeoutException as e:
                raise RuntimeError(f"TimeoutException in {func.__name__}({signature}): {e.msg}") from e
            except NoSuchElementException as e:
                raise RuntimeError(f"Element was not found in {func.__name__}({signature}): {e.msg}") from e
            return response
        return inner_function

    @exception_handler
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
        # initiate the session
        options = Options()
        options.add_argument("--headless")
        # These settings required otherwise initialisation of driver slow
        options.add_argument('--no-proxy-server')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # options.binary_location = '/usr/bin/google-chrome'
        # driverService = Service('/usr/bin/chromedriver')
        self.__driver = webdriver.Chrome(options=options)
        self.__driver.get(url)
        logging.info("Successfully initiated driver and loaded website")      

    def dismiss_popup(
            self,
            button_loc: By,
            iframe_loc: By = None) -> None:
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
                    EC.visibility_of_element_located(*iframe_loc))
                self.__driver.switch_to.frame(dismiss_frame)

                # This additional wait may be required to ensure 
                # the buttons are accessible

                dismiss_button = WebDriverWait(self.__driver, 10).until(
                    EC.element_to_be_clickable(*button_loc))
                dismiss_button.click()

            self.__driver.switch_to.default_content()

        except TimeoutException:
            # already clicked / not there
            return

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
                EC.element_to_be_clickable(*button_loc))
            button_loc.click()

    # @exception_handler
    def search(self, search_url: str, results_loc: By = None) -> bool:
        """
        Executes a search with a search URL which should
        be in the correct format for the web site being scraped

        Parameters
        ----------
        search_url: str
            The URL which executes a search on the website
        results_loc: Locator
            Locator strategy and value for the elements displaying results

        Returns
        -------
        bool
            True when search results are found, otherwise False

        """

        self.__driver.get(search_url)
        
        # if the no results div exists then search returned no results
        return len(self.__driver.find_elements(*results_loc)) != 0

    @exception_handler
    def get_item_links(self, 
            results_loc: By) -> list:

        """
        Returns a list of URLs for each item in a page of the search results

        Parameters
        ----------
        results_loc: Locator
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

        # Was getting a timeout error here, adding this wait for all the elements
        # to be present seems to solve this
        items = WebDriverWait(self.__driver, 10).until(
            EC.presence_of_all_elements_located(results_loc))
        for item in items:
            # go to each recipe and get the link and add to list
            item_url = item.get_attribute("href")
            url_list.append(item_url)
        return url_list

    @exception_handler
    def go_to_page_url(self, 
        url: str, 
        invalid_page: By) -> bool:
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
        self.__driver.get(url)
        if invalid_page != None:
            return len(self.__driver.find_elements(*invalid_page)) == 0
        else:
            return True

    @exception_handler
    def get_element(self, loc: tuple) -> WebElement:
        """
        Returns an element using the defined locator information

        Parameters
        ----------
        loc: tuple
            A supported Locator strategy and value

        Returns
        -------
        WebElement
            A web elements
        """
        return self.__driver.find_element(*loc)

    @exception_handler
    def get_elements(self, loc: tuple) -> list[WebElement]:
        """
        Returns a list of elements using the defined locator information

        Parameters
        ----------
        loc: tuple
            A supported Locator strategy and value

        Returns
        -------
        list[WebElement]
            A list of web elements
        """
        return self.__driver.find_elements(*loc)

    @exception_handler
    def get_element_text(self, loc: tuple) -> str:
        """
        Returns text attribute of element using the defined locator information

        Parameters
        ----------
        loc: tuple
            A supported Locator strategy and value

        Returns
        -------
        str
            The text attribute of the web element
        """
        
        return self.__driver.find_element(*loc).text

    @exception_handler
    def get_element_list(self, list_def: tuple) -> list[dict]:
        """
        Finds a list of elements using the defined Locator
        and returns the text of each in a list

        Parameters
        ----------
        list_def: tuple
            A supported Locator strategy and value

        Returns
        -------
        list[dict]:
            A list of dictionaries with a single key: value
            pair in each dictionary
        """
        key, loc = list_def
        list_values = []
        list_items = self.__driver.find_elements(*loc)
        if len(list_items) > 0:
            for item in list_items:
                list_dict = {key: item.text}
                list_values.append(list_dict)
            return list_values
        else:
            # raise RuntimeError(f"Elements at {loc.locate_value} does not exist.")
            return []
 
    @exception_handler
    def get_elements_dict(
            self, 
            list_loc: tuple,
            dict_keys: list,
            dict_values: list) -> list[dict]:
        """
        Finds a list of elements, and then finds multiple values
        as specified by locator details in 'values' which corresponds to 
        items specified in 'keys' and creates a dictionary item
        for each key / value pair
        
        Parameters
        ----------
        list_loc: tuple
            A supported locator strategy and value
        keys: list
            A list of key values for each dictionary item
        values: list
            A list of supported locator strategy and values of elements
            containing the values for each dictionary item
        Returns
        -------
        list[dict]
            A list of dictionaries with key / value pairs

        """
        dict_list = []

        list_items = self.__driver.find_elements(*list_loc)
        if len(list_items) > 0:     
            for item in list_items:     
                item_dict = {}
                for idx, key in enumerate(dict_keys):
                    key_text = key
                    key_value = item.find_element(*dict_values[idx]).text
                    item_dict.update({key_text: key_value})
                dict_list.append(item_dict)
            return dict_list
        else:
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
            {key: tuple} - returns a text value from an element
            {key: [tuple]} - returns list of dictionaries from a list of elements
            {key: {list_loc: tuple}, {key_loc: tuple}, {value_loc: tuple}} - 
                returns a dictionary of key / value pairs from a list of elements
            tuple values are supported locator strategy and value pairs
            e.g. (By.XPATH, "//div[(@class='post recipe')]//h1[(@class='heading-1')]")
        
        Returns
        -------
        dict 
            A dictionary of items containing information scraped from the page
        """

        page_dict = {}

        for key, value in page_definition.items():
            if type(value) is tuple:
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

    def get_image_url(self, loc: tuple) -> list:
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
        images = self.__driver.find_elements(*loc)
        for image in images:
            # image_urls.append(image.get_attribute('src').split('?', 1)[0])
            image_urls.append(image.get_attribute('src'))
        return image_urls

    def quit(self) -> None:
        """Closes the browser session"""
        self.__driver.quit()
        self.__driver = None
