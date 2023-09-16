from pathlib import Path
from tqdm import tqdm
import time
import pandas as pd
import os
import numpy as np
import requests
from bs4 import BeautifulSoup
import openpyxl
import warnings
import boto3
from typing import List

from matplotlib import pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")



def first_format_wrangling(path_list: List[str],
                           s3: boto3.resource,
                           bucket_name: str = 'sipsatracker', 
                           aws_flag:bool= True):
    # Creating target dataframe
    year_file = pd.DataFrame()

    # Creating food categories 
    categories_dict = {1: 'verduras_hortalizas',
        2: 'frutas_frescas',
        3: 'tuberculos_raices_platanos',
        4: 'granos_cereales',
        5: 'huevos_lacteos',
        6: 'carnes',
        7: 'pescados',
        8: 'productos_procesados'}

    # Iterating over list of paths 

    bucket = s3.Bucket(bucket_name)

    for file_path in tqdm(path_list):
        
        # Capturing off cases
        try: 
            if aws_flag: 
                # Import data
                obj = bucket.Object(file_path)
                obj.download_file(Path.cwd()/Path(file_path).name)
                dataframe = pd.read_excel(Path.cwd()/Path(file_path).name)
            else:
                with open(file_path, 'rb') as f: 
                    dataframe = pd.read_excel(f, header = None)

            # Keeping only first five columns and renaming them
            dataframe = dataframe.iloc[:,0:5]
            dataframe.columns = ['ciudad','precio_minimo','precio_maximo','precio_medio', 'tendencia']
            dataframe['ciudad'] = dataframe['ciudad'].str.lower().str.replace('bogotá, d.c.', 'bogota')
            
            # rows where ciudad is non null
            dataframe = dataframe[~dataframe['ciudad'].isnull()]
            
            # This formatting would have eight food categories within the same spreadsheet divided only by a big title. 
            # Such title would include the word 'cuadro'. So, to separate categories, we look for blocks of data contained 
            # within two consecutive appareances of such words. 

            # Get row indexes where the word 'cuadro' is present
            index_cuadro = dataframe[dataframe['ciudad'].str.contains('cuadro')].index
            
            # Creating target dataframe for all data
            df_final= pd.DataFrame()

            # Itearting over food categories. 
            for i_categoria in range(len(index_cuadro)):
                
                # Capturing first seven categories
                if i_categoria < 7:
                    dataframe_categoria = dataframe[index_cuadro[i_categoria]+2:index_cuadro[i_categoria+1]]
                # Capturing last category
                else: 
                    dataframe_categoria = dataframe[index_cuadro[i_categoria]+2:]

                # Within each category block, add category name
                dataframe_categoria['categoria'] = categories_dict[i_categoria+1]

                # within each category block, there are several products. In the whole reporting, products are very likely to contain 
                # several rows (same food item in different locations). What identifies such product blocks is the fact that the precio_minimo
                # column will be blank. So the product data would be contain within two consecutive occurrencies of blank prices. 
                index_producto = dataframe_categoria[dataframe_categoria['precio_minimo'].isnull()].index

                # creating target data frame for product category
                df_categoria_final = pd.DataFrame()

                # Iterating over products within food category
                for i_producto in range(len(index_producto)): 
                    
                    # Capturing the first product in the category 
                    if i_producto == 0:
                        dataframe_producto = dataframe_categoria.loc[index_producto[i_producto]-1:index_producto[i_producto+1]-1].reset_index(drop = True)
                    
                    # Capturing all intermediate products
                    elif i_producto < len(index_producto)-1: 
                        dataframe_producto = dataframe_categoria.loc[index_producto[i_producto]:index_producto[i_producto+1]-1].reset_index(drop = True)
                    
                    # Capturing last product within category 
                    else: 
                        dataframe_producto = dataframe_categoria.loc[index_producto[i_producto]:].reset_index(drop = True)
                    
                    # Adding product name column to each block of products
                    dataframe_producto['producto'] = dataframe_producto['ciudad'][0]

                    # Keeping only city name under the ciudad column
                    dataframe_producto['ciudad'] = dataframe_producto['ciudad'].str.replace(r'\s*\([^)]*\)', '', regex=True)
                    
                    # The name of the marketplaces is included on some of the city names. So we try to retrieve it
                    try: 
                        dataframe_producto['mercado'] = dataframe_producto['ciudad'].str.split(',').str[1].str.strip()
                    except:
                        dataframe_producto['mercado'] = np.nan
                    
                    # Getting a clean version of city name
                    try: 
                        dataframe_producto['ciudad'] = dataframe_producto['ciudad'].str.split(',').str[0].str.strip()
                    except: 
                        None
                    # Dropping first row
                    dataframe_producto = dataframe_producto.drop(0)

                    # Putting together all data for products within food category 
                    df_categoria_final = pd.concat([df_categoria_final, dataframe_producto], ignore_index = True)

                # Putting together all data 
                df_final = pd.concat([df_final,df_categoria_final], ignore_index = True)

            # Once data per file is complete, time stamps are added: year and week number
            df_final['semana_no'] = int(file_path.name.split('_')[1])#file_path.stem[5:7]
            df_final['anho'] = file_path.stem[-4:]
            
            # Adding data file to main target dataframe
            year_file = pd.concat([year_file,df_final], ignore_index = True)
            year_file = year_file[['anho','semana_no','categoria','producto','ciudad','precio_minimo','precio_maximo','precio_medio','tendencia']]
        
        # Printing what went wrong
        except Exception as e: 
            print(f'[Info] There is a problem in {file_path}: \n {e}')
    
    return year_file;


def second_format_wrangling(path_list):
    
    # Creating target dataframe
    year_file2 = pd.DataFrame()

    # Creating food categories 
    categories_dict = {1: 'verduras_hortalizas',
        2: 'frutas_frescas',
        3: 'tuberculos_raices_platanos',
        4: 'granos_cereales',
        5: 'huevos_lacteos',
        6: 'carnes',
        7: 'pescados',
        8: 'productos_procesados'}

    # Iteration over list of paths
    for file_path in tqdm(path_list): 

        # Capturing off cases
        try: 
            # Importing file and extracting book names
            xl = pd.ExcelFile(file_path)
            ref_dict = {i: xl.sheet_names[i] for i in range(len(xl.sheet_names))}
            
            # Creating target dataframe for file data
            dataframe_file = pd.DataFrame()

            # Iterating over tabs within file
            for index in range(1,9):
                
                # Importing file
                with open(file_path, 'rb') as f: 
                    dataframe = pd.read_excel(f, sheet_name = ref_dict[index])

                # within this second type of formatting, there is two groups based on a subtle
                # detail: In one, data would start at row 10, in the other, data would start at row 11
                if pd.isnull(dataframe.iloc[9,0]):
                    dataframe = dataframe.iloc[10:,:6]
                else: 
                    dataframe = dataframe.iloc[9:,:6]

                # Setting column names
                dataframe.columns = ['producto', 'ciudad','precio_minimo','precio_maximo','precio_medio', 'tendencia']
                # keeping rows non null for ciudad column only
                dataframe = dataframe[~dataframe['ciudad'].isnull()]

                # Adding categoria and ciudad info 
                dataframe['categoria'] = categories_dict[index]
                dataframe['ciudad'] = dataframe['ciudad'].str.lower().str.replace('bogotá, d.c.', 'bogota')
                dataframe['ciudad'] = dataframe['ciudad'].str.replace(r'\s*\([^)]*\)', '', regex=True)
                                
                # The name of the marketplaces is included on some of the city names. So we try to retrieve it
                try: 
                    dataframe['mercado'] = dataframe['ciudad'].str.split(',').str[1].str.strip()
                except:
                    dataframe['mercado'] = np.nan
                                
                # Getting a clean version of city name
                try: 
                    dataframe['ciudad'] = dataframe['ciudad'].str.split(',').str[0].str.strip()
                except: 
                    pass
                
                # Once data per file is complete, time stamps are added: year and week number
                dataframe['semana_no'] = int(file_path.name.split('_')[1])#file_path.stem[5:7]
                dataframe['anho'] = file_path.stem[-4:]

                 # Adding data file to main target dataframe
                dataframe = dataframe[['anho','semana_no','categoria','producto','ciudad','precio_minimo','precio_maximo','precio_medio','tendencia']]
                dataframe_file = pd.concat([dataframe_file, dataframe], ignore_index = True)

            # Adding file data to target dataframe 
            year_file2 = pd.concat([year_file2, dataframe_file], ignore_index = True)
        
        # Printing what went wrong
        except Exception as e: 
            print(f'[Info] There is a problem in {file_path}: \n {e}')

    return year_file2;

def data_preparation(dataframe):
    city_to_region = {
    'barranquilla': 'caribe',
    'cartagena': 'caribe',
    'santa marta': 'caribe',
    'valledupar': 'caribe',
    'montería': 'caribe',
    'sincelejo': 'caribe',
    'riohacha': 'caribe',
    'ciénaga': 'caribe',
    'magangué': 'caribe',
    'maicao': 'caribe',
    'turbo': 'caribe',
    'lorica': 'caribe',
    'sahagún': 'caribe',
    'aracataca': 'caribe',
    'el banco': 'caribe',
    'girardot': 'andina',
    'ibagué': 'andina',
    'neiva': 'andina',
    'pereira': 'andina',
    'manizales': 'andina',
    'armenia': 'andina',
    'cali': 'pacífico',
    'buenaventura': 'pacífico',
    'tuluá': 'pacífico',
    'palmira': 'pacífico',
    'pasto': 'pacífico',
    'popayán': 'pacífico',
    'tumaco': 'pacífico',
    'yumbo': 'pacífico',
    'quibdó': 'pacífico',
    'bogotá': 'andina',
    'medellín': 'andina',
    'bucaramanga': 'andina',
    'cúcuta': 'andina',
    'villavicencio': 'orinoquía',
    'yopal': 'orinoquía',
    'arauca': 'orinoquía',
    'florencia': 'amazonía',
    'mocoa': 'amazonía',
    'leticia': 'amazonía',
    'puerto carreño': 'orinoquía',
    'mitú': 'amazonía',
    'inírida': 'amazonía',
    'bogota': 'andina',
    'duitama': 'andina',
    'ipiales': 'pacífico',
    'pamplona': 'andina',
    'sogamoso': 'andina',
    'tunja': 'andina',
    'cartago': 'pacífico',
    'rionegro': 'andina',
    'san gil': 'andina',
    'socorro': 'andina',
    'chiquinquirá': 'andina',
    'el santuario': 'andina',
    'marinilla': 'andina',
    'cajamarca': 'andina',
    'carmen de viboral': 'andina',
    'la ceja': 'andina',
    'san vicente': 'andina',
    'sonsón': 'andina',
    'peñol': 'andina',
    'santa bárbara': 'andina',
    'yarumal': 'andina',
    'la virginia': 'andina',
    'la unión': 'andina',
    'la parada': 'andina',
    'la dorada': 'andina',
    'charalá': 'andina',
    'güepsa': 'andina',
    'moniquirá': 'andina',
    'puente nacional': 'andina',
    'santana': 'andina',
    'vélez': 'andina',
    'caparrapí': 'andina',
    'nocaima': 'andina',
    'villeta': 'andina',
    'honda': 'andina',
    'ubaté': 'andina',
    'cartagena frigorífico candelaria': 'caribe',
    'san marcos': 'caribe',
    'alvarado': 'andina',
    'espinal': 'andina',
    'lérida': 'andina',
    'purificación': 'andina',
    'venadillo': 'andina',
    'cereté': 'caribe',
    'san gilpanela': 'andina',
    'yolombó': 'andina',
    'malambo': 'caribe',
    'el carmen de viboral': 'andina',
    'túquerres': 'pacífico',
    'san andrés de tumaco': 'pacífico',
    'ancuyá': 'andina',
    'consacá': 'andina',
    'sandoná': 'andina',
    'ancuya': 'andina',
    'tibasosa': 'andina',
    'san sebastián de mariquita': 'andina',
    }
    
    dataframe = dataframe[(~dataframe['precio_minimo'].isnull()) &
                        (~dataframe['precio_maximo'].isnull()) & 
                        (~dataframe['precio_medio'].isnull()) & 
                        (dataframe['precio_medio']!='b')]

    dataframe['precio_minimo'] = dataframe['precio_minimo'].astype(int)
    dataframe['precio_maximo'] = dataframe['precio_maximo'].astype(int)
    dataframe['precio_medio'] = dataframe['precio_medio'].astype(int)

    dataframe['producto'] = dataframe['producto'].str.lower()
    dataframe = dataframe[~dataframe['producto'].isnull()]

    dataframe['region'] = dataframe['ciudad'].map(city_to_region)
    # Saving resulting file
    dataframe.to_csv(Path.cwd()/'reports'/'full_report.csv', sep = ',', index = False)
    
    return dataframe;
    

