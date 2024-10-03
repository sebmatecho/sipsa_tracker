
from src.logging_setup import setup_logger
from src.ProcessHandler import ProcessHandler
from dotenv import load_dotenv
from sqlalchemy import create_engine
import boto3
import os

# Loading credentials
def run_project():
    load_dotenv()
    aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
    aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
        
    db_user = os.environ['DB_USER']
    db_pass = os.environ['DB_PASS']
    db_host = os.environ['DB_HOST']
    db_port = os.environ['DB_PORT']
    db_name = os.environ['DB_NAME']

    table_name = os.environ['TABLE_NAME']
    bucket_name = os.environ['BUCKET_NAME']


    # Creating connection to database
    engine = create_engine(f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}')

    # Creating boto3 session (access the S3 bucket)
    s3 = boto3.resource('s3',
                        aws_access_key_id = aws_access_key_id, 
                        aws_secret_access_key = aws_secret_access_key)

    # Initialize logger
    logger, upload_log_to_s3 = setup_logger(s3 = s3)


    sipsa_process = ProcessHandler(s3 = s3, 
                                engine = engine, 
                                bucket_name = bucket_name, 
                                table_name = table_name, 
                                logger = logger)

    sipsa_process.executing_process()
    upload_log_to_s3(bucket_name = bucket_name)

if __name__ == "__main__": 
    run_project()