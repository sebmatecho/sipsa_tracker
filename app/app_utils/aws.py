import boto3
import os
import pandas as pd
from dotenv import load_dotenv
from io import BytesIO
from sqlalchemy import create_engine
from botocore.exceptions import ClientError

class DataPipelineManager:
    def __init__(self):
        """
        Initializes the DataPipelineManager class, loading environment variables and setting up S3 and RDS connections.
        """
        load_dotenv()

        # Initialize AWS credentials
        self.aws_access_key_id = os.environ['aws_access_key_id']
        self.aws_secret_access_key = os.environ['aws_secret_access_key']
        self.bucket_name = os.environ['BUCKET_NAME']
        
        # Initialize S3 resource
        self.s3 = boto3.resource('s3',
                                aws_access_key_id=self.aws_access_key_id, 
                                aws_secret_access_key=self.aws_secret_access_key)

        # Initialize RDS database credentials
        self.db_user = os.environ['db_user']
        self.db_pass = os.environ['db_pass']
        self.db_host = os.environ['db_host']
        self.db_port = os.environ['db_port']
        self.db_name = os.environ['db_name']
        self.engine = create_engine(f'postgresql://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}')
    
    def queries_on_rds(self, query: str) -> pd.DataFrame:
        """
        Executes a SQL query on the RDS PostgreSQL database and returns the result as a pandas DataFrame.

        Args:
            query (str): The SQL query to execute.

        Returns:
            pd.DataFrame: The result of the SQL query.
        """
        with self.engine.begin() as conn:
            dataframe = pd.read_sql(sql=query, con=conn)
        return dataframe

    def get_files_tracker_from_s3(self, file_name: str = 'files_tracker.csv') -> pd.DataFrame:
        """
        Retrieves the 'files_tracker.csv' from the S3 bucket and returns its content as a pandas DataFrame.

        Args:
            file_name (str): The name of the file to retrieve from S3.

        Returns:
            pd.DataFrame: The content of the file as a pandas DataFrame.
        """
        try:
            obj = self.s3.Object(self.bucket_name, file_name)
            csv_content = obj.get()['Body'].read()
            df = pd.read_csv(BytesIO(csv_content))
            return df
        except ClientError as e:
            print(f"Error retrieving file from S3: {e}")
            return pd.DataFrame()

    def log_files_manager(self, log_file: str = None, log_prefix: str = 'logs/') -> list:
        """
        Lists or retrieves log files from the S3 bucket. If a log file is provided, its content is loaded into a pandas DataFrame.

        Args:
            log_file (str, optional): The specific log file to retrieve. Defaults to None, in which case all log files are listed.
            log_prefix (str, optional): The prefix where log files are stored. Defaults to 'logs/'.

        Returns:
            list: A list of log file names if log_file is None.
            pd.DataFrame: The content of the log file as a pandas DataFrame if log_file is provided.
        """
        if log_file is None:
            try:
                bucket = self.s3.Bucket(self.bucket_name)
                log_files = [obj.key for obj in bucket.objects.filter(Prefix=log_prefix) if obj.key.endswith('.log')]
                return log_files
            except ClientError as e:
                print(f"Error listing log files from S3: {e}")
                return []
        else:
            try:
                obj = self.s3.Object(self.bucket_name, log_file)
                log_content = obj.get()['Body'].read().decode('utf-8')
                log_lines = log_content.splitlines()
                log_data = [line.split(' - ', maxsplit=2) for line in log_lines if len(line.split(' - ', maxsplit=2)) == 3]
                df = pd.DataFrame(log_data, columns=['timestamp', 'level', 'message'])
                return df
            except ClientError as e:
                print(f"Error reading log file {log_file} from S3: {e}")
                return pd.DataFrame()



class AppDataManager:
    def __init__(self):
        """
        Initializes the AppDataManager class, loading environment variables and setting up S3 and RDS connections.
        """
        load_dotenv()


        # Initialize RDS database credentials
        self.db_user = os.environ['db_user']
        self.db_pass = os.environ['db_pass']
        self.db_host = os.environ['db_host']
        self.db_port = os.environ['db_port']
        self.db_name = os.environ['db_name']
        self.engine = create_engine(f'postgresql://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}')
    
    def queries_on_rds(self, query: str) -> pd.DataFrame:
        """
        Executes a SQL query on the RDS PostgreSQL database and returns the result as a pandas DataFrame.

        Args:
            query (str): The SQL query to execute.

        Returns:
            pd.DataFrame: The result of the SQL query.
        """
        with self.engine.begin() as conn:
            dataframe = pd.read_sql(sql=query, con=conn)
        return dataframe

    