from package.storage.s3_storage import S3Storage
from package.storage.db_storage import DBStorage
from package.scraper.recipe_scraper import RecipeScraper
import json
import configparser

def init_storage(bucket: str) -> S3Storage:
    """Initialises the S3Storage object using config.ini settings

    Parameters
    ----------
    bucket : str
        Name of the bucket to create on initialisation

    Returns
    -------
    S3Storage
       S3Storage instance
    """    
    # Get the aws settings from config file
    config = configparser.ConfigParser()
    config.read_file(open('./source/config.ini'))
    aws_access_key = config.get('S3Storage', 'accesskeyid')
    aws_secret_key = config.get('S3Storage', 'secretaccesskey') 
    aws_user = config.get('S3Storage', 'iamuser') 
    aws_region = config.get('S3Storage', 'region') 
    
    return S3Storage(
            aws_access_key,
            aws_secret_key,
            aws_region,
            aws_user,
            bucket)

def get_data(search: str,
        num_pages: int) -> list:
    """Initialises a RecipeSraper object and gets the data

    Parameters
    ----------
    search : str
        Keyword(s) for recipe search
    num_pages : int
        Number of search pages to get links from

    Returns
    -------
    list
        List of dictionaries containing recipe data
    """    
    rs = RecipeScraper()
    rs.get_recipe_data(search, num_pages)
    return rs.page_data

def save_file(s3storage: S3Storage,
        page_dict: dict,
        folder: str):
    """Saves a file to S3 bucket

    Parameters
    ----------
    s3storage : S3Storage
        An S3Storage instance
    page_dict : dict
        A dictionary containing recipe data
    folder : str
        Folder name to construct key for the object storage
    """        
    s3storage.dict_to_json_file(
        page_dict,
        folder,
        f"{page_dict['item_id']}"
        )

def save_images(s3storage: S3Storage,
        page_dict: dict,
        folder: str):
    """Saves the images to S3 bucket in the recipe dictionary

    Parameters
    ----------
    s3storage : S3Storage
        An S3Storage instance
    page_dict : dict
        A dictionary containing recipe data
    folder : str
        Folder name to construct key for the object storage
    """
    for url in page_dict["image_urls"]:
        # Get the file extension from the url
        file_ext = url.rsplit('/', 1)[-1].rsplit('.', 1)[-1]
        s3storage.save_image(
            url,
            folder,
            f"{page_dict['item_id']}.{file_ext}")

def store_data_files(s3storage: S3Storage,
        page_data_list: list,
        search: str):
    """Saves each recipe and images to S3

    Parameters
    ----------
    s3storage : S3Storage
        An S3Storage instance
    page_data_list : list
        List of recipe dictionaries
    search : str
        Search keywords used (will be used to construct keys for objects)
    """
    # if data has been scraped
    if len(page_data_list) > 0:
        for idx, page_dict in enumerate(page_data_list):
            folder_name = search.replace(' ', '-')
            save_file(s3storage, page_dict, search)
            save_images(s3storage, page_dict, search)

def get_json_data(s3storage: S3Storage,
        data_folder: str) -> list:
    """Returns a list of json strings from files in an S3 bucket

    Parameters
    ----------
    s3storage : S3Storage
        An S3Storage instance
    data_folder : str
        The folder to get the files from

    Returns
    -------
    list
       List of recipes as json strings
    """
    file_list = s3storage.list_files(data_folder, "json")
    json_list = []
    for file in file_list:
        item_json = s3storage.read_json_file(file)
        json_list.append(item_json)
    return json_list

def init_db() -> DBStorage:
    """Initialises the DBStorage object using settings in config.ini

    Returns
    -------
    DBStorage
        A DBStorage instance  
    """    
    config = configparser.ConfigParser()
    config.read_file(open('./source/config.ini'))
    aws_access_key = config.get('RDSStorage', 'database_type')

    DATABASE_TYPE = config.get('RDSStorage', 'database_type')
    DBAPI = config.get('RDSStorage', 'dbapi')
    ENDPOINT = config.get('RDSStorage', 'endpoint')
    USER = config.get('RDSStorage', 'user')
    PASSWORD = config.get('RDSStorage', 'password')
    PORT = config.get('RDSStorage', 'port')
    DATABASE = config.get('RDSStorage', 'database')
    db_conn = f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}"
    return DBStorage(db_conn)

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
    'replace')

    db_storage.store_child_df(
        json_data,
        'ingredients',
        ['item_id', 'ingredient'],
        ['item_id'],
        'replace'
    )
    db_storage.store_child_df(
        json_data,
        'method',
        ['item_id', 'method_step'],
        ['item_id'],
        'replace'
    )
    db_storage.store_child_df(
        json_data,
        'planning_info',
        ['item_id', 'prep_stage'],
        ['item_id'],
        'replace'
    )
    db_storage.store_child_df(
        json_data,
        'nutritional_info',
        ['item_id', 'nutritional_info'],
        ['item_id'],
        'replace'
    )

if __name__ == "__main__":
    # Get the data, store it on S3, upload to RDS
    search_term = "prawn"
    search = search_term.replace(' ', '_')
    recipe_data = get_data(search, 1)
    s3 = init_storage("raw-data")
    store_data_files(s3, recipe_data, search_term)
    json_data = get_json_data(s3, f"{search}")
    db = init_db()
    store_data_db(db, json_data)
