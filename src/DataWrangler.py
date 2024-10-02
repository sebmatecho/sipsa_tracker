

import pandas as pd
from src.FileNameBuilder import FileNameBuilder
from config import CATEGORIES_DICT, CITY_TO_REGION
import boto3
import logging
from pathlib import Path
from io import BytesIO
from tqdm import tqdm
import re
import numpy as np

class DataWrangler(FileNameBuilder):
    """
    A class to handle data extraction and transformation from Excel files stored in an S3 bucket.

    This class extends the FileNameBuilder class to include data wrangling functionalities such as 
    extracting and transforming data from different formats of Excel files, constructing complete reports,
    and categorizing data based on predefined schemas.

    Attributes:
        bucket_name (str): The name of the S3 bucket to interact with.
        s3 (boto3.resource): An S3 resource object to interact with AWS S3.
        logger (logging.Logger): Logger instance for logging messages.
        categories_dict (dict): A dictionary mapping category indices to category names.
        city_to_region (dict): A dictionary mapping city names to their respective regions.

    Methods:
        __init__(bucket_name: str, s3: boto3.resource, logger: logging.Logger):
            Initializes the DataWrangler class with S3 resource, bucket name, and logger.

        first_format_data_extraction(file_path: str) -> pd.DataFrame:
            Extracts and processes data from an Excel file stored in an S3 bucket using the first format.

        first_format_data_transformation(dataframe: pd.DataFrame, file_path: str) -> pd.DataFrame:
            Transforms the raw data extracted from a file into a structured format with relevant categories and products.

        second_format_data_extraction(file_path: str) -> pd.DataFrame:
            Extracts and processes data from an Excel file stored in an S3 bucket using multiple sheets for the second format.

        building_complete_report() -> pd.DataFrame:
            Constructs a complete report by extracting and transforming data from two different file formats stored in an S3 bucket.
    """
    def __init__(self, 
                 bucket_name: str, 
                 s3: boto3.resource, 
                 logger:logging.Logger):
        """
        Initializes the DataWrangler class with S3 resource, bucket name, and logger.

        Args:
            bucket_name (str): The name of the S3 bucket to interact with.
            s3 (boto3.resource): An S3 resource object to interact with AWS S3.
            logger (logging.Logger): Logger instance for logging messages.
        """
        FileNameBuilder.__init__(self, s3, logger)
        self.bucket_name = bucket_name
        self.s3 = s3
        self.logger = logger
        self.categories_dict = CATEGORIES_DICT
        self.city_to_region = CITY_TO_REGION
        
    def first_format_data_extraction(self, file_path: str) -> pd.DataFrame:
        """
        Extracts and processes data from an Excel file stored in an S3 bucket using the first format.

        This method reads Excel files stored in an S3 bucket, handling different file formats and engines.
        It returns a DataFrame with the extracted data or an empty DataFrame if extraction fails.

        Args:
            file_path (str): The path of the file in the S3 bucket.

        Returns:
            pd.DataFrame: A DataFrame containing the extracted data, or an empty DataFrame if extraction fails.
        """
        bucket = self.s3.Bucket(self.bucket_name)
        obj = bucket.Object(file_path)
        xls_data = obj.get()['Body'].read()

        dataframe = None
        try:
            dataframe = pd.read_excel(BytesIO(xls_data), engine='openpyxl')
        except Exception as e:
            self.logger.debug(f"openpyxl failed for {file_path}: {e}")
        if dataframe is None:
            try:
                dataframe = pd.read_excel(BytesIO(xls_data), engine='xlrd')
            except Exception as e:
                self.logger.error(f"Failed to read Excel file {file_path} with xlrd: {e}")
                return pd.DataFrame()  # Return empty DataFrame if reading fails

        if dataframe.empty:
            self.logger.warning(f"No data found in {file_path}")
            return pd.DataFrame()

        dataframe = dataframe[dataframe[dataframe.columns[0]].apply(
            lambda x: bool(re.search(r'[a-zA-Z]', str(x))) and pd.notna(x))]

        return dataframe

    def first_format_data_transformation(self, dataframe: pd.DataFrame, file_path: str) -> pd.DataFrame:
        """
        Transforms the raw data extracted from a file into a structured format with relevant categories and products.

        This method processes the extracted data by renaming columns, identifying product categories, and cleaning city names.
        It returns a structured DataFrame containing the transformed data.

        Args:
            dataframe (pd.DataFrame): The raw extracted data as a DataFrame.
            file_path (str): The path of the file in the S3 bucket.

        Returns:
            pd.DataFrame: A DataFrame containing the transformed data, or an empty DataFrame if transformation fails.
        """
        # Keep only the first five columns and rename them
        dataframe = dataframe.iloc[:, 0:5]
        dataframe.columns = ['ciudad', 'precio_minimo', 'precio_maximo', 'precio_medio', 'tendencia']
        dataframe['ciudad'] = dataframe['ciudad'].str.lower().str.replace('bogotá, d.c.', 'bogota')

        # Remove rows where 'ciudad' is null
        dataframe = dataframe[~dataframe['ciudad'].isnull()]

        # Get row indexes where the word 'cuadro' is present
        index_cuadro = dataframe[dataframe['ciudad'].str.contains('cuadro', case=False, na=False)].index.tolist()

        if not index_cuadro:
            self.logger.warning(f"No 'cuadro' titles found in {file_path}")
            return pd.DataFrame()  # Return empty DataFrame if no categories found

        # Create target dataframe for all data
        df_final = pd.DataFrame()

        # Iterate over food categories
        for i_categoria in range(len(index_cuadro) + 1):
            try:
                if i_categoria == 0:
                    dataframe_categoria = dataframe.iloc[1:index_cuadro[i_categoria]]
                elif i_categoria <= 6:
                    dataframe_categoria = dataframe.iloc[index_cuadro[i_categoria - 1] + 2:index_cuadro[i_categoria]]
                else:
                    dataframe_categoria = dataframe.iloc[index_cuadro[i_categoria - 1] + 2:]

                # Add category name
                dataframe_categoria = dataframe_categoria.copy()
                dataframe_categoria['categoria'] = self.categories_dict.get(i_categoria + 1, 'unknown')

                # Identify products within category
                index_producto = dataframe_categoria[dataframe_categoria['precio_minimo'].isnull()].index.tolist()
                if not index_producto:
                    continue

                df_categoria_final = pd.DataFrame()

                for i_producto in range(len(index_producto)):
                    if i_producto < len(index_producto) - 1:
                        start_idx = index_producto[i_producto]
                        end_idx = index_producto[i_producto + 1]
                    else:
                        start_idx = index_producto[i_producto]
                        end_idx = None

                    dataframe_producto = dataframe_categoria.loc[start_idx:end_idx].reset_index(drop=True)

                    # Add product name
                    producto_name = dataframe_producto.at[0, 'ciudad']
                    dataframe_producto['producto'] = producto_name

                    # Clean city names
                    dataframe_producto['ciudad'] = dataframe_producto['ciudad'].str.replace(r'\s*\([^)]*\)', '', regex=True)

                    # Extract marketplace if present
                    dataframe_producto['mercado'] = dataframe_producto['ciudad'].str.extract(r',\s*(.*)')[0]
                    dataframe_producto['ciudad'] = dataframe_producto['ciudad'].str.split(',').str[0].str.strip()
                    dataframe_producto = dataframe_producto[~dataframe_producto['precio_medio'].isnull()]
                    
                    # Drop first row (product name)
                    dataframe_producto = dataframe_producto.iloc[1:].reset_index(drop=True)

                    df_categoria_final = pd.concat([df_categoria_final, dataframe_producto], ignore_index=True)

                df_final = pd.concat([df_final, df_categoria_final], ignore_index=True)

            except Exception as e:
                self.logger.error(f"Error processing category {i_categoria} in file {file_path}: {e}")
                continue

        if df_final.empty:
            self.logger.warning(f"No data extracted from {file_path} after transformation.")
            return df_final

        # Add timestamps
        try:
            df_final['semana_no'] = int(Path(file_path).stem.split('_')[1])
            df_final['anho'] = Path(file_path).stem[-4:]
        except Exception as e:
            self.logger.error(f"Error extracting week and year from {file_path}: {e}")
            df_final['semana_no'] = None
            df_final['anho'] = None

        # Reorder columns
        df_final = df_final[['producto', 'ciudad', 'precio_minimo', 'precio_maximo', 'precio_medio',
                             'tendencia', 'categoria', 'mercado', 'semana_no', 'anho']]
        
        df_final= df_final[~df_final['precio_medio'].isnull()]
        
        return df_final

    def second_format_data_extraction(self, file_path: str) -> pd.DataFrame:
        """
        Extracts and processes data from an Excel file stored in an S3 bucket using multiple sheets for the second format.

        This method reads Excel files stored in an S3 bucket, handling different file formats and sheets. 
        It returns a structured DataFrame containing the extracted data.

        Args:
            file_path (str): The path of the file in the S3 bucket.

        Returns:
            pd.DataFrame: A DataFrame containing the extracted data, or an empty DataFrame if extraction fails.
        """
        bucket = self.s3.Bucket(self.bucket_name)
        obj = bucket.Object(file_path)
        xls_data = obj.get()['Body'].read()

        xl = None
        try:
            xl = pd.ExcelFile(BytesIO(xls_data), engine='openpyxl')
        except Exception as e:
            self.logger.debug(f"openpyxl failed for {file_path}: {e}")
        if xl is None:
            try:
                xl = pd.ExcelFile(BytesIO(xls_data), engine='xlrd')
            except Exception as e:
                self.logger.error(f"Failed to read Excel file {file_path} with xlrd: {e}")
                return pd.DataFrame()

        full_dataframe = pd.DataFrame()
        for index in range(1, 9):
            sheet_name = xl.sheet_names[index]
            dataframe = None
            try:
                dataframe = pd.read_excel(BytesIO(xls_data), sheet_name=sheet_name)
            except Exception as e:
                self.logger.error(f"Failed to read sheet {sheet_name} in {file_path}: {e}")
                continue

            if dataframe.empty:
                self.logger.warning(f"No data found in sheet {sheet_name} of {file_path}")
                continue

            if file_path == 'reports/2018/week_20_Sem_12may__18may_2018.xlsx':
                dataframe['mercado'] = dataframe['Mercado mayorista'].str.split(',').str[1].str.strip()
                dataframe['ciudad'] = dataframe['Mercado mayorista'].str.split(',').str[0].str.strip()
                dataframe.columns = dataframe.columns.str.lower().str.replace(' ','_').str.replace('í','i').str.replace('á','a')
            else:

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
            dataframe['semana_no'] = int(Path(file_path).name.split('_')[1])  # file_path.stem[5:7]
            dataframe['anho'] = Path(file_path).stem[-4:]
          

            # Add to full_dataframe
            full_dataframe = pd.concat([full_dataframe, dataframe], ignore_index=True)

        if full_dataframe.empty:
            self.logger.warning(f"No data extracted from {file_path} after processing all sheets.")
            return full_dataframe

        # Reorder columns
        full_dataframe = full_dataframe[['producto', 'ciudad', 'precio_minimo', 'precio_maximo', 'precio_medio',
                                         'tendencia', 'categoria', 'mercado', 'semana_no', 'anho']]
        return full_dataframe

    def building_complete_report(self) -> pd.DataFrame:
        """
        Constructs a complete report by extracting and transforming data from two different file formats stored in an S3 bucket.

        This method consolidates data from the two different file formats (first and second format) stored in an S3 bucket.
        It combines and transforms the data into a structured report for analysis or further processing.

        Returns:
            pd.DataFrame: A complete report DataFrame containing data from both file formats.
        """
        first_format_paths_aws = self.first_format_paths(bucket_name=self.bucket_name)
        second_format_paths_aws = self.second_format_paths(bucket_name=self.bucket_name)

        first_format_final = pd.DataFrame()
        self.logger.info('[INFO] First batch of files')

        for file_path in tqdm(first_format_paths_aws):
            dataframe = self.first_format_data_extraction(file_path)
            if not dataframe.empty:
                transformed_df = self.first_format_data_transformation(dataframe, file_path)
                first_format_final = pd.concat([first_format_final, transformed_df], ignore_index=True)

        self.logger.info('[INFO] Second batch of files')
        second_format_final = pd.DataFrame()
        for file_path in tqdm(second_format_paths_aws):
            dataframe = self.second_format_data_extraction(file_path)
            second_format_final = pd.concat([second_format_final, dataframe], ignore_index=True)

        complete_report = pd.concat([first_format_final, second_format_final], ignore_index=True)
        return complete_report
