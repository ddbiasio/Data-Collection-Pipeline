from s3_storage import S3Storage
from db_storage import DBStorage
from recipe_scaper import RecipeScraper
import json
import configparser

def init_storage(bucket: str):
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
        num_pages) -> list:

    rs = RecipeScraper()
    rs.get_recipe_data(search, num_pages)
    return rs.page_data

def save_file(s3storage: S3Storage,
        page_dict: dict,
        folder: str):

        s3storage.dict_to_json_file(
            page_dict,
            folder,
            f"{page_dict['item_id']}"
            )

def save_images(s3storage: S3Storage,
        page_dict: dict,
        folder: str):

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

        # if data has been scraped
        if len(page_data_list) > 0:
            for idx, page_dict in enumerate(page_data_list):
                folder_name = search.replace(' ', '-')
                save_file(s3storage, page_dict, search)
                save_images(s3storage, page_dict, search)

def get_json_data(s3storage: S3Storage,
        data_folder: str) -> list:

    file_list = s3storage.list_files(data_folder)
    json_list = []
    for file in file_list:
        with open(file, "r") as json_file:
            if not ".json" in json_file.name:
                pass
            else:
                item_json = s3storage.read_json_file(file)
                json_list.append(item_json)
    return json_list

def init_db():
    config = configparser.ConfigParser()
    config.read_file(open('./source/config.ini'))
    aws_access_key = config.get('RDStorage', 'database_type')

    DATABASE_TYPE = config.get('RDStorage', 'database_type')
    DBAPI = config.get('RDStorage', 'dbapi')
    ENDPOINT = config.get('RDStorage', 'endpoint')
    USER = config.get('RDStorage', 'user')
    PASSWORD = config.get('RDStorage', 'password')
    PORT = config.get('RDStorage', 'port')
    DATABASE = config.get('RDStorage', 'database')
    db_conn = f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}"
    return DBStorage(db_conn)

def store_data_db(db_storage: DBStorage,
        json_data: list):

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
    search_term = "steak"
    search = search_term.replace(' ', '_')
    recipe_data = get_data(search, 1)
    s3 = init_storage("raw-data")
    store_data_files(s3, recipe_data, search_term)
    json_data = get_json_data(s3, f"{s3.bucket_name}/{search}")
    db = init_db()
    store_data_db(db, json_data)
