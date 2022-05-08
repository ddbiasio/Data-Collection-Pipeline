from scraper import Locator
from scraper import Scraper
from selenium.webdriver.common.by import By 
from string import Template
from utilities import file_ops
import uuid
import recipe_constants as rc

class RecipeScraper:

    def __init__(self):

        self.recipe_dict = {
            "recipe_name": rc.RECIPE_NAME_LOC,
            "ingredients": [rc.INGREDIENTS_LOC],
            "method": {
                "list_loc": rc.METHOD_STEPS_LOC,
                "key_loc": rc.METHOD_STEP_KEY_LOC,
                "value_loc": rc.METHOD_STEP_DETAIL
                },
            "nutritional_info": {
                "list_loc": rc.NUTRITIONAL_LIST_LOC,
                "key_loc": rc.NUTRITIONAL_INFO_LOC,
                "value_loc": rc.NUTRITIONAL_VALUE_LOC       
                },
            "planning_info": {
                "list_loc": rc.PLANNING_LIST_LOC,
                "key_loc": rc.PLANNING_LIST_TASK,
                "value_loc": rc.PLANNING_LIST_TIME              
                }
        }

        # Set up variables to be passed to scraping methods
        self.xp_accept_button = rc.ACCEPT_BUTTON_LOC
        self.scraper = Scraper(rc.WEBSITE_URL)

        self.dismiss_sign_in_button = rc.DISMISS_SIGN_IN_LOC
        self.dismiss_sign_in_iframe = rc.SIGN_IN_IFRAME_LOC

        if self.scraper is not None:
            self.scraper.dismiss_popup(self.xp_accept_button)

        # Set search template based on 
        # https://www.bbcgoodfood.com/search?q=chicken
        # Multiple word searches should be separated by plus
        self.search_template = rc.SEARCH_URL_TEMPLATE

        # Set results template based on 
        # https://www.bbcgoodfood.com/search/recipes/page/2/?q=chicken&sort=-relevance
        # Multiple word searches should be separated by plus
        self.results_template = rc.RESULTS_URL_TEMPLATE
    

        # XPATH details for the no results element
        self.xp_no_results = rc.NO_RESULTS_DIV_LOC

        self.images = rc.IMAGES_LOC

        # XPATH details for the invalid page content
        self.invalid_page = rc.ERROR_PAGE_DIV_LOC

    def scrape_pages(
        self,
        item_links: list,
        page_def: dict, 
        image_loc: Locator,
        data_folder: str,
        image_folder: str) -> None:

        """
        Scrapes a list of URLS in range to num_pages
        using the page definition dictionary provided
        and saves each page as a JSON file
        """
        for link in item_links:

            self.scraper.go_to_page_url(link, self.invalid_page)
            self.scraper.dismiss_popup(
                self.dismiss_sign_in_button, 
                self.dismiss_sign_in_iframe)
            page_dict = self.scraper.get_page_data(page_def)
            item_id = link.rsplit('/', 1)[-1]
            page_dict.update({"item_id": link.rsplit('/', 1)[-1]})
            page_dict.update({"item_UUID": uuid.uuid4()})
            page_dict.update({"image_urls": self.scraper.get_image_url(image_loc)})
            file_ops.dict_to_json_file(page_dict, f"{data_folder}/{item_id}.json")
            for url in page_dict["image_urls"]:
                file_ops.get_image(url, f"{image_folder}/{item_id}.json")

    def get_recipe_data(
            self, 
            keyword_search: str, 
            num_pages: int):

        try:
            # Search for recipes    
            search_mappings = {'searchwords': keyword_search}
            search_url = Template(self.search_template).substitute(**search_mappings)
            if self.scraper.search(search_url, self.xp_no_results):

                # Get the links from the recipe cards in search results
                search_results_locator = Locator(By.XPATH,
                    "//a[(@class='body-copy-small standard-card-new__description')]")

                for page in range(1, num_pages + 1):
                    # Sets the URL for results pages by page num
                    results_mappings = {'pagenum': page, 'searchwords': keyword_search}
                    results_page = Template(self.results_template).substitute(**results_mappings)

                    if self.scraper.go_to_page_url(results_page, self.invalid_page):
                        urls = self.scraper.get_item_links(search_results_locator)
                
                if urls.count > 1:
                    # Create the folders for the data and images
                    # Data folder ./raw_data/search_term (replace spaces with underscore)
                    data_folder = f"./raw_data/{keyword_search.replace(' ', '_')}"
                    # Images folder ./raw_data/search_term/images
                    images_folder = f"{data_folder}/images"
                    file_ops.create_folder(data_folder)
                    file_ops.create_folder(images_folder)
                    # Iterate through the page URLS n times and scrape the data
                    # Writing the files to the defined data folder
                    self.scrape_pages(
                        urls, 
                        self.recipe_dict, 
                        self.images, 
                        data_folder,
                        images_folder)
            else:
                print(f"No results for {keyword_search}")
        finally:
            self.scraper.quit()