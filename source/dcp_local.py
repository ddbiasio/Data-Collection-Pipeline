from package.storage.file_storage import FileStorage
import pipeline
import configparser
import os
from source.package.storage.db_storage import DBStorage
import logging

def get_db_conn() -> str:
    """Initialises the DBStorage object using settings in config.ini

    Returns
    -------
    DBStorage
        A DBStorage instance
    """    
    # Local DB
    config = configparser.ConfigParser()
    config_file_path = os.path.join(os.path.dirname(__file__), "config.ini")
    config.read_file(open(config_file_path))
    DATABASE_TYPE = config.get('DBStorage', 'database_type')
    DBAPI = config.get('DBStorage', 'dbapi')
    HOST = config.get('DBStorage', 'host')
    USER = config.get('DBStorage', 'user')
    PASSWORD = config.get('DBStorage', 'password')
    DATABASE = config.get('DBStorage', 'database')
    PORT = config.get('DBStorage', 'port')
    return f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

if __name__ == "__main__":
    # Setup log files
    logging.basicConfig(filename='./dcp_local.log', level=logging.INFO, format='%(name)s: %(asctime)s - %(message)s', filemode="w")
    logger = logging.getLogger('dcp_local')
    logger.info('Initialising pipeline')
    search_term = "pear"
    search = search_term.replace(' ', '_')
    root_folder = "./raw_data"
    data_folder = f"{root_folder}/{search}"
    images_folder = f"{root_folder}/{search}/images"
    logger.info(f"Running pipeline for search: {search}")
    try:
        pipeline.run_pipeline(
            search, 
            1,
            FileStorage("./raw_data", data_folder, images_folder), 
            DBStorage(get_db_conn()))
    except RuntimeError as e:
       logger.exception(f"Exception raised in {__name__}. exception: {str(e)}")