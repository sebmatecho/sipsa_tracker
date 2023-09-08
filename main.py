import time
import pandas as pd
from pathlib import Path
import os

from utils import web_scrapping, file_names, data_wrangling, aws

from dotenv import load_dotenv



if __name__ == '__main__': 
    # Loading credentials
    load_dotenv()
    aws_access_key_id = os.environ['aws_access_key_id']
    aws_secret_access_key = os.environ['aws_secret_access_key']

    # Starting time counter
    start_time = time.perf_counter()

    ######## Extracting data ########
    web_scrapping.data_gathering()
    
    ######## Transforming data ########
    
    # First format data (All data within same tab)
    print('Working on first format batch')
    first_batch = data_wrangling.first_format_wrangling(file_names.first_format_paths())

    # Second format data (with tabs within spreadsheets)
    print('Working on second format batch')
    second_batch = data_wrangling.second_format_wrangling(file_names.second_format_paths())

    # Merging and cleaning resulting data
    final_dataframe = pd.concat([first_batch, second_batch], ignore_index = True)
    final_dataframe = data_wrangling.data_preparation(final_dataframe)


    # Updating resulting file on AWS bucket
    aws.update_sipsa_file(aws_access_key_id = aws_access_key_id, 
                          aws_secret_access_key = aws_secret_access_key, 
                          dataframe = final_dataframe)
    
    # Ending time counter
    end_time = time.perf_counter()
    
    # Computing total processing time 
    total_time = end_time - start_time
    print(f'[Info] Total execution time {total_time:.2f}')