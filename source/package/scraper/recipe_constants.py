
from .scraper import Locator
from selenium.webdriver.common.by import By

# Navigational constants
WEBSITE_URL = "https://www.bbcgoodfood.com/"
SEARCH_URL_TEMPLATE = "https://www.bbcgoodfood.com/search?q=$searchwords"
RESULTS_URL_TEMPLATE = "https://www.bbcgoodfood.com/search/recipes/page/$pagenum/?q=$searchwords&sort=-relevance"

# Locator constants
ACCEPT_BUTTON_LOC = Locator(By.XPATH, "//button[(@class=' css-1x23ujx')]")
DISMISS_SIGN_IN_LOC = Locator(By.XPATH,"//button[(@class='pn-widget__link pn-widget__link--secondary unbutton')]")
SIGN_IN_IFRAME_LOC = Locator(By.TAG_NAME, "iframe")

RESULT_CARDS_LOC = Locator(By.XPATH, "//a[(@class='body-copy-small standard-card-new__description')]")
NO_RESULTS_DIV_LOC = Locator(By.XPATH,
            "//div[(@class='col-12 template-search-universal__no-results')]")

RECIPE_NAME_LOC = Locator(By.XPATH,"""//div[(@class='post recipe')]//h1[(@class='heading-1')]""")

INGREDIENTS_LOC = Locator(By.XPATH, """//div[(@class='post recipe')]//section[(@class='recipe__ingredients col-12 mt-md col-lg-6')]//li[(@class='pb-xxs pt-xxs list-item list-item--separator')]""")

METHOD_STEPS_LOC = Locator(By.XPATH, """//div[(@class='post recipe')]//section[(@class='recipe__method-steps mb-lg col-12 col-lg-6')]//li[(@class='pb-xs pt-xs list-item')]""")
METHOD_STEP_KEY_LOC = Locator(By.XPATH, "./span[(@class='mb-xxs heading-6')]")
METHOD_STEP_DETAIL = Locator(By.TAG_NAME, "p")

NUTRITIONAL_LIST_LOC = Locator(By.XPATH, """//div[(@class='post recipe')]//tr[(@class='key-value-blocks__item')]""")
NUTRITIONAL_INFO_LOC = Locator(By.XPATH, "./td[(@class='key-value-blocks__key')]")
NUTRITIONAL_VALUE_LOC = Locator(By.XPATH, "./td[(@class='key-value-blocks__value')]") 

PLANNING_LIST_LOC = Locator(By.XPATH, """//div[(@class='post recipe')]//div[(@class='icon-with-text time-range-list cook-and-prep-time post-header__cook-and-prep-time')]//li[(@class='body-copy-small list-item')]""")
PLANNING_LIST_TASK = Locator(By.XPATH, ".//span[(@class='body-copy-bold mr-xxs')]")
PLANNING_LIST_TIME = Locator(By.XPATH, ".//time") 

IMAGES_LOC = Locator(By.XPATH, "//div[(@class='post recipe')]//div[(@class='post-header__image-container')]//img[(@class='image__img')]")
ERROR_PAGE_DIV_LOC = Locator(By.XPATH, "//div[(@class='template-error__content')]")