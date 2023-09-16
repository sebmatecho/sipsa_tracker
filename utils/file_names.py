import boto3
from pathlib import Path

def first_format_paths():

    # Overall files are consistent with formating, but there are two major types of formats. First of them would apply up to week 19 of 2018. 
    first_format = ['2012','2013','2014','2015','2016','2017','2018']
    final_files_paths = []

    # Putting together overall list of files
    for year in first_format: 
        
        # Collecting paths from each year
        root_path = Path.cwd()/'reports'/year
        
        # collecting both xls and xlsx files
        xls_files = list(root_path.glob('*.xls'))
        xlsx_files = list(root_path.glob('*.xlsx'))
        all_files = xls_files + xlsx_files
        
        # This formatting would only apply prior to the 20th week of 2018
        if year == '2018':
            all_files = [path for path in all_files if int(path.stem.split('_')[1]) <= 19]
        
        # Putting together the list of paths
        final_files_paths.extend(all_files)

    return final_files_paths



def second_format_paths():
    # Overall files are consistent with formating, but there are two major types of formats. First of them would apply up to week 19 of 2018. 
    first_format = ['2018', '2019', '2020', '2021', '2022', '2023']
    final_files_paths = []

    # Putting together overall list of files
    for year in first_format: 
        
        # Collecting paths from each year
        root_path = Path.cwd()/'reports'/year
        
        # collecting both xls and xlsx files
        xls_files = list(root_path.glob('*.xls'))
        xlsx_files = list(root_path.glob('*.xlsx'))
        all_files = xls_files + xlsx_files
        
        # This formatting would only apply after the 20th week of 2018
        if year == '2018':
            all_files = [path for path in all_files if int(path.stem.split('_')[1]) > 19]
        
        # Putting together the list of paths
        final_files_paths.extend(all_files)
    
    return final_files_paths;

def first_format_paths_aws(s3: boto3.resource, 
                           bucket_name: str = 'sipsatracker'):
	"""
	This function collects data files keys from AWS S3. 

	SIPSA has two major formats for how data is presented. This required the development
	of data flow for each format. This function correspond to the first of them where data 
	would be file with a single sheet. 

	Args:
		s3 (boto3.resource): S3 resource connection 
		bucket_name (str, optional): Bucket name. Defaults to 'sipsatracker'.

	Returns:
		list: list of paths to files for the file data wrangling process
	"""
	# Create connection with bucket
	bucket = s3.Bucket(bucket_name)

	# Creating list of all objects available in such bucket
	object_names = [obj.key for obj in bucket.objects.all()]

	# this batch of files are prior to the 20th week of 2018
	first_format = ['2012','2013','2014','2015','2016','2017','2018']
	final_files_paths = []

	# Checking files
	for path in object_names:
		# in case the file would not have a part 1
		try: 
			# for years prior to 2018, take everything
			if str(Path(path).parts[1]) in first_format[:-1]:
				final_files_paths.append(path)
			# for 2018, take everything under week 19
			if (str(Path(path).parts[1]) == first_format[-1]) and (int(Path(path).stem.split('_')[1])<= 19):
				final_files_paths.append(path)
		except:
			None

	return final_files_paths