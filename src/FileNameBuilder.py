
from typing import List
import boto3
import logging
from pathlib import Path

class FileNameBuilder:
    def __init__(self, 
                 s3: boto3.resource, 
                 logger:logging.Logger):
        """
        Initialize FileNameBuilder with S3 resource.
        """
        self.s3 = s3
        self.logger = logger

    def first_format_paths(self, bucket_name: str) -> List[str]:
        """
        Get the paths of files in the S3 bucket that match the first format criteria.
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
        Get the paths of files in the S3 bucket that match the second format criteria.
        """
        self.logger.info(f"Fetching second format paths from bucket: {bucket_name}")
        bucket = self.s3.Bucket(bucket_name)
        object_names = [obj.key for obj in bucket.objects.all() if obj.key.endswith(('.xls', '.xlsx'))]

        second_format_years = {'2018', '2019', '2020', '2021', '2022', '2023', '2024'}
        final_files_paths_second = []

        for path in object_names:
            try:
                parts = Path(path).parts
                if len(parts) < 2:
                    continue
                year = parts[1]
                week = int(Path(path).stem.split('_')[1])

                if year in second_format_years:
                    if year == '2018' and week <= 19:
                        continue
                    final_files_paths_second.append(path)
                    self.logger.debug(f"File added to second format: {path}")

            except (IndexError, ValueError) as e:
                self.logger.warning(f"Error processing path {path}: {e}")

        self.logger.info(f"Found {len(final_files_paths_second)} files for the second format.")
        return final_files_paths_second
