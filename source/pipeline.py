import logging
from package.storage.file_storage import Storage
from package.storage.db_storage import DBStorage
from recipe_scraper import RecipeScraper
from tqdm.auto import tqdm
import uuid
from package.utils.logger import log
import logging

# Create a logger for pipeline log messages
logger = logging.getLogger("pipeline")

@log(my_logger=logger)
def save_file(storage: Storage,
        page_dict: dict,
        folder: str):
    """Saves a file to a folder

    Parameters
    ----------
    storage: Storage
        A FileStorage or S3Storage instance
    page_dict : dict
        A dictionary containing recipe data
    folder : str
        Folder name to construct file name
    """    
    storage.save_json_file(
        page_dict,
        folder,
        f"{page_dict['item_id']}"
        )
    logger.info(f"Saved file: {page_dict['item_id']}")

@log(my_logger=logger)
def save_images(storage: Storage,
        page_dict: dict,
        folder: str):
    """Saves the images to a folder

    Parameters
    ----------
    storage : Storage
        A FileStorage or S3Storage instance
    page_dict : dict
        A dictionary containing recipe data
    folder : str
        Folder name to construct key for the object storage
    """
    for url in page_dict["image_urls"]:
        # Get the file extension from the url
        file_ext = url.rsplit('?', 1)[-2].rsplit('.', 1)[-1]
        storage.save_image(
            url,
            folder,
            f"{page_dict['item_id']}.{file_ext}")
        logger.info(f"Saved image: {page_dict['item_id']}.{file_ext}")

@log(my_logger=logger)
def store_data_files(storage: Storage,
        page_data_list: list,
        search: str):
    """Stores the data dictionaries in a single file

    Parameters
    ----------
    storage : Storage
        A concrete instance of a Storage class
    page_data_list : list
        List of dictionaries defining scraped page data
    search : str
        The search string used (for the file name)
    """
    if len(page_data_list) > 0:

        storage.save_json_file(
            page_data_list,
            storage.data_folder,
            f"{search}-{uuid.uuid4()}"
            )

        for page_dict in page_data_list:
            # save the files in the appropriate folder
            # save_file(storage, page_dict, storage.data_folder)
            save_images(storage, page_dict, storage.images_folder)
        logger.info(f"Saved all data and image files.")

@log(my_logger=logger)
def store_data_db(db_storage: DBStorage,
        json_data: list):
    """Uploads the data to the database

    Parameters
    ----------
    db_storage : DBStorage
        A DBStorage instance
    json_data : list
        A list of json strings
    """
    db_storage.json_to_db(
        json_data,
        'recipe',
        ['item_id', 'recipe_name', 'item_UUID','image_urls'],
        [
            ('ingredients', ['item_id', 'ingredient']),
            ('method', ['item_id', 'method_step']),
            ('planning_info', ['item_id', 'prep_stage']),
            ('nutritional_info', ['item_id', 'nutritional_info'])
        ],
        ['item_id']
    )
    logger.info(f"Saved data to database for {len(json_data)} items.")

@log(my_logger=logger)
def run_pipeline(
        search_term: str, 
        num_pages: int, 
        file_store: Storage, 
        db_storage: DBStorage):
    """The main routine to run all the necessary 
    tasks to scrape and save recipe data

    Parameters
    ----------
    search_term : str
        The search words to be used to sear for recipes
    num_pages : int
        Number fo results pages to scrape
    file_store : Storage
       An instance of a concrete Storage object
    db_storage : DBStorage
        An instance of DBStorage initialised with a valid DB connection

    Raises
    ------
    RuntimeError
        RuntimeError excepion will be propagated up and raised to calling functions
    """
    try:

        rs = RecipeScraper()
        logger.info(f"Initialised the scraper class.")
        results_pages = rs.search_recipes(search_term, num_pages)
        if results_pages > 0:
            
            logger.info(f"Executed search: {results_pages} pages if results")

            for page_num in tqdm(range(1, results_pages + 1), desc = 'Scraping progress', leave=False):
                # Get urls per page of search results
                urls = rs.get_urls(search_term, page_num)
                logger.info(f"Retrieved urls for page {page_num} of search results.")
                # Check list of urls is populated    
                if len(urls) > 0:
                    rs.page_data = []
                    # Scrape pages for results page `page_num`
                    for url in tqdm(urls, desc = 'Scraping pages'):
                        # get the ID from the URL
                        item_id = url.rsplit('/', 1)[-1]
                        if not db_storage.item_exists("recipe", "item_id", item_id):
                            page_dict = rs.get_page_data(url)
                            if len(page_dict) != 0:
                                rs.page_data.append(page_dict)
                        logger.info(f"Scraped data from {url}.")
                    if len(rs.page_data) > 0:
                        store_data_files(file_store, rs.page_data, search_term)
                        # json_data = get_json_data(file_store, f"{file_store.root_folder}/{search_term}")
                        store_data_db(db_storage, rs.page_data)
                        logger.info(f"Saved files, images and uploaded data for {len(rs.page_data)} items.")
        rs.quit()
    except RuntimeError as e:
       logger.exception(f"Exception raised in {__name__}. exception: {str(e)}")
       raise e
