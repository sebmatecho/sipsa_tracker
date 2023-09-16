
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from tqdm import tqdm
import time
import datetime
from typing import List
import boto3

from utils.web_scrapper import DataCollector

class FileNameBuilder(DataCollector): 
	def __init__(self, s3: boto3.resource): 
		super().__init__(s3)

	def first_format_paths(self, bucket_name:str):
		# Create connection with bucket
		bucket = self.s3.Bucket(bucket_name)

		# Creating list of all objects available in such bucket
		object_names = [obj.key for obj in bucket.objects.all()]

		# this batch of files are prior to the 20th week of 2018
		first_format = ['2012','2013','2014','2015','2016','2017','2018']
		final_files_paths_first = []

		# Checking files
		for path in object_names:
			# in case the file would not have a part 1
			try: 
				# for years prior to 2018, take everything
				if str(Path(path).parts[1]) in first_format[:-1]:
					final_files_paths_first.append(path)
				# for 2018, take everything under week 19
				if (str(Path(path).parts[1]) == first_format[-1]) and (int(Path(path).stem.split('_')[1])<= 19):
					final_files_paths_first.append(path)
			except:
				None

		return final_files_paths_first
	
	def second_format_paths(self, bucket_name:str):

		# Create connection with bucket
		bucket = self.s3.Bucket(bucket_name)

		# Creating list of all objects available in such bucket
		object_names = [obj.key for obj in bucket.objects.all()]
		# Overall files are consistent with formating, but there are two major types of formats. First of them would apply up to week 19 of 2018. 
		second_format = ['2018', '2019', '2020', '2021', '2022', '2023']
		final_files_paths_second = []
		# Putting together overall list of files
		for path in object_names:
			
			try: 
				# for years after 2018, take everything
				if str(Path(path).parts[1]) in second_format[1:]:
					final_files_paths_second.append(path)
				# for 2018, take everything after week 19
				if (str(Path(path).parts[1]) == second_format[0]) and (int(Path(path).stem.split('_')[1])> 19):
					final_files_paths_second.append(path)
			except:
				None
		
		return final_files_paths_second;
