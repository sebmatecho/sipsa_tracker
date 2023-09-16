import streamlit as st
import pandas as pd
from utils import aws
from pathlib import Path
from utils import app_utils
import boto3
from dotenv import load_dotenv
import os


# pd.read_csv
st.write('## Colombian food prices tracker :flag-co: :avocado: :canned_food:')
st.write('###### Developed by [Sébastien Lozano-Forero](https://www.linkedin.com/in/sebastienlozanoforero/)')

st.write('Data compiled from the Colombian National Division of Statistics (DANE) through the [SIPSA](https://www.dane.gov.co/index.php/estadisticas-por-tema/agropecuario/sistema-de-informacion-de-precios-sipsa) program.')


@st.cache_data
def fetch_and_clean_data():
    load_dotenv()
    aws_access_key_id = os.environ['aws_access_key_id']
    aws_secret_access_key = os.environ['aws_secret_access_key']
    
    # Creating boto3 session (access the S3 bucket)
    s3 = boto3.resource('s3',
                        aws_access_key_id = aws_access_key_id, 
			aws_secret_access_key = aws_secret_access_key)
    
#     data = pd.read_csv('https://media.githubusercontent.com/media/sebmatecho/sipsa_tracker/master/reports/full_report.csv')
    data = aws.read_csv_from_s3(s3 = s3, bucket_name = 'sipsatracker',file_name = 'full_report.csv')
    return data

dataframe = fetch_and_clean_data()



with st.sidebar:
    figure = st.radio(
              "How you want to track prices?",
              ["Product only", "Product by city", "Product by region", 
               'Product category only', 'Product category by city', 'Product category by region'])

# Visualizing product only 
if figure == 'Product only':
             
    producto = st.selectbox(
            'What product product you want to display?',
            dataframe['producto'].unique())
    app_utils.product_evolution(dataframe = dataframe, product = producto)

# # Visualizing product only 
if figure == 'Product by city':
    ciudad = st.selectbox(
            'What city you want to display?',
            [x.title() for x in dataframe.ciudad.unique()])
    producto = st.selectbox(
            'What product product you want to display?',
            dataframe['producto'].unique())

    app_utils.product_city_evolution(dataframe = dataframe, 
                                         ciudad = ciudad.lower(), 
                                         producto = producto)

if figure == 'Product by region':
    region = st.selectbox(
            'What region you want to display?',
            [x.title() for x in dataframe['region'].unique()])
    producto = st.selectbox(
            'What product you want to display?',
            dataframe['producto'].unique())

    app_utils.product_region_evolution(dataframe = dataframe, 
                                         region = region.lower(), 
                                         producto = producto)


# Visualizing product only 
if figure == 'Product category only':
             
    
    # app_utils.category_evolution(dataframe = dataframe, categoria = categoria)
    app_utils.all_category_evolution(dataframe = dataframe)

if figure == 'Product category by city':
    ciudad = st.selectbox(
            'What city you want to display?',
            [x.title() for x in dataframe.ciudad.unique()])
    
    app_utils.all_category_evolution_city(dataframe = dataframe, ciudad = ciudad)


if figure == 'Product category by region':
    region = st.selectbox(
            'What region you want to display?',
            [x.title() for x in dataframe.region.unique()])
    
    app_utils.all_category_evolution_region(dataframe = dataframe, region = region)
