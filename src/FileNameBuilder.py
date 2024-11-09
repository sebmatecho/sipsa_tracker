
from typing import List
import boto3
import logging
from pathlib import Path

class FileNameBuilder:
    """
    A class used to build file paths for data files stored in an S3 bucket based on specific format criteria.

    This class interacts with an S3 bucket to identify and categorize files according to predefined format
    specifications. It uses criteria such as year and file type to segregate files into 'first format' and 
    'second format' categories. This comes from DANE changing format of the report throughout the years. 
    
    DANE first format refers to a single tab file with information displayed with several titles through it
    DANE second format refers to a file containing several tabs (per food class)

    Attributes:
        s3 (boto3.resource): An S3 resource object to interact with AWS S3.
        logger (logging.Logger): Logger instance for logging messages.

    Methods:
        __init__(s3: boto3.resource, logger: logging.Logger):
            Initializes the FileNameBuilder class with the provided S3 resource and logger.

        first_format_paths(bucket_name: str) -> List[str]:
            Retrieves file paths from the S3 bucket that match the first format criteria.

        second_format_paths(bucket_name: str) -> List[str]:
            Retrieves file paths from the S3 bucket that match the second format criteria.
    """
    def __init__(self, 
                 s3: boto3.resource, 
                 logger:logging.Logger):
        """
        Initializes the FileNameBuilder class with the provided S3 resource and logger.

        Args:
            s3 (boto3.resource): An S3 resource object to interact with AWS S3.
            logger (logging.Logger): Logger instance for logging messages.
        """
        self.s3 = s3
        self.logger = logger

    def first_format_paths(self, bucket_name: str) -> List[str]:
        """
        Retrieves file paths from the S3 bucket that match the first format criteria.

        The first format includes files from the years 2012 to 2017, and files from the year 2018 up to 
        and including week 19. It filters files based on their extensions (.xls, .xlsx).

        Args:
            bucket_name (str): The name of the S3 bucket containing the files.

        Returns:
            List[str]: A list of file paths matching the first format criteria.
        """
        self.logger.info(f"Fetching first format paths from bucket: {bucket_name}")
        bucket = self.s3.Bucket(bucket_name)
        object_names = [obj.key for obj in bucket.objects.all() if obj.key.endswith(('.xls', '.xlsx'))]

        first_format_years = {'2012', '2013', '2014', '2015', '2016', '2017'}
        final_files_paths_first = []

        for path in object_names:
            try:
                parts = Path(path).parts
                if len(parts) < 2:
                    continue
                year = parts[1]
                week = int(Path(path).stem.split('_')[1])

                # Check for files in years prior to 2018
                if year in first_format_years:
                    final_files_paths_first.append(path)
                    self.logger.debug(f"File added to first format: {path}")
                elif year == '2018' and week <= 19:
                    final_files_paths_first.append(path)
                    self.logger.debug(f"File added to first format: {path}")

            except (IndexError, ValueError) as e:
                self.logger.warning(f"Error processing path {path}: {e}")

        self.logger.info(f"Found {len(final_files_paths_first)} files for the first format.")
        return final_files_paths_first

    def second_format_paths(self, bucket_name: str) -> List[str]:
        """
        Retrieves file paths from the S3 bucket that match the second format criteria.

        The second format includes files from the years 2018 (after week 19) to 2024. It filters files based 
        on their extensions (.xls, .xlsx).

        Args:
            bucket_name (str): The name of the S3 bucket containing the files.

        Returns:
            List[str]: A list of file paths matching the second format criteria.
        """
        self.logger.info(f"Fetching second format paths from bucket: {bucket_name}")
        bucket = self.s3.Bucket(bucket_name)
        object_names = [obj.key for obj in bucket.objects.all() if obj.key.endswith(('.xls', '.xlsx'))]

        second_format_years = {'2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025'}
        final_files_paths_second = []

        for path in object_names:
            try:
                parts = Path(path).parts
                if len(parts) < 2:
                    continue
                year = parts[1]
                week = int(Path(path).stem.split('_')[1])

                if year in second_format_years:
                    ### week 19 of 2018. Major format change!
                    if year == '2018' and week <= 19:
                        continue
                    final_files_paths_second.append(path)
                    self.logger.debug(f"File added to second format: {path}")

            except (IndexError, ValueError) as e:
                self.logger.warning(f"Error processing path {path}: {e}")

        self.logger.info(f"Found {len(final_files_paths_second)} files for the second format.")
        return final_files_paths_second
