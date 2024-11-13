import numpy as np
np.float_ = np.float64
import sys
from pathlib import Path
import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
from datetime import timedelta, datetime
import streamlit as st
from io import BytesIO
from prophet.plot import plot_plotly, plot_components_plotly
import plotly.graph_objs as go

def remove_timezone(dt):
    return dt.replace(tzinfo=None)

def forecast_price_for_product_city(dataframe, 
									product, 
									city, 
									steps):
	df_filtered = dataframe[['date', 'avg_price']]
	df_filtered.columns = ['ds', 'y']  
	  
	# remove timezone info - Prophet is picky AF
	df_filtered['ds'] = df_filtered['ds'].apply(remove_timezone)
	# Initialize the Prophet model
	model = Prophet(interval_width=0.95, yearly_seasonality=True, weekly_seasonality=False)
    # Fit the model
	model.fit(df_filtered)

	future_dates = model.make_future_dataframe(periods=steps, freq='W')

    #  Forecast the future prices
	forecast = model.predict(future_dates)

    # Plot the forecast
	fig = model.plot(forecast)
	# fig = plot_plotly(model, forecast)
      
	plt.title(f"Price Forecast for {product.title().replace('_',' ')} in {city.title()}", fontsize=16, weight='bold')
	plt.xlabel('Date', fontsize=12)
	plt.ylabel('Average Price', fontsize=12)
	# Adjust layout for readability
	plt.tight_layout()

    # Display the plot using Streamlit
	st.pyplot(plt)

    # Save the plot to a BytesIO buffer for download
	buf = BytesIO()
	plt.savefig(buf, format="png")
	buf.seek(0)

    # Provide a download button for the plot
	st.download_button(
        label="Download Plot as PNG",
        data=buf,
        file_name=f"price_forecast_{product}_in_{city}_{steps}_ahead.png",
        mime="image/png")
    
	forecast = forecast[['ds','yhat']].tail(steps)
	forecast.columns = ['date','projected_value']
	forecast['product'] = product
	forecast['city'] = city 
	forecast = forecast[['date','product', 'city', 'projected_value']]
      
	return forecast