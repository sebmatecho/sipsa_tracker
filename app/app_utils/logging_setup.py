import logging
import sys
from pathlib import Path
import boto3
from dotenv import load_dotenv
import os
from logging.handlers import RotatingFileHandler
import atexit
from concurrent.futures import ThreadPoolExecutor

def setup_logger(s3_key_prefix: str = "app_logs/"):
    load_dotenv()
    aws_access_key_id = os.environ['aws_access_key_id']
    aws_secret_access_key = os.environ['aws_secret_access_key']
    bucket_name = os.environ['BUCKET_NAME']
    
    s3 = boto3.resource('s3',
                        aws_access_key_id=aws_access_key_id, 
                        aws_secret_access_key=aws_secret_access_key)

    log_path = Path.cwd() / 'app_logs'
    log_path.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    c_handler = logging.StreamHandler(sys.stdout)
    file_name = f'sipsapp_usage.log'
    f_handler = RotatingFileHandler(log_path / file_name, maxBytes=5*1024*1024, backupCount=3)

    c_handler.setLevel(logging.ERROR)
    f_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)
    
    executor = ThreadPoolExecutor(max_workers=1)

    def upload_log_to_s3():
        try:
            with open(log_path / file_name, "rb") as f:
                s3.Bucket(bucket_name).put_object(Key=s3_key_prefix + file_name, Body=f)
            logger.info(f"Log file uploaded to S3: s3://{bucket_name}/{s3_key_prefix}{file_name}")
        except Exception as e:
            logger.error(f"Failed to upload log file to S3: {e}")

    # Schedule log upload at exit
    atexit.register(lambda: executor.submit(upload_log_to_s3))

    return logger, upload_log_to_s3
