from scraper import Locator
from scraper import Scraper
from selenium.webdriver.common.by import By 
from string import Template
from utilities import file_ops
import uuid

class RecipeScraper:

    def __init__(self):

        self.recipe_dict = {
            "recipe_name": Locator(By.XPATH,"""//div[(@class='post recipe')]//h1[(@class='heading-1')]"""),
            "ingredients": [Locator(By.XPATH, """//div[(@class='post_recipe')]//section[(@class='recipe__ingredients col-12 mt-md col-lg-6')]//li[(@class='pb-xxs pt-xxs list-item list-item--separator')]""")],
            "method": {
                "list_loc": Locator(By.XPATH, """//div[(@class='post recipe')]//section[(@class='recipe__method-steps mb-lg col-12 col-lg-6')]//li[(@class='pb-xs pt-xs list-item')]"""),
                "key_loc": Locator(By.XPATH, "./span[(@class='mb-xxs heading-6')]"),
                "value_loc": Locator(By.TAG_NAME, "p")
            },
            "nutritional_info": {
                "list_loc": Locator(By.XPATH, """//div[(@class='post recipe')]//tr[(@class='key-value-blocks__item')]"""),
                "key_loc": Locator(By.XPATH, "./td[(@class='key-value-blocks__key')]"),
                "value_loc": Locator(By.XPATH, "./td[(@class='key-value-blocks__value')]")        
            },
            "planning_info": {
                "list_loc": Locator(By.XPATH, """//div[(@class='post recipe')]//div[(@class='icon-with-text time-range-list cook-and-prep-time post-header__cook-and-prep-time')]//li[(@class='body-copy-small list-item')]"""),
                "key_loc": Locator(By.XPATH, ".//span[(@class='body-copy-bold mr-xxs')]"),
                "value_loc": Locator(By.XPATH, ".//time")               
            }
        }

        # Set up variables to be passed to scraping methods
        self.xp_accept_button = Locator(By.XPATH, "//button[(@class=' css-1x23ujx')]")
        self.scraper = Scraper("https://www.bbcgoodfood.com/")

        if self.scraper is not None:
            self.scraper.accept_cookies(self.xp_accept_button)

        # Set search template based on 
        # https://www.bbcgoodfood.com/search?q=chicken
        # Multiple word searches should be separated by plus
        self.search_template = (
            "https://www.bbcgoodfood.com/search?q=$searchwords")

        # Set results template based on 
        # https://www.bbcgoodfood.com/search/recipes/page/2/?q=chicken&sort=-relevance
        # Multiple word searches should be separated by plus
        self.results_template = (
            "https://www.bbcgoodfood.com/search/recipes/page/$pagenum/?q=$searchwords&sort=-relevance")

        # XPATH details for the no results element
        self.xp_no_results = Locator(By.XPATH,
            "//div[(@class='col-12 template-search-universal__no-results')]")

        self.images = Locator(By.XPATH, "//div[(@class='post recipe')]//div[(@class='post-header__image-container')]//img[(@class='image__img')]")

        # XPATH details for the invalid page content
        self.invalid_page = Locator(By.XPATH, "//div[(@class='template-error__content')]")

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

            self.scraper.go_to_page_url(link, self.invalid_page)
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
                # Create the folders for the data and images
                # Data folder ./raw_data/search_term (replace spaces with underscore)
                data_folder = f"./raw_data/{keyword_search.replace(' ', '_')}"
                # Images folder ./raw_data/search_term/images
                images_folder = f"{data_folder}/images"
                file_ops.create_folder(data_folder)
                file_ops.create_folder(images_folder)

                # Get the links from the recipe cards in search results
                search_results_locator = Locator(By.XPATH,
                    "//a[(@class='body-copy-small standard-card-new__description')]")

                # Get links from first 'num_pages' of results
                for page in range(1, num_pages):
                    # Sets the URL for results pages by page num
                    results_mappings = {'pagenum': page, 'searchwords': keyword_search}
                    results_page = Template(self.results_template).substitute(**results_mappings)

                    if self.scraper.go_to_page_url(results_page, self.invalid_page):
                        urls = self.scraper.get_item_links(search_results_locator)
                
                # Iterate through the page URLS n times and scrape the data
                # Writing the files to the defined data folder
                self.scrape_pages(
                    urls, 
                    self.recipe_dict, 
                    self.images, 
                    2, 
                    data_folder,
                    images_folder)
        finally:
            self.scraper.quit()