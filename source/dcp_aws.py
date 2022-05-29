from package.storage.s3_storage import S3Storage
from package.storage.db_storage import DBStorage
import configparser
import logging
import pipeline
import os

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
    
if __name__ == "__main__":
    # Get the data, store it on S3, upload to RDS
    # Setup log files
    logging.basicConfig(filename='dcp_was.log', level=logging.INFO, format='%(asctime)s - %(message)s', filemode="w")
    logging.info('Initialising pipeline')
    search_term = "noodles"
    search = search_term.replace(' ', '_')

    # Get the aws settings from config file
    config = configparser.ConfigParser()
    config.read_file(open('./source/config.ini'))
    aws_access_key = config.get('S3Storage', 'accesskeyid')
    aws_secret_key = config.get('S3Storage', 'secretaccesskey') 
    aws_region = config.get('S3Storage', 'region') 
    logging.info(f"Running pipeline for search: {search}")
    pipeline.run_pipeline(
        search, 
        2,
        S3Storage(aws_access_key, aws_secret_key, aws_region, "raw-data", search_term, "images"), 
        DBStorage(get_db_conn()))