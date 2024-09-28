
import sqlalchemy
from sqlalchemy import create_engine
import logging
import pandas as pd

class DataIngestor:
    def __init__(self, 
                 engine:sqlalchemy.engine.base.Engine,
                logger:logging.Logger)-> None:
        self.engine = engine
        self.logger = logger
    def insert_dataframe_to_db(self,
                               dataframe: pd.DataFrame, 
                               table_name: str)-> None:
    
        """
        Inserts a DataFrame into a PostgreSQL table.

        :param dataframe: DataFrame to be inserted.
        :param table_name: Name of the PostgreSQL table.
        :param engine: SQLAlchemy engine for the connection.

        """

        try:
            # Insert data in chunks to handle large DataFrames
            dataframe.to_sql(table_name, 
                             self.engine, 
                             if_exists='append', 
                             index=False, 
                             chunksize=500)

            self.logger.info(f"Data successfully inserted into {table_name}.")
#             print(f"Data successfully inserted into {table_name}.")

        except SQLAlchemyError as e:
            self.logger.error(f"Error inserting data: {e}")
            print(f"Error inserting data:")

        finally:
            # Close the connection
            engine.dispose()
