from file_storage import FileStorage
from db_storage import DBStorage
from recipe_scraper import RecipeScraper
import json
import configparser

def init_storage(root_folder: str):
    return FileStorage(root_folder)

def get_data(search: str,
        num_pages) -> list:

    rs = RecipeScraper()
    rs.get_recipe_data(search, num_pages)
    return rs.page_data

def save_file(fs_client: FileStorage,
        page_dict: dict,
        folder: str):

        fs_client.dict_to_json_file(
            page_dict,
            folder,
            f"{page_dict['item_id']}"
            )

def save_images(fs_client: FileStorage,
        page_dict: dict,
        folder: str):

    for url in page_dict["image_urls"]:
        # Get the file extension from the url
        file_ext = url.rsplit('/', 1)[-1].rsplit('.', 1)[-1]
        fs_client.save_image(
            url,
            folder,
            f"{page_dict['item_id']}.{file_ext}")

def store_data_files(fs_client: FileStorage,
        page_data_list: list,
        search: str):

    if len(page_data_list) > 0:
        fs = init_storage("./raw_data")
        fs.create_folder(fs.root_folder)
        # s3.create_bucket("aicore-recipes-raw-data")
        for idx, page_dict in enumerate(page_data_list):
            # create the folders for data and images
            data_folder = f"{fs.root_folder}/{search.replace(' ', '-')}"
            images_folder = f"{data_folder}/images"
            fs.create_folder(data_folder)
            fs.create_folder(images_folder)
            # save the files in the appropriate folder
            save_file(fs, page_dict, data_folder)
            save_images(fs, page_dict, images_folder)

def get_json_data(fs_client: FileStorage,
        data_folder: str) -> list:

    file_list = fs_client.list_files(data_folder)
    json_list = []
    for file in file_list:
        with open(file, "r") as json_file:
            if not ".json" in json_file.name:
                pass
            else:
                item_json = fs_client.read_json_file(file)
                json_list.append(item_json)
    return json_list

def init_db():
    # Local DB
    config = configparser.ConfigParser()
    config.read_file(open('./source/config.ini'))
    DATABASE_TYPE = config.get('DBStorage', 'database_type')
    DBAPI = config.get('DBStorage', 'dbapi')
    HOST = config.get('DBStorage', 'host')
    USER = config.get('DBStorage', 'user')
    PASSWORD = config.get('DBStorage', 'password')
    DATABASE = config.get('DBStorage', 'database')
    PORT = config.get('DBStorage', 'port')
    db_conn = f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
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
    search_term = "chocolate"
    search = search_term.replace(' ', '_')
    recipe_data = get_data(search, 1)
    fs = init_storage("./raw_data")
    store_data_files(fs, recipe_data, search_term)
    json_data = get_json_data(fs, f"{fs.root_folder}/{search}")
    db = init_db()
    store_data_db(db, json_data)
