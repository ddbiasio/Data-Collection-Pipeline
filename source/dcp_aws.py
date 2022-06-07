from package.storage.s3_storage import S3Storage
from package.storage.db_storage import DBStorage
import configparser
import logging
import pipeline
import os
import argparse

def get_db_conn() -> str:
    """Initialises the DBStorage object using settings in config.ini

    Returns
    -------
    DBStorage
        A DBStorage instance
    """    
    # RDS
    DATABASE_TYPE = config.get('RDSStorage', 'database_type')
    DBAPI = config.get('RDSStorage', 'dbapi')
    ENDPOINT = config.get('RDSStorage', 'endpoint')
    USER = config.get('RDSStorage', 'user')
    PASSWORD = config.get('RDSStorage', 'password')
    PORT = config.get('RDSStorage', 'port')
    DATABASE = config.get('RDSStorage', 'database')
    return f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}"

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--search', type=str, default="chicken")
    parser.add_argument('--pages', type=int, default=1)
    return parser.parse_args()

if __name__ == "__main__":
    # Get the data, store it on S3, upload to RDS
    # Setup log files
    logging.basicConfig(filename='./dcp_aws.log', level=logging.INFO, format='%(name)s: %(asctime)s - %(message)s', filemode="w")
    logger = logging.getLogger('dcp_aws')
    logger.info('Initialising pipeline')
    
    args = get_args()

    search_term = args.search
    search = search_term.replace(' ', '_')
    if args.pages is None:
        num_pages = 0
    else:
        num_pages = args.pages
    # Get the aws settings from config file
    config = configparser.ConfigParser()
    config_file_path = os.path.join(os.path.dirname(__file__), "config.ini")
    config.read_file(open(config_file_path))
    aws_access_key = config.get('S3Storage', 'accesskeyid')
    aws_secret_key = config.get('S3Storage', 'secretaccesskey') 
    aws_region = config.get('S3Storage', 'region') 
    logger.info(f"Running pipeline for search: {search}")
    try:
        pipeline.run_pipeline(
            search, 
            num_pages,
            S3Storage(aws_access_key, aws_secret_key, aws_region, "raw-data", search_term, "images"), 
            DBStorage(get_db_conn()))
    except RuntimeError as e:
       logger.exception(f"Exception raised in {__name__}. exception: {str(e)}")