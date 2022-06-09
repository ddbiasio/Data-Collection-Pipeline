import configparser
import os
config = configparser.ConfigParser()

config['DBStorage'] = {'DATABASE_TYPE': 'postgresql',
                        'DBAPI': 'psycopg2',
                        'HOST': 'localhost',
                        'USER': 'postgres',
                        'PASSWORD': 'C0balamin',
                        'DATABASE': 'dcp',
                        'PORT': '5432'}

config['RDSStorage'] = {'DATABASE_TYPE': 'postgresql',
                        'DBAPI': 'psycopg2',
                        'ENDPOINT': 'aicoredb.cadmkvwd3lux.eu-west-2.rds.amazonaws.com',
                        'USER': 'postgres',
                        'PASSWORD': 'C0balamin',
                        'DATABASE': 'postgres',
                        'PORT': '5432'}

config_file = os.path.join(os.path.dirname(__file__), "config.ini")

with open(config_file, 'w') as configfile:
    config.write(configfile)