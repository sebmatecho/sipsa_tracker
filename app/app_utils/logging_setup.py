
import logging
import sys
from pathlib import Path
from datetime import datetime
import boto3
from dotenv import load_dotenv
import os

# Configure logging
def setup_logger(s3_key_prefix: str = "app_logs/"):
    """
    Sets up and configures a logger for the application.

    This function creates a logger that outputs log messages both to the console (stdout) and a log file. 
    It ensures the log directory and file are created if they do not already exist.

    The log messages include the timestamp, log level, and message. The log level is set to `INFO` for 
    both console and file handlers, meaning that messages of level `INFO` and higher will be recorded.

    Returns:
        logger (logging.Logger): Configured logger object for the application.

    Logging Details:
        - Log Directory: A directory named 'logs' is created in the current working directory if it does not exist.
        - Log File: Logs are written to 'sipsa_process.log' in the 'logs' directory.
        - Log Format: '%(asctime)s - %(levelname)s - %(message)s'
        - Log Levels: Both console and file handlers are set to `INFO`.
        - Handlers:
            - Console (`stdout`) Handler: Outputs logs to the console.
            - File Handler: Outputs logs to 'sipsa_process.log' with overwrite mode (`mode='w'`).
    
    Example Usage:
        >>> logger = setup_logger()
        >>> logger.info("Logger is successfully configured.")

    Last update:
        Nov 28, 2024. 
    """
    load_dotenv()
    aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
    aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
    bucket_name = os.environ['BUCKET_NAME']
    
    # Creating boto3 session (access the S3 bucket)
    s3 = boto3.resource('s3',
                        aws_access_key_id = aws_access_key_id, 
                        aws_secret_access_key = aws_secret_access_key)

    
    # Create logfile path
    log_path = Path.cwd()/'app_logs'
    if not log_path.exists():
        print(f'{log_path} created successfully')
        log_path.mkdir(parents = True, 
                   exist_ok = True)
        
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create handlers
    today_date = datetime.today().strftime(format = '%m_%d_%Y')
    c_handler = logging.StreamHandler(sys.stdout)
    file_name = f'sipsapp_usage_{today_date}.log'
    f_handler = logging.FileHandler(log_path/file_name, mode='w')

    # Set levels
    c_handler.setLevel(logging.ERROR)
    f_handler.setLevel(logging.INFO)

    # Create formatters and add them to handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    
    def upload_log_to_s3(bucket_name = bucket_name, 
                         s3 = s3, 
                         file_name = file_name):
        logger.info(f"Uploading log file  to S3 bsucket {s3}")
        try:
            with open(f'app_logs/{file_name}', "rb") as f:
                 s3.Bucket(bucket_name).put_object(Key=s3_key_prefix + file_name, Body=f)
            logger.info(f"Log file uploaded to S3: s3://{s3}/{s3_key_prefix}{file_name}")
        except Exception as e:
            logger.error(f"Failed to upload log file to S3: {e}")
    # Return the logger and upload function
    return logger, upload_log_to_s3