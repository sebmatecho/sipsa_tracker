
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