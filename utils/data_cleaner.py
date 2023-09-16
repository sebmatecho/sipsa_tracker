import os
import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
import boto3
from io import BytesIO
import warnings
warnings.filterwarnings("ignore")
from utils.file_names_builder import FileNameBuilder


class DataWrangler(FileNameBuilder):
    def __init__(self, s3: boto3.resource):
        super().__init__(s3)
        self.categories_dict = {
            1: 'verduras_hortalizas',
            2: 'frutas_frescas',
            3: 'tuberculos_raices_platanos',
            4: 'granos_cereales',
            5: 'huevos_lacteos',
            6: 'carnes',
            7: 'pescados',
            8: 'productos_procesados'
        }

    def first_format_wrangling(self, bucket_name: str):
        first_format_files = self.first_format_paths(bucket_name)
        year_file = pd.DataFrame()
        
        print('[Info] Working on first batch of files')
        for file in tqdm(first_format_files):
        # for file in first_format_files:
            data = self.process_file(file, bucket_name)
            year_file = pd.concat([year_file, data], ignore_index=True)
            
        return year_file

    def process_file(self, 
                     file_path: str, 
                     bucket_name: str) -> pd.DataFrame:
        bucket = self.s3.Bucket(bucket_name)

        # Download file to local
        obj = bucket.Object(file_path)
        # local_file_path = Path.cwd() / Path(file_path).name
        # obj.download_file(local_file_path)

        # Read file into a DataFrame
        # dataframe = pd.read_excel(local_file_path)
        # Read the XLS file from S3
        xls_data = obj.get()['Body'].read()

        # Create a Pandas DataFrame from the XLS data
        dataframe = pd.read_excel(BytesIO(xls_data), engine='xlrd')

        # Delete the local file
        # os.remove(local_file_path)

        # Process the DataFrame
        dataframe = self.process_dataframe(dataframe, file_path)

        return dataframe

    def process_dataframe(self, 
                          dataframe: pd.DataFrame, 
                          file_path:str) -> pd.DataFrame:
        # Keep only the first five columns and rename them
        dataframe = dataframe.iloc[:, 0:5]
        dataframe.columns = ['ciudad', 'precio_minimo', 'precio_maximo', 'precio_medio', 'tendencia']
        dataframe['ciudad'] = dataframe['ciudad'].str.lower().str.replace('bogotá, d.c.', 'bogota')

        # Remove rows where 'ciudad' is null
        dataframe = dataframe[~dataframe['ciudad'].isnull()]

        # This formatting would have eight food categories within the same spreadsheet divided only by a big title.
        # Such title would include the word 'cuadro'. So, to separate categories, we look for blocks of data contained
        # within two consecutive appearances of such words.

        # Get row indexes where the word 'cuadro' is present
        index_cuadro = dataframe[dataframe['ciudad'].str.contains('cuadro')].index
        
        # Creating target dataframe for all data
        df_final = pd.DataFrame()

        # Iterating over food categories.
        for i_categoria in range(len(index_cuadro) + 1):
            # week 16 of 2015 does not have the 'cuadro' titles. 
            try:
                # Capturing first category
                if i_categoria == 0:
                    dataframe_categoria = dataframe[1:index_cuadro[i_categoria]]
                # capturing intermediate categories
                elif (i_categoria <= 6) and (i_categoria > 0):
                    dataframe_categoria = dataframe[index_cuadro[i_categoria - 1] + 2:index_cuadro[i_categoria]]
                # Capturing last category
                else:
                    dataframe_categoria = dataframe[index_cuadro[i_categoria - 1] + 2:]

                # Within each category block, add category name
                dataframe_categoria['categoria'] = self.categories_dict[i_categoria + 1]

                # within each category block, there are several products. In the whole reporting, products are very likely to
                # contain several rows (same food item in different locations). What identifies such product blocks is the
                # fact that the precio_minimo column will be blank. So the product data would be contain within two
                # consecutive occurrences of blank prices.
                index_producto = dataframe_categoria[dataframe_categoria['precio_minimo'].isnull()].index

                # creating target data frame for product category
                df_categoria_final = pd.DataFrame()

                # Iterating over products within food category
                for i_producto in range(len(index_producto)):

                    # Capturing the first product in the category
                    if i_producto == 0:
                        dataframe_producto = dataframe_categoria.loc[
                                            index_producto[i_producto] - 1:index_producto[i_producto + 1] - 1].reset_index(
                            drop=True)

                    # Capturing all intermediate products
                    elif i_producto < len(index_producto) - 1:
                        dataframe_producto = dataframe_categoria.loc[
                                            index_producto[i_producto]:index_producto[i_producto + 1] - 1].reset_index(
                            drop=True)

                    # Capturing last product within category
                    else:
                        dataframe_producto = dataframe_categoria.loc[index_producto[i_producto]:].reset_index(drop=True)

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
                    df_categoria_final = pd.concat([df_categoria_final, dataframe_producto], ignore_index=True)

                # Putting together all data
                df_final = pd.concat([df_final, df_categoria_final], ignore_index=True)
            except: 
                None
        # Once data per file is complete, time stamps are added: year and week number
        df_final['semana_no'] = int(Path(file_path).name.split('_')[1])  # file_path.stem[5:7]
        df_final['anho'] = Path(file_path).stem[-4:]

        return df_final
    
    def second_format_wrangling(self, bucket_name: str):
        second_format_files = self.second_format_paths(bucket_name)
        year_file2 = pd.DataFrame()
        print('[Info] Working on second batch of files')
        for file_path in tqdm(second_format_files):
            try:
                # local_file_path = self.download_file_from_s3(file_path, bucket_name)
                # ref_dict = self.get_sheet_names(local_file_path)
                ref_dict, xl = self.get_sheet_names(file_path, bucket_name, self.s3)
                dataframe_file = self.process_excel_sheets(file_path, ref_dict, xl)
                year_file2 = self.concat_to_year_file(year_file2, dataframe_file)
                
            except Exception as e:
                print(f'[Info] There is a problem in {file_path}: \n {e}')

        return year_file2

    def download_file_from_s3(self, file_path, bucket_name):
        bucket = self.s3.Bucket(bucket_name)
        obj = bucket.Object(file_path)
        local_file_path = Path.cwd() / Path(file_path).name
        # obj.download_file(local_file_path)
        
        return local_file_path

    def get_sheet_names(self, file_path, bucket_name, s3):
        # with open(local_file_path, 'rb') as f:
        #     xl = pd.ExcelFile(f)

        # return {i: xl.sheet_names[i] for i in range(len(xl.sheet_names))}
        # Read Excel data from S3 object
        # Get the S3 bucket and object
        bucket = s3.Bucket(bucket_name)
        obj = bucket.Object(file_path)
        
        # Read the Excel file from S3
        xls_data = obj.get()['Body'].read()

        # Create an ExcelFile object with specified encoding
        xl = pd.ExcelFile(BytesIO(xls_data), engine='xlrd')

        # Get the list of sheet names
        return {i: xl.sheet_names[i] for i in range(len(xl.sheet_names))}, xl
        


    def process_excel_sheets(self, local_file_path, ref_dict, xl):
        dataframe_file = pd.DataFrame()
        for index in range(1, 9):
            # with open(local_file_path, 'rb') as f:
            #     dataframe = pd.read_excel(f, sheet_name=ref_dict[index])
            dataframe = pd.read_excel(xl, sheet_name=ref_dict[index])

            dataframe = self.process_sheet(dataframe, local_file_path, index)
            dataframe_file = self.concat_to_dataframe_file(dataframe_file, dataframe)
        return dataframe_file

    def process_sheet(self, dataframe, local_file_path, index):
        if pd.isnull(dataframe.iloc[9, 0]):
            dataframe = dataframe.iloc[10:, :6]
        else:
            dataframe = dataframe.iloc[9:, :6]
        dataframe.columns = ['producto', 'ciudad', 'precio_minimo', 'precio_maximo', 'precio_medio', 'tendencia']
        dataframe = dataframe[~dataframe['ciudad'].isnull()]
        dataframe['ciudad'] = dataframe['ciudad'].str.replace(r'\s*\([^)]*\)', '', regex=True)
        dataframe['ciudad'] = dataframe['ciudad'].str.lower().str.replace('bogotá, d.c.', 'bogota')
        dataframe['ciudad'] = dataframe['ciudad'].str.replace(r'\s*\([^)]*\)', '', regex=True)

        # Adding categoria and ciudad info
        dataframe['categoria'] = self.categories_dict[index]
                    
                    
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
        dataframe['semana_no'] = int(Path(local_file_path).name.split('_')[1])  # file_path.stem[5:7]
        dataframe['anho'] = Path(local_file_path).stem[-4:]
        
        return dataframe

    def concat_to_dataframe_file(self, dataframe_file, dataframe):
        return pd.concat([dataframe_file, dataframe], ignore_index=True)

    def concat_to_year_file(self, year_file2, dataframe_file):
        return pd.concat([year_file2, dataframe_file], ignore_index=True)


    def building_final_file(self, bucket_name:str): 
        first_batch = self.first_format_wrangling(bucket_name)
        second_batch = self.second_format_wrangling(bucket_name)

        df_final = pd.concat([first_batch,second_batch], ignore_index=True)

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
        
        df_final = df_final[(~df_final['precio_minimo'].isnull()) &
                            (~df_final['precio_maximo'].isnull()) & 
                            (~df_final['precio_medio'].isnull()) & 
                            (df_final['precio_medio']!='b')]

        df_final['precio_minimo'] = df_final['precio_minimo'].astype(int)
        df_final['precio_maximo'] = df_final['precio_maximo'].astype(int)
        df_final['precio_medio'] = df_final['precio_medio'].astype(int)

        df_final['producto'] = df_final['producto'].str.lower()
        df_final = df_final[~df_final['producto'].isnull()]

        df_final['region'] = df_final['ciudad'].map(city_to_region)
        return df_final
    
