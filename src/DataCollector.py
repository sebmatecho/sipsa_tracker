
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
    def __init__(self, s3: boto3.resource, logger: logging.Logger) -> None:
        """
        Initialize the DataCollector with S3 resource and configuration parameters.
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
        Get the set of year links available on the DANE webpage.
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
        Get all report links for a specific year.
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
        Check if a file already exists in the S3 bucket.
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
        Load the files_tracker.csv from S3 or create a new DataFrame if it does not exist.
        """
        try:
            obj = self.s3.Object(bucket_name, self.files_tracker_name)
            response = obj.get()
            tracker_df = pd.read_csv(BytesIO(response['Body'].read()))
            self.logger.info("Loaded existing files tracker from S3.")
        except self.s3.meta.client.exceptions.NoSuchKey:
            # If files_tracker.csv does not exist, initialize an empty DataFrame
            tracker_df = pd.DataFrame(columns=['file', 'link', 'date_added'])
            self.logger.info("No existing files tracker found in S3. Creating a new one.")
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
        Update the files_tracker.csv in S3.
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
        Upload or update a DataFrame as a CSV file to an S3 bucket.
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
        Download all files for a specific year and optionally upload them directly to an S3 bucket.
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
