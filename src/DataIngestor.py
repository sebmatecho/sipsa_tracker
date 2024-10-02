
import sqlalchemy
from sqlalchemy import create_engine
import logging
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

class DataIngestor:
    """
    The DataIngestor class is responsible for inserting data from a Pandas DataFrame into a PostgreSQL database.
    It provides methods to handle the insertion of large DataFrames into a specified table using the SQLAlchemy engine.

    Attributes:
        engine (sqlalchemy.engine.base.Engine): The SQLAlchemy engine used to connect to the PostgreSQL database.
        logger (logging.Logger): A logger instance to log information, warnings, and errors.

    Methods:
        insert_dataframe_to_db(dataframe: pd.DataFrame, table_name: str) -> None:
            Inserts the contents of a DataFrame into a specified PostgreSQL table in chunks.
    """
    def __init__(self, 
                 engine:sqlalchemy.engine.base.Engine,
                logger:logging.Logger)-> None:
        """
        Initializes the DataIngestor with a SQLAlchemy engine and a logger instance.

        Args:
            engine (sqlalchemy.engine.base.Engine): The SQLAlchemy engine for the database connection.
            logger (logging.Logger): A logger instance for logging messages.
        """
        self.engine = engine
        self.logger = logger
        
    def insert_dataframe_to_db(self,
                               dataframe: pd.DataFrame, 
                               table_name: str)-> None:
    
        """
        Inserts a DataFrame into a PostgreSQL table. Handles large DataFrames by inserting data in chunks.

        Args:
            dataframe (pd.DataFrame): The DataFrame to be inserted into the database.
            table_name (str): The name of the PostgreSQL table where the data will be inserted.

        Returns:
            None

        Raises:
            SQLAlchemyError: If an error occurs while inserting data into the database.

        Example:
            # Create an engine and logger
            engine = create_engine("postgresql+psycopg2://user:password@localhost:5432/mydatabase")
            logger = logging.getLogger(__name__)
            
            # Initialize DataIngestor
            ingestor = DataIngestor(engine, logger)
            
            # Example DataFrame to insert
            df = pd.DataFrame({'column1': [1, 2], 'column2': ['A', 'B']})
            
            # Insert DataFrame into table 'my_table'
            ingestor.insert_dataframe_to_db(dataframe=df, table_name='my_table')
        """

        try:
            # Insert data in chunks to handle large DataFrames
            dataframe.to_sql(table_name, 
                             self.engine, 
                             if_exists='append', 
                             index=False, 
                             chunksize=500)

            self.logger.info(f"Data successfully inserted into {table_name}.")

        except SQLAlchemyError as e:
            self.logger.error(f"Error inserting data: {e}")
            raise

        finally:
            # Close the connection
            self.engine.dispose()
