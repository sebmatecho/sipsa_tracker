
import boto3
import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
import datetime
from io import BytesIO
from typing import List
from botocore.exceptions import ClientError
from pathlib import Path
from tqdm import tqdm
import logging

class DataCollector:    
    """
    A class used to collect, manage, and store data files from the DANE website into an S3 bucket.

    This class interacts with the DANE website to fetch and download data files. It checks the existence
    of files in an S3 bucket and updates a file tracker to ensure no duplicate downloads occur. It also provides
    methods to upload or update files in the S3 bucket, as well as methods to display the tracking information.
    

    Attributes:
        s3 (boto3.resource): An S3 resource object to interact with AWS S3.
        url_base (str): The base URL of the DANE website.
        url (str): The URL of the DANE webpage for the data.
        headers (dict): HTTP headers used for web requests.
        files_tracker_name (str): The name of the file tracker CSV in S3.
        logfile_name (str): The name of the log file.
        logger (logging.Logger): Logger instance for logging messages.

    Methods:
        __init__(s3: boto3.resource, logger: logging.Logger) -> None:
            Initializes the DataCollector with S3 resource and logger.

        all_years_links() -> List[BeautifulSoup]:
            Fetches the set of year links available on the DANE webpage.

        links_per_year(link: BeautifulSoup) -> List[BeautifulSoup]:
            Retrieves all report links for a specific year.

        check_file_exists_in_s3(bucket_name: str, file_name: str) -> bool:
            Checks if a specific file already exists in the S3 bucket.

        load_files_tracker(bucket_name: str) -> pd.DataFrame:
            Loads the files_tracker.csv from S3 or creates a new DataFrame if it does not exist.

        update_files_tracker(df: pd.DataFrame, bucket_name: str):
            Updates the files_tracker.csv in S3.

        upload_or_update_dataframe_to_s3(df: pd.DataFrame, bucket_name: str, file_name: str):
            Uploads or updates a DataFrame as a CSV file to an S3 bucket.

        download_files_per_year(link: BeautifulSoup, bucket_name: str = None):
            Downloads all files for a specific year and optionally uploads them to an S3 bucket.

        get_files(bucket_name: str = None):
            Downloads all files from all years and optionally uploads them to an S3 bucket.

        display_files_tracker(bucket_name: str) -> pd.DataFrame:
            Displays the DataFrame contained in the files_tracker.csv file from the S3 bucket.
            """
    
    def __init__(self, s3: boto3.resource, logger: logging.Logger) -> None:
        """
        Initializes the DataCollector class with the provided S3 resource and logger.

        Args:
            s3 (boto3.resource): An S3 resource object to interact with AWS S3.
            logger (logging.Logger): Logger instance for logging messages.
            """
        self.url_base = 'https://www.dane.gov.co'
        self.url = 'https://www.dane.gov.co/index.php/estadisticas-por-tema/agropecuario/sistema-de-informacion-de-precios-sipsa/mayoristas-boletin-semanal-1'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        self.s3 = s3
        self.files_tracker_name = 'files_tracker.csv'
        self.logfile_name = 'logfile'
        self.logger = logger

    def all_years_links(self) -> List[BeautifulSoup]:
        """
        Retrieves the set of year links available on the DANE webpage.

        Returns:
            List[BeautifulSoup]: A list of BeautifulSoup objects representing the links for each year.
        """
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch URL {self.url}: {e}")
            return []

        soup = BeautifulSoup(response.content, "html.parser")
        link_years = soup.find_all(lambda tag: tag.name == 'a' and re.match(r'^\d+$', tag.get_text().strip()))
        return link_years

    def links_per_year(self, link: BeautifulSoup) -> List[BeautifulSoup]:
        """
        Retrieves all report links for a specific year.

        Args:
            link (BeautifulSoup): The BeautifulSoup object containing the link to the year page.

        Returns:
            List[BeautifulSoup]: A list of BeautifulSoup objects representing the report links for the specified year.
        """
        try:
            r = requests.get(self.url_base + link['href'], headers=self.headers)
            r.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch URL {self.url_base + link['href']}: {e}")
            return []

        self.logger.info(f"Working on {link['href'][-4:]} files")
        soup_year = BeautifulSoup(r.content, "html.parser")
        one_year_links = [item for item in soup_year.find_all(target='_blank') if 'Anexo' in item.text]
        return one_year_links

    def check_file_exists_in_s3(self, bucket_name: str, file_name: str) -> bool:
        """
        Checks if a specific file already exists in the S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            file_name (str): The name of the file to check.

        Returns:
            bool: True if the file exists in the S3 bucket, False otherwise.
        """
        try:
            self.s3.Object(bucket_name, file_name).load()
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                self.logger.error(f"ClientError when checking {file_name} in bucket {bucket_name}: {e}")
                raise

    def load_files_tracker(self, bucket_name: str) -> pd.DataFrame:
        """
        Loads the files_tracker.csv from S3 or creates a new DataFrame if it does not exist.

        Args:
            bucket_name (str): The name of the S3 bucket containing the files_tracker.csv.

        Returns:
            pd.DataFrame: A DataFrame containing the file tracking information.
        """
        try:
            obj = self.s3.Object(bucket_name, self.files_tracker_name)
            response = obj.get()
            tracker_df = pd.read_csv(BytesIO(response['Body'].read()))
            self.logger.info("Loaded existing files tracker from S3.")
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                tracker_df = pd.DataFrame(columns=['file', 'link', 'date_added'])
                self.logger.info("No existing files tracker found in S3. Creating a new one.")
            else:
                self.logger.error(f"ClientError when accessing {self.files_tracker_name}: {e}")
                raise
        return tracker_df

    def update_files_tracker(self, df: pd.DataFrame, bucket_name: str):
        """
        Updates the files_tracker.csv in S3 with new file information.

        Args:
            df (pd.DataFrame): The DataFrame containing file tracking information to update.
            bucket_name (str): The name of the S3 bucket where the files_tracker.csv is stored.
        """
        buffer = BytesIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        try:
            self.s3.Bucket(bucket_name).put_object(Body=buffer, Key=self.files_tracker_name)
#             self.logger.info("Files tracker updated successfully in S3.")
        except ClientError as e:
            self.logger.error(f"Failed to update files tracker in S3 bucket {bucket_name}: {e}")
            raise

    def upload_or_update_dataframe_to_s3(self, df: pd.DataFrame, bucket_name: str, file_name: str):
        """
        Uploads or updates a DataFrame as a CSV file to an S3 bucket.

        Args:
            df (pd.DataFrame): The DataFrame to be uploaded.
            bucket_name (str): The name of the S3 bucket to upload to.
            file_name (str): The name of the file to be uploaded.
        """
        buffer = BytesIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        try:
            self.s3.Bucket(bucket_name).upload_fileobj(buffer, file_name, ExtraArgs={'ContentType': 'text/csv'})
            self.logger.info(f"DataFrame {file_name} uploaded successfully to S3 bucket {bucket_name}.")
        except ClientError as e:
            self.logger.error(f"Failed to upload DataFrame {file_name} to S3 bucket {bucket_name}: {e}")
            raise

    def download_files_per_year(self, link: BeautifulSoup, bucket_name: str = None):
        """
        Downloads all files for a specific year and optionally uploads them to an S3 bucket.

        Args:
            link (BeautifulSoup): The BeautifulSoup object representing the year link.
            bucket_name (str, optional): The name of the S3 bucket to upload the files to. Defaults to None.
        """
        links_per_year = self.links_per_year(link)
        n = len(links_per_year)

        tracker_df = self.load_files_tracker(bucket_name) if bucket_name else pd.DataFrame(columns=['file', 'link', 'date_added'])

        new_files_count = 0

        with tqdm(total=n, desc=f"Processing {link['href'][-4:]} files", unit='file') as pbar:
            for i, file in enumerate(links_per_year):
                file_name = f'week_{n - i}_{file["href"].split("/")[-1]}'
                file_link = self.url_base + file['href']

                if bucket_name and file_name in tracker_df['file'].values:
                    pbar.update(1)
                    continue

                try:
                    with requests.get(file_link, headers=self.headers, stream=True) as result:
                        result.raise_for_status()

                        if bucket_name:
                            destination_key = f'reports/{link.text.strip()}/{file_name}'
                            self.s3.Bucket(bucket_name).upload_fileobj(result.raw, destination_key)

                            new_entry = pd.DataFrame({
                                'file': [file_name],
                                'link': [file_link],
                                'date_added': [datetime.datetime.today().strftime('%Y-%m-%d')]
                            })
                            tracker_df = pd.concat([tracker_df, new_entry], ignore_index=True)
                            new_files_count += 1

                except requests.RequestException as e:
                    self.logger.error(f"Failed to download file from {file_link}: {e}")
                    continue
                except ClientError as e:
                    self.logger.error(f"Failed to upload file {file_name} to S3 bucket {bucket_name}: {e}")
                    continue
                finally:
                    pbar.update(1)

        if bucket_name:
            self.update_files_tracker(tracker_df, bucket_name)
            self.logger.info(f"Year {link['href'][-4:]} processed: {new_files_count} new files uploaded to S3 bucket {bucket_name}.")

    def get_files(self, bucket_name: str = None):
        """
        Download all files from all years and optionally upload them to an S3 bucket.
        """
        all_years_links = self.all_years_links()
        for link in all_years_links:
            self.download_files_per_year(link, bucket_name)

        # Upload log file to S3 after processing
        if bucket_name:
            try:
                self.logger.info(f"Log file {self.logfile_name} uploaded successfully to S3 bucket {bucket_name}.")
            except ClientError as e:
                self.logger.error(f"Failed to upload log file to S3 bucket {bucket_name}: {e}")

    def display_files_tracker(self, bucket_name: str) -> pd.DataFrame:
        """
        Display the DataFrame contained in the files_tracker.csv file from the S3 bucket.
        """
        tracker_df = self.load_files_tracker(bucket_name)
        return tracker_df
