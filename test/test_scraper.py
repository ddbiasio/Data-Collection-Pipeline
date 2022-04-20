import pytest
from source.scraper import Locator
from source.scraper import Scraper
from selenium.webdriver.common.by import By

@pytest.fixture(scope="module")
def test_scraper() -> Scraper:
    ts = Scraper("https://www.propertypal.com/")
    yield ts
    ts.quit()

def test_constructor():
    ts = Scraper("https://www.propertypal.com/")
    assert ts._driver.session_id
    ts.quit()

def test_quit():
    ts = Scraper("https://www.propertypal.com/")
    ts.quit()
    assert ts._driver is None

def test_accept_cookies(test_scraper: Scraper):
    accept_button = Locator(By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div/button[2]")
    test_scraper.accept_cookies(accept_button)
    test_scraper.accept_cookies(accept_button)

def test_search(test_scraper: Scraper):
    no_results = Locator(By.XPATH, "//div[(@class='pgheader pgheader-noresults')]")
    assert test_scraper.search("https://www.propertypal.com/property-for-sale/castlereagh-belfast", no_results)

def test_no_results(test_scraper: Scraper):
    no_results = Locator(By.XPATH, "//div[(@class='pgheader pgheader-noresults')]")
    assert not test_scraper.search(
        "https://www.propertypal.com/property-for-sale/searching-for-something-silly", 
        no_results)

def test_go_to_page_url(test_scraper: Scraper):
    error_page = Locator(By.XPATH, "//div[(@class='article error-page error-page-404')]")
    assert test_scraper.go_to_page_url("https://www.propertypal.com/property-for-sale/castlereagh-belfast/page-2", error_page)

def test_go_to_page_url_invalid(test_scraper: Scraper):
    error_page = Locator(By.XPATH, "//div[(@class='article error-page error-page-404')]")
    assert not test_scraper.go_to_page_url("https://www.propertypal.com/this_is_not_a_page", error_page)

def test_get_item_links(test_scraper: Scraper):
    error_page = Locator(By.XPATH, "//div[(@class='article error-page error-page-404')]")
    test_scraper.go_to_page_url("https://www.propertypal.com/property-for-sale/castlereagh-belfast/page-2", error_page)
    results_cards = Locator(By.XPATH,"""//div[(@class='box propbox
		 
		
		
		
		 propbox--forsale 
		
		
		
		
		
		
	')]""")
    results = test_scraper.get_item_links(results_cards)
    assert len(results) > 0

def test_get_element(test_scraper: Scraper):
    error_page = Locator(By.XPATH, "//div[(@class='article error-page error-page-404')]")
    price = Locator(By.XPATH, "//span[(@class='price-value ')]")
    test_scraper.go_to_page_url("https://www.propertypal.com/33-bloomfield-road-belfast/749013", error_page)
    price_text = test_scraper.get_element_text(price)
    assert price_text

def test_get_element_list(test_scraper: Scraper):
    features = Locator(By.XPATH, "//div[(@class='prop-descr-text')]//li")
    feature_list = test_scraper.get_element_list(features)
    assert len(feature_list) > 0

def test_get_element_dict(test_scraper: Scraper):
    list_loc = Locator(By.ID, "key-info-table")
    key_loc = Locator(By.XPATH, ".//th")
    value_loc = Locator(By.XPATH, ".//td")
    details = test_scraper.get_elements_dict(list_loc, key_loc, value_loc)
    assert len(details) > 0

def test_get_page_data(test_scraper: Scraper):
    page_def = {
        "price": Locator(By.XPATH, "//span[(@class='price-value ')]"), 
        "features": [Locator(By.XPATH, "//div[(@class='prop-descr-text')]//li")],
        "details": {
            "list_loc": Locator(By.ID, "key-info-table"),
            "key_loc": Locator(By.XPATH, ".//th"),
            "value_loc": Locator(By.XPATH, ".//td")
        }
    }
    page_dict = test_scraper.get_page_data(page_def)
    assert len(page_dict) > 0