from datetime import datetime
import pandas as pd
import boto3

# Imports credentials
def update_sipsa_file(aws_access_key_id:str, 
                      aws_secret_access_key:str, 
					  dataframe: pd.DataFrame, 
					  bucket_name:str = 'sipsatracker', 
					  file_name:str = 'full_report'): 
	"""
	This function updates (delete and upload) the sipsa file hosted on the S3 bucket (AWS). 

	Args:
		aws_access_key_id (str): AWS credential user.
		aws_secret_access_key (str): AWS credential password.
		dataframe (pd.DataFrame): datafarme containing data to be uploaded.
		bucket_name (str, optional): Bucket name of interest. Defaults to 'sipsatracker'.
		file_name (str, optional): file to be give to uploaded file. Defaults to 'full_report'.

	Returns:
		None

	Example usage: 
		update_sipsa_file(	aws_access_key_id = aws_access_key_id, 
							aws_secret_access_key = aws_secret_access_key, 
							dataframe = dataframe,
							bucket_name = 'sipsatracker', 
							file_name = 'full_report')
	"""
	# coding entry data
	csv_buffer = dataframe.to_csv(index=False).encode('utf-8')

	# Creating time stamp
	today = datetime.today().strftime('%Y-%m-%d')

	# Creating boto3 session (access the S3 bucket)
	s3 = boto3.resource('s3',
						aws_access_key_id = aws_access_key_id, 
						aws_secret_access_key = aws_secret_access_key)

	print(f'[info] Connection created successfully')
	# upload file
	s3_path =  f'{file_name}_{today}.csv'

	# Get the S3 bucket
	bucket = s3.Bucket(bucket_name)
	print(f'[info] Resource created successfully. S3 bucket: {bucket_name}.')

	# List all objects in the bucket and retrieve their keys (object names)
	object_names = [obj.key for obj in bucket.objects.all()]
	
	# Delete previous file
	s3.Object(bucket_name, object_names[0]).delete()
	print(f'[info] {object_names[0]} deleted successfully.')

	# upload updated file 
	s3.Object(bucket_name,s3_path).put(Body=csv_buffer)
	print(f'[info] {s3_path} uploaded successfully.')

	return None;



# s3.Object(bucket_name, s3_path).download_file(Path.cwd())