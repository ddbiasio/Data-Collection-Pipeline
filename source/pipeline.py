from package.storage.file_storage import Storage
from package.storage.db_storage import DBStorage
from recipe_scraper import RecipeScraper
import json
import configparser
import recipe_constants as rc
from tqdm.auto import tqdm
from time import sleep

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

def store_data_files(storage: Storage,
        page_data_list: list,
        search: str):
    """Saves each recipe and images to a folder

    Parameters
    ----------
    storage : Storage
        A FileStorage or S3Storage instance
    page_data_list : list
        List of recipe dictionaries
    search : str
        Search keywords used (will be used to construct file names)
    """
    if len(page_data_list) > 0:

        for idx, page_dict in enumerate(page_data_list):
            # save the files in the appropriate folder
            save_file(storage, page_dict, storage.data_folder)
            save_images(storage, page_dict, storage.images_folder)

def get_json_data(storage: Storage,
        data_folder: str) -> list:
    """Returns a list of json strings from files in a folder

    Parameters
    ----------
    storage : Storage
        A FileStorage or S3Storage instance
    data_folder : str
        The folder to get the files from

    Returns
    -------
    list
       List of recipes as json strings
    """
    file_list = storage.list_files(data_folder)
    json_list = []
    for file in file_list:
        with open(file, "r") as json_file:
            if not ".json" in json_file.name:
                pass
            else:
                item_json = storage.read_json_file(file)
                json_list.append(item_json)
    return json_list

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
    db_storage.store_parent_df(
    json_data, 
    'recipe', 
    ['item_id'], 
    ['item_id', 'recipe_name', 'item_UUID','image_urls'],
    'append')

    db_storage.store_child_df(
        json_data,
        'ingredients',
        ['item_id', 'ingredient'],
        ['item_id'],
        'append'
    )

    db_storage.store_child_df(
        json_data,
        'method',
        ['item_id', 'method_step'],
        ['item_id'],
        'append'
    )
    db_storage.store_child_df(
        json_data,
        'planning_info',
        ['item_id', 'prep_stage'],
        ['item_id'],
        'append'
    )

    db_storage.store_child_df(
        json_data,
        'nutritional_info',
        ['item_id', 'nutritional_info'],
        ['item_id'],
        'append'
    )

def run_pipeline(
        search_term: str, 
        num_pages: int, 
        file_store: Storage, 
        db_storage: DBStorage):
    
    rs = RecipeScraper()
    results_pages = rs.search_recipes(search_term, num_pages)
    if results_pages > 0:
        for page_num in tqdm(range(1, results_pages + 1), desc = 'Scraping progress', leave=False):
            # Get urls per page of search results
            urls = rs.get_urls(search_term, page_num)
            # Check list of urls is populated    
            if len(urls) > 0:
                # Scrape pages for results page `page_num`
                for url in tqdm(urls, desc = 'Scraping pages'):
                    # get the ID from the URL
                    item_id = url.rsplit('/', 1)[-1]
                    if not db_storage.item_exists("recipe", "item_id", item_id):
                        rs.scrape_pages(urls)
                        if len(rs.page_data) > 0:
                            store_data_files(file_store, rs.page_data, search_term)
                            # json_data = get_json_data(file_store, f"{file_store.root_folder}/{search_term}")
                            store_data_db(db_storage, rs.page_data)
                
    rs.quit()