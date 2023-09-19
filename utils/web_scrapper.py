import requests
from bs4 import BeautifulSoup
from pathlib import Path
from tqdm import tqdm
import time
import datetime
from typing import List
import boto3

class DataCollector():
    def __init__(self, s3: boto3.resource)-> None:
        self.url_base = 'https://www.dane.gov.co'
        self.url = 'https://www.dane.gov.co/index.php/estadisticas-por-tema/agropecuario/sistema-de-informacion-de-precios-sipsa/mayoristas-boletin-semanal-1'
        self.headers = {
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
           }
        self.s3 = s3
     
    def all_years_links(self) -> List[str]:
        """
        this method gets the set of links, per year, available
        """
        response = requests.get(self.url, headers = self.headers)
        soup = BeautifulSoup(response.content, "html.parser")
        link_years = soup.find_all(lambda tag: tag.name == 'a' and any(substring in tag.get('title', '').lower() for substring in ['boletín mayorista semanal','boletin mayorista semanal', 'mayoristas boletín semanal']))
        return link_years
   
   
    def links_per_year(self, link: str) -> List[str]:
        """
        This method downloads the file from each individual link
        """
        # Request for reports available in such year
        r = requests.get(self.url_base + link['href'], headers = self.headers)
        soup_year = BeautifulSoup(r.content, "html.parser")
       
        # Create links for each report within the given year and creating reference lenght
        one_year_links = [item for item in soup_year.find_all(target = '_blank') if 'Anexo' in item.text]      
        return one_year_links

    def creates_folder(self, link:str):
        """
        
        """
        # Creating folder name per year  
        if link.text.strip() == 'Mayoristas boletín semanal':
            REPORTS_PATH = Path.cwd()/'reports'/str(datetime.datetime.today().year)
        else:
            REPORTS_PATH = Path.cwd()/'reports'/link.text.strip()

         # Create folders per year
        if not REPORTS_PATH.exists():
            REPORTS_PATH.mkdir(parents= True, exist_ok=True)
    
        return REPORTS_PATH   

    def download_files_per_year(self, link,  bucket_name:str = None):

        REPORTS_PATH = self.creates_folder(link)
        
        # For each link, create file in local and fill it with data        
        links_per_year = self.links_per_year(link)
        n = len(links_per_year)
        
        for i, file in tqdm(enumerate(links_per_year)):
            # name output file
            file_name = 'week_'+str(n-i)+'_'+file['href'].split('/')[-1]
            file_path = REPORTS_PATH/file_name

            # Checking if file already exists. If it does, do nothing. Otherwise, download it.
            if not file_path.exists():

            # request information
                try:
                    result = requests.get(self.url_base+file['href'], headers = self.headers)
                except:
                    result = requests.get(file['href'], headers = self.headers)

                # export data to local path
                with open(file_path, 'wb') as f:
                    f.write(result.content)     
                
                # if bucket name is provided, upload file
                if bucket_name is not None:
                    # upload to S3 bucket
                    destination_key  = f'reports/{REPORTS_PATH.name}/{file_name}'   
                    self.s3.Bucket(bucket_name).upload_file(file_path, destination_key)

    def get_files(self, bucket_name:str = None):
        all_years_links = self.all_years_links()
        for link in all_years_links:
                self.download_files_per_year(link, bucket_name)

