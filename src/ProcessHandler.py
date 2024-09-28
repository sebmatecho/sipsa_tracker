
from src.DataCollector import DataCollector
from src.DataWrangler import DataWrangler
from src.FileNameBuilder import FileNameBuilder
from src.DataValidator import DataValidator
from src.DataIngestor import DataIngestor

import pandas as pd
from tqdm import tqdm
from pathlib import Path

class ProcessHandler(DataWrangler, DataIngestor, DataCollector, DataValidator, FileNameBuilder):
    def __init__(self, s3, engine, bucket_name, table_name, logger):
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
        Constructs a complete report by extracting and transforming data from two different file formats stored in an S3 bucket.
        Only processes files not marked as 'rds_load' in the files tracker.
        """
        # Fetch all files from the source
        self.get_files(self.bucket_name)

        # Generate paths for the different file formats
        first_format_paths_aws = self.first_format_paths(bucket_name=self.bucket_name)
        second_format_paths_aws = self.second_format_paths(bucket_name=self.bucket_name)

        first_format_final = pd.DataFrame()
        self.logger.info('Started working on first batch of files')

        # Process files in the first format
        for file_path in tqdm(first_format_paths_aws):
            
            file_name = Path(file_path).name
            # Skip files that are already loaded into RDS
            if not self.files_tracker_df.empty and self.files_tracker_df.loc[self.files_tracker_df['file'] == file_name, 'rds_load'].values[0] == 'yes':
#                 logger.info(f"[INFO] Skipping file {file_name} as it is already loaded into RDS.")
                continue

            dataframe = self.first_format_data_extraction(file_path)
            if not dataframe.empty:
                transformed_df = self.first_format_data_transformation(dataframe, file_path)

                # Validate DataFrame before inserting into the database
                valid_df = self.validate_dataframe(transformed_df)

                if output_dataframe:
                    first_format_final = pd.concat([first_format_final, transformed_df], ignore_index=True)
                self.insert_dataframe_to_db(dataframe=valid_df, table_name=self.table_name)
                self.update_files_tracker_with_rds_load(file_name)  # Update tracker after successful load
        self.logger.info('Started working on second batch of files')
        second_format_final = pd.DataFrame()
        
        # Process files in the second format
        for file_path in tqdm(second_format_paths_aws):
            file_name = Path(file_path).name
            # Skip files that are already loaded into RDS
            if not self.files_tracker_df.empty and self.files_tracker_df.loc[self.files_tracker_df['file'] == file_name, 'rds_load'].values[0] == 'yes':
#                 logger.info(f"[INFO] Skipping file {file_name} as it is already loaded into RDS.")
                continue

            dataframe = self.second_format_data_extraction(file_path)
            
            # Validate DataFrame before inserting into the database
            valid_df = self.validate_dataframe(dataframe)
            
            self.insert_dataframe_to_db(dataframe=valid_df, table_name=self.table_name)
            self.update_files_tracker_with_rds_load(file_name)  # Update tracker after successful load
            if output_dataframe:
                second_format_final = pd.concat([second_format_final, dataframe], ignore_index=True)

        if output_dataframe:
            complete_report = pd.concat([first_format_final, second_format_final], ignore_index=True)
            return complete_report


    def update_files_tracker_with_rds_load(self, file_name: str):
        """
        Update the 'rds_load' status in the files tracker after successful insertion into RDS.
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
        Downloads dataframe based on query pulling data from AWS RDS instance.

        Args:
            query (str): SQL query to retrieve data.

        Returns:
            pd.DataFrame with the output of query.
        """
        # Running query and importing it 
        with self.engine.begin() as conn:
            df = pd.read_sql(sql=query, con=conn)

        print(f'[Info] Data Frame with {df.shape[0]} rows and {df.shape[1]} columns imported successfully.')
        return df
