import configparser
import json
import sqlalchemy
import uuid
import os
from .file_storage import FileStorage
import pandas as pd
from pandas import DataFrame, json_normalize
import psycopg2
from sqlalchemy import create_engine

class DBStorage:

    """
    A class with methods to save scraped data to a Postgres database

    Methods
    -------
    store_parent_df(data_json: str, table_name: str, index_cols: list, column_list: list, table_action: str) -> DataFrame
    store_child_df(data_json: json, table_name: str, index_cols: list, record_fk: str, table_action: str) -> DataFrame
    upsert_df(df: pd.DataFrame, table_name: str) -> bool
    item_exists(table_owner: str, table_name: str, item_id_column: str, item_id_value: str) -> bool
    """
    def __init__(self,
            db_conn: str):
        """
        Creates an instance of the class DBStorage
        
        Parameters
        ----------
        db_conn: str
            A valid database connction string
        """
        self.__engine = create_engine(db_conn)
       
    def store_parent_df(self,
            data_json: str,
            table_name: str,
            index_cols: list,
            column_list: list,
            table_action: str) -> None:
        """
        Normalises a string in json format into a pandas DataFrame and uploads to database (parent table)

        Parameters
        ----------
        data_json: str
            Data in the format of a json string
        table_name: str
            The nameof the table where data will be inserted
        index_cols: list
            A list of columns to be used as indexes in the DataFrame
        column_list: list
            The list of column names to be extracted from the json
        table_action: str
            How to behave if the table already exists (fail, replace, append) 
        """
        df = (json_normalize(
                data_json)[column_list].copy()
                .set_index(index_cols, verify_integrity=True))
        df.to_sql(table_name, self.__engine, if_exists=table_action, index=True)

    def store_child_df(self,
            data_json: json,
            table_name: str,
            index_cols: list,
            record_fk: str,
            table_action: str):

        """
        Normalises a string in json format into a pandas DataFrame and uploads to database (child table)

        Parameters
        ----------
        data_json: str
            Data in the format of a json string
        table_name: str
            The nameof the table where data will be inserted
        index_cols: list
            A list of columns to be used as indexes in the DataFrame
        record_fk: str
            The column which will be the foreign key to the parent table
        table_action: str
            How to behave if the table already exists (fail, replace, append) 
        """
        df = json_normalize(
                    data_json,
                    record_path=[table_name],
                    meta=[record_fk]
                    ).set_index(index_cols)
        df.to_sql(table_name, self.__engine, if_exists=table_action, index=True)

    def upsert_df(self,
        df: pd.DataFrame, 
        table_name: str) -> bool:
        """Implements the equivalent of pd.DataFrame.to_sql(..., if_exists='update')
        (which does not exist). Creates or updates the db records based on the
        dataframe records.
        Conflicts to determine update are based on the dataframes index.
        This will set unique keys constraint on the table equal to the index names
        1. Create a temp table from the dataframe
        2. Insert/update from temp table into table_name
        Parameters
        ----------
        df: pd.DataFrame
            A pandas DataFrame
        table_name:
            The table name to perform the upsert against
        Returns
        -------
            True if successful
        """
        # If the table does not exist
        # we should just use to_sql to create it
        if not self.__engine.execute(
            f"""SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE  table_schema = 'public'
                AND    table_name   = '{table_name}');
                """
        ).first()[0]:
            df.to_sql(table_name, self.__engine)
            return True

        # If it already exists create a temp table
        # for the data frame to hold for processing
        temp_table_name = f"temp_{uuid.uuid4().hex[:6]}"
        df.to_sql(temp_table_name, self.__engine, index=True)

        index = list(df.index.names)
        index_sql_txt = ", ".join([f'"{i}"' for i in index])
        columns = list(df.columns)
        headers = index + columns
        headers_sql_txt = ", ".join(
            [f'"{i}"' for i in headers]
        )  # index1, index2, ..., column 1, col2, ...

        # col1 = exluded.col1, col2=excluded.col2
        update_column_stmt = ", ".join([f'"{col}" = EXCLUDED."{col}"' for col in columns])

        # For the ON CONFLICT clause, postgres requires that the columns have unique constraint
        query_pk = f"""
        ALTER TABLE "{table_name}" DROP CONSTRAINT IF EXISTS unique_constraint_for_upsert;
        ALTER TABLE "{table_name}" ADD CONSTRAINT unique_constraint_for_upsert UNIQUE ({index_sql_txt});
        """
        self.__engine.execute(query_pk)

        # Compose and execute upsert query
        query_upsert = f"""
        INSERT INTO "{table_name}" ({headers_sql_txt}) 
        SELECT {headers_sql_txt} FROM "{temp_table_name}"
        ON CONFLICT ({index_sql_txt}) DO UPDATE 
        SET {update_column_stmt};
        """
        self.__engine.execute(query_upsert)
        self.__engine.execute(f"DROP TABLE {temp_table_name}")

        return True

    def item_exists(self,
            table_owner: str,
            table_name: str,
            item_id_column: str,
            item_id_value: str) -> bool:
        """
        Checks if an record exists in a specified table for a given ID

        Parameters
        ----------
        table_owner: str
            The table owner
        table_name: str
            The table name
        item_id_column: str
            Name of the the ID column
        item_id_value: str
            The ID value to check

        Returns
        -------
            True if record exists
        """
        # check if an ID exists in the database already
        if self.__engine.execute(
            f"""SELECT EXISTS (
                SELECT FROM {table_owner}.{table_name} 
                WHERE  {item_id_column} = '{item_id_value}');
                """
        ).first()[0]:
            return True
