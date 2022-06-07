import psycopg2
from sqlalchemy.exc import ProgrammingError, OperationalError
import uuid
import pandas as pd
from pandas import json_normalize
from sqlalchemy import create_engine
from ..utils.logger import log_class
import logging

@log_class
class DBStorage:
    # Create a logger for the Locator class
    # Will be accessed by class decorator
    # which decorates each method with logging functionality
    logger = logging.getLogger(__name__)
    """
    A class with methods to save scraped data to a Postgres database

    """
    def __init__(self,
            db_conn: str):
        """
        Creates an instance of the class DBStorage
        
        Parameters
        ----------
        db_conn : str
            A valid database connction string
        """
        self.__engine = create_engine(db_conn)
        # Test connection to make sure database up etc.
        try:
            self.__engine.connect()
        except OperationalError as oe:
            raise RuntimeError(f"The database connection cannot be made (error code: {oe.code})")

    def json_to_db(self,
            data_json: dict,
            parent_table: str,
            parent_tab_cols: list,
            child_tabs: list[tuple],
            fk_column: list):
        """Normalises a json dictionary into parent and child entities
        and inserts the data into the relevant database tables

        Parameters
        ----------
        data_json : dict
            A valid json dictionary
        parent_table : str
            The name of the parent table
        parent_tab_cols : list
            (The column(s) to extract for the parent table)
        child_tabs : list[tuple]
            List of child tables and index keys paired as tuples of a string and a list
            e.g. [("table1", ["fk_col", "ind_col1"]), ("table2", ["fk_col", "ind_col2"])]
            Index columns must include the foreign key and at least one other column
            to provide a unique value for the index
        fk_column : list
            The unique column(s) for the parent table, also used as foreign key in child tables
        """
        # Get the parent table
        (json_normalize(
            data_json)[parent_tab_cols]).set_index(
            fk_column, verify_integrity=True).to_sql(
            parent_table, self.__engine, if_exists="append")
        # Get the child table(s)
        for tab in child_tabs:
            table_name, index_cols = tab
            (json_normalize(
                    data_json, [table_name], fk_column)).set_index(
                    index_cols, verify_integrity=True).to_sql(
                    table_name, self.__engine, if_exists="append")

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
            table_name: str,
            item_id_column: str,
            item_id_value: str) -> bool:
        """
        Checks if an record exists in specified owner.table for a given ID

        Parameters
        ----------
        table_name: str
            The table name
        item_id_column: str
            Name of the the ID column
        item_id_value: str
            The ID value to check

        Returns
        -------
            True if record exists (or table doesn't exist)
        """
        # check if an ID exists in the database already
        try:
            result = self.__engine.execute(
                f"""SELECT EXISTS (
                    SELECT FROM {table_name} 
                    WHERE  {item_id_column} = '{item_id_value}');
                    """)
            if result.first()[0]:
                return True
        except ProgrammingError as pe:
            if pe.code == psycopg2.errors.lookup("42P01"):
                return True
        except OperationalError as oe:
            return False

