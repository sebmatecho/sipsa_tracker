import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set up Streamlit page configuration
st.set_page_config(
    page_title="SIPSA explorer",
    page_icon="📊",
    layout="wide",
)

# Main app content
st.title("Colombian Food Price Dynamics")
st.write("This Streamlit app provides an interactive exploration of Colombian food price dynamics using data from DANE (Departamento Administrativo Nacional de Estadística). By connecting directly to an AWS RDS database, it offers up-to-date visualizations that help users analyze trends, fluctuations, and anomalies in product pricing across different cities and marketplaces. With features to compare regional differences, examine price volatility, and detect potential monopolistic behaviors, this tool is invaluable for researchers, policymakers, and businesses seeking to gain deeper insights into the factors influencing Colombia's food markets and understand economic implications for consumers nationwide.")

# Sidebar
st.sidebar.header("Settings")

# visualization_type = st.sidebar.radio(
#     "Analysis area",
#     (" Price Trends Across Time", 
#      "City and Regional Comparisons", 
#      "Category-Specific Trends",
#      "Product Popularity and Trends",
#      "Price Extremes and Anomalies",
#      "Market-Specific Insights", 
#      "Relationship Between Prices and Trends" 
# 	)
# )

st.sidebar.title("Analysis Area")
with st.sidebar.expander("Price Trends Across Time"):
    st.write("Details about Price Trends Across Time")
with st.sidebar.expander("City and Regional Comparisons"):
    st.write("Details about City and Regional Comparisons")


# Footer
st.sidebar.write("Created with 💖 using Streamlit")



# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align: center;'>Developed by <b>Sébastien Lozano-Forero</b></div>",
    unsafe_allow_html=True,
)