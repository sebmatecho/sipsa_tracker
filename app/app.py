import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from app_utils import visualizations as visuals
from app_utils import queries 

# Set up Streamlit page configuration
st.set_page_config(
    page_title="SIPSA explorer",
    page_icon="📊",
    layout="wide",
)


# Main app content
st.title("Exploring Colombian Food Price Dynamics - SIPSA Project")
st.header("Developed by [Sébastien Lozano-Forero](https://www.linkedin.com/in/sebastienlozanoforero/)")
# st.write("""
# 		 This Streamlit app provides an interactive exploration of Colombian food price dynamics using data from DANE (Departamento Administrativo Nacional de Estadística). 
# 		 By connecting directly to an AWS RDS database, it offers up-to-date visualizations that help users analyze trends, fluctuations, and anomalies in product pricing 
# 		 across different cities and marketplaces. With features to compare regional differences, examine price volatility, and detect potential monopolistic behaviors, 
# 		 this tool is invaluable for researchers, policymakers, and businesses seeking to gain deeper insights into the factors influencing Colombia's 
# 		 food markets and understand economic implications for consumers nationwide.
# 		 """
# 		 )

# Sidebar
st.sidebar.header("Settings")

visualization_type = st.sidebar.radio(
    "Analysis area",
    ("Introduction to SIPSA Project", 
     "Price Trends Across Time", 
     "Individual Products",
    #  "City and Regional Comparisons", 
    #  "Category-Specific Trends",
    #  "Product Popularity and Trends",
    #  "Price Extremes and Anomalies",
     "Marketplaces Exploration", 
    #  "Relationship Between Prices and Trends" 
	)
)


# Content for the Introduction tab
if visualization_type == "Introduction to SIPSA Project":
    # st.title("SIPSA Project - Food Price Visualization Tool")
    st.markdown("""
    # 
    ### Welcome to the SIPSA Food Price Visualization Tool!
    
    This application provides an interactive platform for exploring food price trends in Colombia. Using data provided by the DANE (National Administrative Department of Statistics), the **Sistema de Información de Precios y Abastecimiento del Sector Agropecuario (SIPSA)** aims to facilitate deeper insights into Colombian food dynamics by allowing users to visualize how different food products' prices vary across time, cities, and regions.

    Our interactive visualization tool provides the following features:
    
    - **Price Trends Across Time:** Understand price patterns and long-term trends for various food products.
    - **City and Regional Comparisons:** Compare the differences in food pricing among Colombian cities and regions.
    - **Category-Specific Trends:** Delve into particular product categories, such as meats, grains, or vegetables, to see how they behave.
    - **Product Popularity and Trends:** Examine how the popularity of certain products and their prices evolve over time.
    - **Price Extremes and Anomalies:** Identify unusual fluctuations in food prices and understand the causes behind them.
    - **Market-Specific Insights:** Learn about the different Colombian markets and how they contribute to price trends.
    - **Relationship Between Prices:** Analyze the correlation between prices of different products and categories.

    ### Architecture of the Application
    This tool is built using **Streamlit**, an easy-to-use framework for creating interactive web applications in Python. It is hosted on **AWS** services to ensure scalability, security, and reliable performance. Below is an overview of the architecture:

    - **AWS RDS** is used to store and manage the food pricing data.
    - **AWS EC2 or Lightsail** hosts the Streamlit application, ensuring that users can access the tool anytime, anywhere.
    - The data is dynamically queried from **AWS RDS** to ensure up-to-date and accurate information is presented on all charts and visualizations.

    The goal is to create a **playground for exploring information** about Colombian food markets. By making use of a wide range of interactive visualizations, users will be able to explore the information they need, adjusting parameters to view trends at different levels of **granularity**. This includes filtering by specific **categories**, **regions**, **marketplaces**, and **timeframes**, allowing for a customizable and comprehensive exploration of the data.

    This tool aims to help everyone from researchers, government agencies, farmers, policy-makers, and the general public to understand **food price trends**, **identify regional differences**, and gain a holistic view of the **agriculture market**.

    #### How to Use This Tool:
    - Use the **Sidebar** to select the analysis area you wish to explore.
    - Start with the "Price Trends Across Time" to gain an understanding of the overall trends.
    - Navigate to different sections to dive deeper into specific topics of interest.
    
    We encourage you to explore the sections to gain insights into **Colombian food price dynamics**, trends over the years, and unique pricing behaviors. Whether you are interested in **food security**, **market trends**, or specific product fluctuations, this tool can serve as an important resource.
    """)
    
    st.title("Composition of the SIPSA Database")
    dataframe = queries.city_composition_query()
    visuals.city_composition_visualization(dataframe = dataframe)

    dataframe = queries.category_composition_query()
    visuals.category_composition_visualization(dataframe = dataframe)

    

    st.markdown("""
    ---
    
    *SIPSA Project - An interactive exploration of Colombia's agricultural markets.*
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
        visuals.plot_product_seasonal_trends(dataframe=dataframe, 
                                            product = product.title().replace('_',' '))
     else:
        cities = queries.city_query()
        cities_list = [city.title().replace('_',' ') for city in cities['ciudad'].to_list()]
        city = st.selectbox("City of interest", 
                          cities_list)
        city = city.lower().replace(' ','_')
        


        products_list= queries.product_query_by_city(city =city)
        products_list = [product.title().replace('_',' ') for product in products_list['product'].to_list()]
        product = st.selectbox("Product of interest", 
                            products_list)
        product = product.lower().replace(' ','_')
        dataframe = queries.product_evolution_query_by_city(product = product, 
                                                            city = city)
        visuals.plot_product_seasonal_trends(dataframe=dataframe, 
                                            product = product.title().replace('_',' '), 
                                            city = city)
        

if visualization_type =='Marketplaces Exploration':

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




# Footer
st.sidebar.write("SIPSA project APP - Streamlit")


# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align: center;'>Developed by <b>Sébastien Lozano-Forero</b></div>",
    unsafe_allow_html=True,
)