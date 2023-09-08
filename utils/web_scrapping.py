import requests
from bs4 import BeautifulSoup
from pathlib import Path
from tqdm import tqdm
import time
import datetime

def data_gathering():
    """
    This function retrieves xlsx and xls files from DANE's webpage relate to the SIPSA project. 
    
    If the files already exists, it does nothing. If they are not, it donwloads them 

    Returns:
       Creates the folders per year to allocate downloaded files. 
    """
    url_base = 'https://www.dane.gov.co'
    url = 'https://www.dane.gov.co/index.php/estadisticas-por-tema/agropecuario/sistema-de-informacion-de-precios-sipsa/mayoristas-boletin-semanal-1'

    headers = {
       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
       }
    response = requests.get(url, headers = headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        # Getting link for each year
        
        link_years = soup.find_all(lambda tag: tag.name == 'a' and any(substring in tag.get('title', '').lower() for substring in ['boletín mayorista semanal','boletin mayorista semanal', 'mayoristas boletín semanal']))

        # within each year
        for link in link_years:
        
            # Request for reports available in such year
            r = requests.get(url_base + link['href'], headers = headers)
            soup_year = BeautifulSoup(r.content, "html.parser")
        
            # Create links for each report within the given year and creating reference lenght
            target_links = [item for item in soup_year.find_all(target = '_blank') if 'Anexo' in item.text]       
            n = len(target_links)

            # Creating folder name per year  
            if link.text.strip() == 'Mayoristas boletín semanal':
               REPORTS_PATH = Path.cwd()/'reports'/str(datetime.datetime.today().year)
            else: 
               REPORTS_PATH = Path.cwd()/'reports'/link.text.strip()

            print(f' Working on {REPORTS_PATH.name} data')

            # Create folders per year
            if REPORTS_PATH.exists():
               pass
            else: 
               REPORTS_PATH.mkdir(parents= True, exist_ok=True)

            # For each link, create file in local and fill it with data 
            for i, file in tqdm(enumerate(target_links)):
                # print(file)
                # name output file
                file_name = 'week_'+str(n-i)+'_'+file['href'].split('/')[-1]
                file_path = REPORTS_PATH/file_name

                # Checking if file already exists. If it does, do nothing. Otherwise, download it. 
                if file_path.exists():
                   pass
            
                else:
                # request information
                    try: 
                        result = requests.get(url_base+file['href'], headers = headers)
                    except:
                        result = requests.get(file['href'], headers = headers)
          
                    # export data to local path
                    with open(file_path, 'wb') as f: 
                        f.write(result.content)
            
                    # Wait one second before next iteration 
                    time.sleep(1)           
    else: 
        print(f'[Fail] Status error:{response.status_code}')
  
    return None;