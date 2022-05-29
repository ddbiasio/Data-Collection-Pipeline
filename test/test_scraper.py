from typing import Type
from numpy import equal
import pytest
from source.package.scraper.scraper import Locator
from source.package.scraper.scraper import Scraper
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement

# TODO Add Docstring

@pytest.fixture(scope="module")
def test_scraper() -> Scraper:
    ts = Scraper("https://www.propertypal.com/")
    yield ts
    ts.quit()

def test_constructor():
    ts = Scraper("https://www.propertypal.com/")
    assert ts._Scraper__driver.session_id
    ts.quit()

def test_quit():
    ts = Scraper("https://www.propertypal.com/")
    ts.quit()
    assert ts._Scraper__driver is None

def test_accept_cookies(test_scraper: Scraper):
    accept_button = Locator(By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div/button[2]")
    test_scraper.dismiss_popup(accept_button)
    test_scraper.dismiss_popup(accept_button)

def test_search(test_scraper: Scraper):
    # no_results = Locator(By.XPATH, "//div[(@class='pgheader pgheader-noresults')]")
    # This is how the class was in the HTML - not sure what all the
    # blanl lines are about but it doesn't work without them
    results_cards = Locator(By.XPATH,"""//div[(@class='box propbox
		 
		
		
		
		 propbox--forsale 
		
		
		
		
		
		
	')]""")
    assert test_scraper.search("https://www.propertypal.com/property-for-sale/castlereagh-belfast", results_cards)

def test_no_results(test_scraper: Scraper):
    # no_results = Locator(By.XPATH, "//div[(@class='pgheader pgheader-noresults')]")
    # This is how the class was in the HTML - not sure what all the
    # blanl lines are about but it doesn't work without them
    results_cards = Locator(By.XPATH,"""//div[(@class='box propbox
		 
		
		
		
		 propbox--forsale 
		
		
		
		
		
		
	')]""")
    assert not test_scraper.search(
        "https://www.propertypal.com/property-for-sale/searching-for-something-silly", 
        results_cards)

def test_go_to_page_url(test_scraper: Scraper):
    error_page = Locator(By.XPATH, "//div[(@class='article error-page error-page-404')]")
    assert test_scraper.go_to_page_url("https://www.propertypal.com/property-for-sale/castlereagh-belfast/page-2", error_page)

def test_go_to_page_url_invalid(test_scraper: Scraper):
    error_page = Locator(By.XPATH, "//div[(@class='article error-page error-page-404')]")
    assert not test_scraper.go_to_page_url("https://www.propertypal.com/this_is_not_a_page", error_page)

def test_get_item_links(test_scraper: Scraper):
    error_page = Locator(By.XPATH, "//div[(@class='article error-page error-page-404')]")
    test_scraper.go_to_page_url("https://www.propertypal.com/property-for-sale/castlereagh-belfast/page-2", error_page)
    # This is how the class was in the HTML - not sure what all the
    # blanl lines are about but it doesn't work without them
    results_cards = Locator(By.XPATH,"""//div[(@class='box propbox
		 
		
		
		
		 propbox--forsale 
		
		
		
		
		
		
	')]""")
    results = test_scraper.get_item_links(results_cards)
    assert len(results) > 0

def test_get_element(test_scraper: Scraper):
    error_page = Locator(By.XPATH, "//div[(@class='article error-page error-page-404')]")
    price = Locator(By.XPATH, "//span[(@class='price-value ')]")
    test_scraper.go_to_page_url("https://www.propertypal.com/7a-albert-drive-belfast/753419", error_page)
    price_text = test_scraper.get_element(price)
    assert type(price_text) is WebElement

def test_get_element_text(test_scraper: Scraper):
    error_page = Locator(By.XPATH, "//div[(@class='article error-page error-page-404')]")
    price = Locator(By.XPATH, "//span[(@class='price-value ')]")
    test_scraper.go_to_page_url("https://www.propertypal.com/7a-albert-drive-belfast/753419", error_page)
    price_text = test_scraper.get_element_text(price)
    assert price_text

def test_get_element_list(test_scraper: Scraper):
    features = ("feature", Locator(By.XPATH, "//div[(@class='prop-descr-text')]//li"))
    feature_list = test_scraper.get_element_list(features)
    assert len(feature_list) > 0

def test_get_element_dict(test_scraper: Scraper):
    list_loc = Locator(By.ID, "key-info-table")
    key_loc = Locator(By.XPATH, ".//th")
    value_loc = Locator(By.XPATH, ".//td")
    details = test_scraper.get_elements_dict(list_loc, ["info", "info_text"], [key_loc, value_loc])
    assert len(details) > 0

def test_get_page_data(test_scraper: Scraper):
    page_def = {
        "price": Locator(By.XPATH, "//span[(@class='price-value ')]"), 
        "features": [("feature", Locator(By.XPATH, "//div[(@class='prop-descr-text')]//li"))],
        "details": {
            "list_loc": Locator(By.ID, "key-info-table"),
            "dict_keys":  ["info", "info_text"],
            "dict_values": [Locator(By.XPATH, ".//th"), Locator(By.XPATH, ".//td")]
        }
    }
    page_dict = test_scraper.get_page_data(page_def)
    assert len(page_dict) > 0

def test_invalid_element(test_scraper: Scraper):
    with pytest.raises(RuntimeError):
        value = test_scraper.get_element(
            Locator(By.XPATH, "invalid_xpath"))

def test_invalid_elements(test_scraper: Scraper):
    value = test_scraper.get_element_list(("feature", Locator(By.XPATH, "invalid_xpath")))
    assert value == []

def test_invalid_list(test_scraper: Scraper):
    value = test_scraper.get_elements(Locator(By.XPATH, "invalid_xpath"))
    assert value == []

def test_invalid_dict_list(test_scraper: Scraper):
    value = test_scraper.get_elements_dict(Locator(By.ID, "invalid_xpath"),
        ["info", "info_text"],
        [Locator(By.XPATH, ".//th"), Locator(By.XPATH, ".//td")]
    )
    assert value == []
def test_invalid_dict_key(test_scraper: Scraper):
    with pytest.raises(RuntimeError):
        value = test_scraper.get_elements_dict(Locator(By.ID, "key-info-table"),
            ["info", "info_text"],
            [Locator(By.XPATH, "invalid_xpath"), Locator(By.XPATH, ".//td")]
        )

def test_invalid_dict_val(test_scraper: Scraper):
    with pytest.raises(RuntimeError):
        value = test_scraper.get_elements_dict(Locator(By.ID, "key-info-table"),
            ["info", "info_text"],
            [Locator(By.XPATH, ".//th"), Locator(By.XPATH, "invalid_xpath")]
        )

def test_invalid_url(test_scraper: Scraper):
    with pytest.raises(RuntimeError):
        assert not test_scraper.go_to_page_url("https://www.this_is_not_a_valid_url.com", None)
