from datetime import datetime
import pandas as pd
import boto3

# Imports credentials
def update_sipsa_file(s3: boto3.resource, 
					  dataframe: pd.DataFrame, 
					  bucket_name:str = 'sipsatracker', 
					  file_name:str = 'full_report'): 
	"""
	This function updates (delete and upload) the sipsa file hosted on the S3 bucket (AWS). 

	Args:
		s3 (boto3.resource): S3 resource created.
		dataframe (pd.DataFrame): datafarme containing data to be uploaded.
		bucket_name (str, optional): Bucket name of interest. Defaults to 'sipsatracker'.
		file_name (str, optional): file to be give to uploaded file. Defaults to 'full_report'.

	Returns:
		None

	Example usage: 
		update_sipsa_file(	s3 = s3,
							dataframe = dataframe,
							bucket_name = 'sipsatracker', 
							file_name = 'full_report')
	"""
	# coding entry data
	csv_buffer = dataframe.to_csv(index=False).encode('utf-8')

	# Creating time stamp
	# today = datetime.today().strftime('%Y-%m-%d')

	print(f'[info] Connection created successfully')
	# upload file
	s3_path =  f'{file_name}.csv'

	# Get the S3 bucket
	# bucket = s3.Bucket(bucket_name)
	# print(f'[info] Resource created successfully. S3 bucket: {bucket_name}.')

	# # List all objects in the bucket and retrieve their keys (object names)
	# object_names = [obj.key for obj in bucket.objects.all()]
	
	# # Delete previous file
	# s3.Object(bucket_name, object_names[0]).delete()
	# print(f'[info] {object_names[0]} deleted successfully.')

	# upload updated file 
	s3.Object(bucket_name,s3_path).put(Body=csv_buffer)
	print(f'[info] {s3_path} uploaded successfully.')

	return None;



# Function to read CSV file from S3 bucket
def read_csv_from_s3(s3: boto3.resource, bucket_name:str, file_name:str):
# Get the S3 bucket and object
    bucket = s3.Bucket(bucket_name)
    obj = bucket.Object(file_name)

    # Read CSV data from S3 object
    df = pd.read_csv(obj.get()['Body'])
    df = df[~((df['anho']==2023)&(df['semana_no']==53))]
    return df