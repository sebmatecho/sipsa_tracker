import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from app_utils import visualizations as visuals
from app_utils import queries 
from pathlib import Path
from PIL import Image




# Set up Streamlit page configuration
st.set_page_config(
    page_title="SIPSA explorer",
    page_icon="📊",
    layout="wide",
)


# Main app content
st.title("SIPSApp - Exploring Colombian Food Price Dynamics 🥑🍖📊")




# st.sidebar.image(sipsapp_logo, use_column_width=True)
with st.sidebar.container():
    img_path = Path().cwd().parent/'img'/'sipsapp2.png'
    image = Image.open(img_path)
    st.image(image, use_column_width=True)
# Sidebar
st.sidebar.header("SIPSApp Start! 🥑🍖📊")

visualization_type = st.sidebar.radio(
    "Area of Interest",
    ("Hi, I'm SIPSApp! 👋", 
     "Price Trends Across Time", 
     "Individual Products",
    #  "City and Regional Comparisons", 
    #  "Category-Specific Trends",
    #  "Product Popularity and Trends",
    #  "Price Extremes and Anomalies",
     "Product Affordability",
     "Marketplaces Exploration", 
    #  "Seasonal Descomposition"
    #  "Relationship Between Prices and Trends" 
	)
)


# Content for the Introduction tab
if visualization_type == "Hi, I'm SIPSApp! 👋":
    # st.title("SIPSA Project - Food Price Visualization Tool")
    st.markdown("""
    ### Welcome to SIPSApp! 
    
This application provides an interactive platform for exploring food price trends in Colombian marketplaces. Using data provided by the Colombian Administrative Department of Statistics - [DANE](), the Sistema de Información de Precios y Abastecimiento del Sector Agropecuario [SIPSA](https://www.dane.gov.co/index.php/estadisticas-por-tema/agropecuario/sistema-de-informacion-de-precios-sipsa) is a comprehensive system for monitoring how food prices behave across cities and regions of Colombia.

With this tool, you'll be able to visualize:

- Price trends across time for different food products.
- City and regional price comparisons, highlighting disparities in affordability.
- Category-specific trends to see which food groups have undergone significant changes.
- Affordability metrics for different categories to understand which food groups are becoming more or less accessible.
                
SIPSApp aims to help everyone—from researchers, policymakers, farmers, businesses, to everyday consumers—understand and engage with Colombian food pricing dynamics. Our interactive tool provides deep insights into food price behavior and promotes data-driven decision-making.

SIPSApp Features Include:

- Price Trends Across Time: Visualize average prices and detect inflationary patterns across product categories over time.
- Individual Product Analysis: Look at trends for specific products, either across the country or within individual cities.
- Product Affordability: Evaluate how different food products compare in terms of affordability, broken down by category and city.
- Marketplaces Exploration: Compare food pricing across different marketplaces to understand regional disparities.
- Seasonal Decomposition: Identify trends, seasonality, and anomalies by decomposing product price data over time.

How to Navigate:

- Use the Sidebar to explore various tabs.
- Choose areas of interest such as "Price Trends Across Time" or "Product Affordability".
- Make use of filters to see individual product insights and market trends.
    """)
    
    st.title("Composition of the SIPSA Database")

    st.markdown("""
                This is where you start! The introduction provides an overview of SIPSApp, along with some background on how the data is collected, processed, and presented. The composition of the dataset is illustrated with stacked bar charts that show the number of records per year and city and year and category, providing a sense of the data's coverage and granularity.
                """)

    dataframe = queries.city_composition_query()

    visuals.city_composition_visualization(dataframe = dataframe)

    dataframe = queries.category_composition_query()
    visuals.category_composition_visualization(dataframe = dataframe)

    

    st.markdown("""
    ---
    
    *SIPSApp - Colombian Food Prices.*
    """)


if visualization_type == 'Price Trends Across Time':
      
      dataframe = queries.nation_wide_trend()
      visuals.lineplot_per_category_nationwide(dataframe=dataframe, 
                                                numerical_value='mean_price',
                                                categorical_value='category',
                                                title='Price Evolution by Category (Nationwide)',
                                                xlabel='',
                                                ylabel='Average Price')



      cities = queries.city_query()
      cities_list = [city.title().replace('_',' ') for city in cities['ciudad'].to_list()]
      city = st.selectbox("City of interest", 
                          cities_list)
      
      
      city = city.lower().replace(' ','_')
      dataframe = queries.price_category_query(city = city)
      
      visuals.lineplot_per_category(dataframe = dataframe, 
									numerical_value = 'mean_price' ,
									categorical_value = 'category',
                                    city = city, 
									title = f"Price Evolution by Category ({city.title().replace('_',' ')})",                   
									xlabel = '', 
									ylabel = 'Average Price')


if visualization_type ==  "Individual Products":
     visual_type = st.radio(
    "Would you like to see nation-wide trends or city-wide trends?",
    ["Nation-wide", "City-wide", ],

)
     if visual_type == "Nation-wide":
          
        products_list= queries.product_query()
        products_list = [product.title().replace('_',' ') for product in products_list['product'].to_list()]
        product = st.selectbox("Product of interest", 
                            products_list)
        product = product.lower().replace(' ','_')
        dataframe = queries.product_evolution_query(product = product)
        visuals.plot_product_seasonal_trends_national(dataframe=dataframe, 
                                            product = product.title().replace('_',' '))
     else:
        cities = queries.city_query()
        cities_list = [city.title().replace('_',' ') for city in cities['ciudad'].to_list()]
        cities = st.multiselect("Cities of interest", 
                          cities_list, 
                          ['Bogota'])
        cities = [city.lower().replace(' ','_') for city in cities]
        

        products_list= queries.product_query_by_city(cities = cities)
        products_list = [product.title().replace('_',' ') for product in products_list['product'].to_list()]
        product = st.selectbox("Product of interest", 
                            products_list)
        product = product.lower().replace(' ','_')
        dataframe = queries.product_evolution_query_by_city(product = product, 
                                                            cities = cities)
        visuals.plot_product_seasonal_trends(dataframe=dataframe, 
                                            product = product.title().replace('_',' '), 
                                            cities = cities)
        

if visualization_type =='Marketplaces Exploration':

    dataframe = queries.marketplace_count_query()
    visuals.plot_marketplace_count(dataframe = dataframe)

    visual_type = st.radio(
    "Would you like to see product-wide trends or category-wide trends?",
    ["Product-wide", "Category-wide"],
    )
    if visual_type == "Category-wide":
    
        dataframe = queries.marketplaces_dynamics_query()
        category_list = list(dataframe['category'].unique())
        category_list = [category.title().replace('_',' ') for category in category_list]
        category = st.selectbox("Category of interest", 
                                category_list)
        category = category.lower().replace(' ','_')
        visuals.plot_price_distribution(dataframe = dataframe, 
                                        category = category)

    else: 
        products_list= queries.product_query()
        products_list = [product.title().replace('_',' ') for product in products_list['product'].to_list()]
        product = st.selectbox("Product of interest", 
                            products_list)
        product = product.lower().replace(' ','_')


        dataframe = queries.marketplaces_product_dynamics_query(product = product)
        visuals.plot_price_distribution(dataframe = dataframe, 
                                        product = product)

if visualization_type =='Seasonal Descomposition':
    cities = queries.city_query()

    cities_list = [city.title().replace('_',' ') for city in cities['ciudad'].to_list()]
    city = st.selectbox("Cities of interest", 
                                cities_list)
    city = city.lower().replace(' ','_')
   

    products_list= queries.product_query_by_city(cities = city)
    products_list = [product.title().replace('_',' ') for product in products_list['product'].to_list()]
    product = st.selectbox("Product of interest", 
                            products_list)
    product = product.lower().replace(' ','_')

    dataframe = queries.product_price_evolution(product = product)
    product = product.title().replace('_',' ') 
    st.write(product)
    visuals.plot_seasonal_decomposition(dataframe = dataframe, 
                                        product = product, 
                                        city = city)

if visualization_type == 'Product Affordability':
    category_list= queries.category_query()
    category_list = [category.title().replace('_',' ') for category in category_list['category'].to_list()]

    category = st.selectbox("Product of interest", 
                            category_list)
    
    category = category.lower().replace(' ','_')
    cities = queries.city_query()

    cities_list = [city.title().replace('_',' ') for city in cities['ciudad'].to_list()]
    city = st.selectbox("City of interest", 
                                cities_list)
    city = city.lower().replace(' ','_')
    dataframe = queries.affordability_category_by_city(category = category,
                                                       city = city)
    visuals.plot_product_affordability_rank(dataframe = dataframe, 
                                            category = category,
                                            city = city)
    
# Footer
st.sidebar.write("SIPSA project APP - Streamlit")


# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="text-align: center;">
        Developed by <a href="https://www.linkedin.com/in/sebastienlozanoforero/" target="_blank" style="text-decoration: none; color: #4CAF50;">Sébastien Lozano Forero</a>
    </div>
    """, 
    unsafe_allow_html=True
)