
from .scraper import Locator
from selenium.webdriver.common.by import By

"""
This file defines constant values to be used in the recipe scraper class
"""
# Navigational constants
# Web site
WEBSITE_URL = "https://www.bbcgoodfood.com/"
# Template string to be used to generate URL for running a search
SEARCH_URL_TEMPLATE = "https://www.bbcgoodfood.com/search?q=$searchwords"
# Template string to be used to generate URL for each page of search results
RESULTS_URL_TEMPLATE = "https://www.bbcgoodfood.com/search/recipes/page/$pagenum/?q=$searchwords&sort=-relevance"
# Div container which is displayed when page is not found on the site
ERROR_PAGE_DIV_LOC = Locator(By.XPATH, "//div[(@class='template-error__content')]")

# Locator constants
# Accept / dismiss buttons and frames
ACCEPT_BUTTON_LOC = Locator(By.XPATH, "//button[(@class=' css-1x23ujx')]")
DISMISS_SIGN_IN_LOC = Locator(By.XPATH,"//button[(@class='pn-widget__link pn-widget__link--secondary unbutton')]")
SIGN_IN_IFRAME_LOC = Locator(By.TAG_NAME, "iframe")

# Elements in search results which display recipe cards 
RESULT_CARDS_LOC = Locator(By.XPATH, "//a[(@class='body-copy-small standard-card-new__description')]")
# The container that is displayed when the search returns no results 
NO_RESULTS_DIV_LOC = Locator(By.XPATH,
            "//div[(@class='col-12 template-search-universal__no-results')]")

# Heading which contains the recipe name
RECIPE_NAME_LOC = Locator(By.XPATH,"""//div[(@class='post recipe')]//h1[(@class='heading-1')]""")

# List elements which contain the ingredients information
INGREDIENTS_LOC = Locator(By.XPATH, """//div[(@class='post recipe')]//section[(@class='recipe__ingredients col-12 mt-md col-lg-6')]//li[(@class='pb-xxs pt-xxs list-item list-item--separator')]""")

# List elements which contain the instructions for the recipe
METHOD_STEPS_LOC = Locator(By.XPATH, """//div[(@class='post recipe')]//section[(@class='recipe__method-steps mb-lg col-12 col-lg-6')]//li[(@class='pb-xs pt-xs list-item')]""")
# Span container containing the method step number
METHOD_STEP_KEY_LOC = Locator(By.XPATH, "./span[(@class='mb-xxs heading-6')]")
# Paragraph with the instructions for the method step
METHOD_STEP_DETAIL = Locator(By.TAG_NAME, "p")

# Table row elements containing nutritional info
NUTRITIONAL_LIST_LOC = Locator(By.XPATH, """//div[(@class='post recipe')]//tr[(@class='key-value-blocks__item')]""")
# Data cell element in each table row which contains the nutritional item name
NUTRITIONAL_INFO_LOC = Locator(By.XPATH, "./td[(@class='key-value-blocks__key')]")
# Data cell elements in each table row which contains the nutritional item value
NUTRITIONAL_VALUE_LOC = Locator(By.XPATH, "./td[(@class='key-value-blocks__value')]") 

# Div container holding the planning information
PLANNING_LIST_LOC = Locator(By.XPATH, """//div[(@class='post recipe')]//div[(@class='icon-with-text time-range-list cook-and-prep-time post-header__cook-and-prep-time')]//li[(@class='body-copy-small list-item')]""")
# Span container containing the prep stage name
PLANNING_LIST_TASK = Locator(By.XPATH, ".//span[(@class='body-copy-bold mr-xxs')]")
# Time element containing the prep stage time
PLANNING_LIST_TIME = Locator(By.XPATH, ".//time") 

# Image element containing the recipe image
IMAGES_LOC = Locator(By.XPATH, "//div[(@class='post recipe')]//div[(@class='post-header__image-container')]//img[(@class='image__img')]")
