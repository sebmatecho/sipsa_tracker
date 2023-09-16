import time
import pandas as pd
from pathlib import Path
import os
import boto3
from utils import web_scrapper, data_cleaner, aws
from dotenv import load_dotenv



if __name__ == '__main__': 
    # Loading credentials
    load_dotenv()
    aws_access_key_id = os.environ['aws_access_key_id']
    aws_secret_access_key = os.environ['aws_secret_access_key']
    
    # Creating boto3 session (access the S3 bucket)
    s3 = boto3.resource('s3',
						aws_access_key_id = aws_access_key_id, 
						aws_secret_access_key = aws_secret_access_key)
    
    # Starting time counter
    start_time = time.perf_counter()

    ######## Extracting data ########
    web_scrapper.DataCollector(s3 = s3).get_files(bucket_name = 'sipsatracker')
    
    ######### Transforming data ########
    dataframe = data_cleaner.DataWrangler(s3 = s3).building_final_file(bucket_name = 'sipsatracker')

    ######### Loading data ########
    aws.update_sipsa_file(s3 = s3, 
							dataframe = dataframe)
    
    # Ending time counter
    end_time = time.perf_counter()
    
    # Computing total processing time 
    total_time = end_time - start_time
    print(f'[Info] Total execution time {total_time:.2f}')