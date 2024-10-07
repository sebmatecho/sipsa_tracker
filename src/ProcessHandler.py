
# from src.DataCollector import DataCollector
# from src.DataWrangler import DataWrangler
# from src.FileNameBuilder import FileNameBuilder
# from src.DataValidator import DataValidator
# from src.DataIngestor import DataIngestor

from DataCollector import DataCollector
from DataWrangler import DataWrangler
from FileNameBuilder import FileNameBuilder
from DataValidator import DataValidator
from DataIngestor import DataIngestor

import pandas as pd
from tqdm import tqdm
from pathlib import Path
import boto3
import logging
import sqlalchemy

class ProcessHandler(DataWrangler, DataIngestor, DataCollector, DataValidator, FileNameBuilder):
    """
    The ProcessHandler class orchestrates the entire process of collecting, transforming, validating, 
    and ingesting data from S3 into a PostgreSQL database. It combines functionalities from multiple classes 
    to handle different stages of data processing, ensuring efficient and robust data management.

    Inheritance:
        DataWrangler: For data extraction and transformation.
        DataIngestor: For data insertion into PostgreSQL.
        DataCollector: For collecting and tracking files from S3.
        DataValidator: For validating data against predefined criteria.
        FileNameBuilder: For constructing paths for files in the S3 bucket.

    Attributes:
        s3 (boto3.resource): The S3 resource for interacting with AWS S3.
        engine (sqlalchemy.engine.base.Engine): The SQLAlchemy engine for the PostgreSQL database connection.
        bucket_name (str): The name of the S3 bucket to interact with.
        table_name (str): The name of the PostgreSQL table to which data will be ingested.
        logger (logging.Logger): Logger instance for logging process information.
        files_tracker_df (pd.DataFrame): DataFrame tracking processed files and their status.

    Methods:
        __init__(self, s3, engine, bucket_name, table_name, logger):
            Initializes the ProcessHandler with necessary attributes and loads the file tracker.

        executing_process(self, output_dataframe: bool = False) -> pd.DataFrame:
            Executes the data processing workflow, including data extraction, transformation, validation, and ingestion.

        update_files_tracker_with_rds_load(self, file_name: str):
            Updates the file tracker in S3 with the status of files loaded into the RDS.

        querying_db(self, query: str) -> pd.DataFrame:
            Executes a query on the PostgreSQL database and returns the result as a DataFrame.
    """
    def __init__(self, 
                 s3:boto3.resource, 
                 engine:sqlalchemy.engine.base.Engine, 
                 bucket_name:str, 
                 table_name:str, 
                 logger:logging.Logger):
        """
        Initializes the ProcessHandler with necessary resources and configurations.

        Args:
            s3 (boto3.resource): The S3 resource to interact with AWS S3.
            engine (sqlalchemy.engine.base.Engine): The SQLAlchemy engine for the PostgreSQL database connection.
            bucket_name (str): The name of the S3 bucket.
            table_name (str): The name of the table in the PostgreSQL database.
            logger (logging.Logger): Logger instance for logging information.

        Initializes the base classes and sets up the files tracker.
        """
        # Initialize DataCollector and other base classes
        
        DataCollector.__init__(self, s3, logger)
        DataIngestor.__init__(self, engine, logger)
        DataWrangler.__init__(self, bucket_name, s3, logger)
        DataValidator.__init__(self, logger)
        FileNameBuilder.__init__(self, s3, logger)
        # Set class attributes
        self.s3 = s3
        self.engine = engine
        self.bucket_name = bucket_name
        self.table_name = table_name
        self.logger = logger

        # Load files tracker after initializing the DataCollector
        self.files_tracker_df = self.load_files_tracker(self.bucket_name)  
        
        # Ensure 'rds_load' column exists in the files_tracker_df
        if 'rds_load' not in self.files_tracker_df.columns:
            self.files_tracker_df['rds_load'] = 'no'
        
#         self.data_validator = DataValidator()  # Initialize the DataValidator

    def executing_process(self, output_dataframe: bool = False) -> pd.DataFrame:
        """
        Executes the complete data processing workflow, including:
        1. Checking for files in the S3 bucket.
        2. Downloading files from SIPSA webpage if not present in S3.
        3. Processing the files and uploading the data to the database if not already in RDS.
        4. Updating the tracker file within S3.

        Args:
            output_dataframe (bool): If True, returns the final concatenated DataFrame from all processed files.

        Returns:
            pd.DataFrame: The concatenated DataFrame of all processed files if output_dataframe is True. Otherwise, returns None.
        """
        # Fetch all files from the S3 bucket
        self.get_files(self.bucket_name)

        # Generate paths for the different file formats
        first_format_paths_aws = self.first_format_paths(bucket_name=self.bucket_name)
        second_format_paths_aws = self.second_format_paths(bucket_name=self.bucket_name)

        first_format_final = pd.DataFrame()
        self.logger.info('Started working on first batch of files')

        # Process files in the first format
        for file_path in tqdm(first_format_paths_aws):
            file_name = Path(file_path).name

            # Check if the file is already in the S3 bucket, if not, download it from SIPSA
            if file_name not in [Path(f).name for f in first_format_paths_aws]:
                self.logger.info(f"Downloading {file_name} from SIPSA webpage as it is not present in S3.")
                self.download_file_from_sipsa(file_name)

            # Skip files already loaded into RDS
            try:
                if not self.files_tracker_df.empty and self.files_tracker_df.loc[self.files_tracker_df['file'] == file_name, 'rds_load'].values[0] == 'yes':
                    self.logger.info(f"Skipping file {file_name} as it is already loaded into RDS.")
                    continue
            except: 
                None

            # Extract data from the first format file
            dataframe = self.first_format_data_extraction(file_path)
            if not dataframe.empty:
                transformed_df = self.first_format_data_transformation(dataframe, file_path)

                # Validate DataFrame before inserting into the database
                valid_df = self.validate_dataframe(transformed_df)

                if output_dataframe:
                    first_format_final = pd.concat([first_format_final, transformed_df], ignore_index=True)

                # Insert into the database and update the tracker
                self.insert_dataframe_to_db(dataframe=valid_df, table_name=self.table_name)
                self.update_files_tracker_with_rds_load(file_name)  # Update tracker after successful load

        self.logger.info('Started working on second batch of files')
        second_format_final = pd.DataFrame()

        # Process files in the second format
        for file_path in tqdm(second_format_paths_aws):
            file_name = Path(file_path).name

            # Check if the file is already in the S3 bucket, if not, download it from SIPSA
            if file_name not in [Path(f).name for f in second_format_paths_aws]:
                self.logger.info(f"Downloading {file_name} from SIPSA webpage as it is not present in S3.")
                self.download_file_from_sipsa(file_name)

            try:
                if not self.files_tracker_df.empty and file_name in self.files_tracker_df['file'].values:
                    if self.files_tracker_df.loc[self.files_tracker_df['file'] == file_name, 'rds_load'].values[0] == 'yes':
                        self.logger.info(f"Skipping file {file_name} as it is already loaded into RDS.")
                        continue
                else:
                    self.logger.info(f"{file_name} not found in the files tracker. Proceeding with processing.")
            except IndexError:
                self.logger.warning(f"IndexError encountered when checking RDS load status for {file_name}. Proceeding with processing.")

            # # Skip files already loaded into RDS
            # if not self.files_tracker_df.empty and \
            #         self.files_tracker_df.loc[self.files_tracker_df['file'] == file_name, 'rds_load'].values[0] == 'yes':
            #     self.logger.info(f"Skipping file {file_name} as it is already loaded into RDS.")
            #     continue

            # Extract data from the second format file
            dataframe = self.second_format_data_extraction(file_path)

            # Validate DataFrame before inserting into the database
            valid_df = self.validate_dataframe(dataframe)

            # Insert into the database and update the tracker
            self.insert_dataframe_to_db(dataframe=valid_df, table_name=self.table_name)
            self.update_files_tracker_with_rds_load(file_name)  # Update tracker after successful load

            if output_dataframe:
                second_format_final = pd.concat([second_format_final, dataframe], ignore_index=True)

        # Return the complete report if requested
        if output_dataframe:
            complete_report = pd.concat([first_format_final, second_format_final], ignore_index=True)
            return complete_report



    def update_files_tracker_with_rds_load(self, file_name: str):
        """
        Updates the 'rds_load' status in the files tracker to 'yes' after successful insertion into the RDS.

        Args:
            file_name (str): The name of the file to update in the files tracker.

        Returns:
            None
        """
        # Check if the file is already present in the tracker and update it
        if file_name in self.files_tracker_df['file'].values:
            self.files_tracker_df.loc[self.files_tracker_df['file'] == file_name, 'rds_load'] = 'yes'
        else:
            # If not present, add a new entry
            new_entry = pd.DataFrame({'file': [file_name], 'rds_load': ['yes']})
            self.files_tracker_df = pd.concat([self.files_tracker_df, new_entry], ignore_index=True)
        
        # Update the tracker in S3
        self.update_files_tracker(self.files_tracker_df, self.bucket_name)

    def querying_db(self, query: str) -> pd.DataFrame:
        """
        Executes a SQL query on the PostgreSQL database and returns the result as a DataFrame.

        Args:
            query (str): The SQL query to execute.

        Returns:
            pd.DataFrame: The result of the query as a Pandas DataFrame.

        Example:
            query = "SELECT * FROM product_prices WHERE ciudad = 'bogota'"
            result_df = self.querying_db(query=query)
        """
        # Running query and importing it 
        with self.engine.begin() as conn:
            df = pd.read_sql(sql=query, con=conn)

        print(f'[Info] Data Frame with {df.shape[0]} rows and {df.shape[1]} columns imported successfully.')
        return df
