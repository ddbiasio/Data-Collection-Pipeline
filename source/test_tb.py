import configparser

from sqlalchemy import create_engine
from file_storage import FileStorage
import pandas as pd
from pandas import json_normalize
import json
from db_storage import DBStorage

fs = FileStorage("/home/siobhan/code/projects/Data-Collection-Pipeline/raw_data")
data_folder = f"{fs.root_folder}/chicken"
file_list = fs.list_files(data_folder)
recipe_list = []
for file in file_list:
    with open(file, "r") as json_file:
        if not ".json" in json_file.name:
            pass
        else:
            item_json = fs.read_json_file(file)
            recipe_list.append(item_json)

# df_ingred = json_normalize(
#     recipe_list,
#     record_path=['ingredients'],
#     meta=['item_id'],
#     sep="_"
# )

# df_method = json_normalize(
#     recipe_list,
#     record_path=['method'],
#     meta=['item_id'],
#     sep="_"
# )

# df_nutritional_info = json_normalize(
#     recipe_list,
#     record_path=['nutritional_info'],
#     meta=['item_id'],
#     sep="_")

# df_planning_info = json_normalize(
#     recipe_list,
#     record_path=['planning_info'],
#     meta=['item_id'],
#     sep="_"
# ) 
# Local DB
# DATABASE_TYPE = 'postgresql'
# DBAPI = 'psycopg2'
# HOST = 'localhost'
# USER = 'postgres'
# PASSWORD = 'C0balamin'
# DATABASE = 'pagila'
# PORT = 5432
# db_conn = f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

# RDS
DATABASE_TYPE = 'postgresql'
DBAPI = 'psycopg2'
ENDPOINT = 'aicoredb.cadmkvwd3lux.eu-west-2.rds.amazonaws.com' # Change it for your AWS endpoint
USER = 'postgres'
PASSWORD = 'C0balamin'
PORT = 5432
DATABASE = 'postgres'
db_conn = f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}"

db_storage = DBStorage(db_conn)
db_storage.store_parent_df(
    recipe_list, 
    'recipe', 
    ['item_id'], 
    ['item_id', 'recipe_name', 'item_UUID','image_urls'],
    'replace')

db_storage.store_child_df(
    recipe_list,
    'ingredients',
    ['item_id', 'ingredient'],
    ['item_id'],
    'replace'
)
db_storage.store_child_df(
    recipe_list,
    'method',
    ['item_id', 'method_step'],
    ['item_id'],
    'replace'
)
db_storage.store_child_df(
    recipe_list,
    'planning_info',
    ['item_id', 'prep_stage'],
    ['item_id'],
    'replace'
)

db_storage.store_child_df(
    recipe_list,
    'nutritional_info',
    ['item_id', 'nutritional_info'],
    ['item_id'],
    'replace'
)

eng = create_engine(db_conn)
rs = eng.execute("""SELECT * FROM recipe;""")
for row in rs:
    print(row)