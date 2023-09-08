from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# def product_evolution(dataframe: pd.DataFrame, 
#                       product: str):
#     dataframe = dataframe.loc[dataframe['producto']==product, ['anho', 'semana_no', 'precio_medio']].groupby(['anho', 'semana_no']).median().reset_index()
#     dataframe['date'] = pd.to_datetime(dataframe['anho'].astype(str) + '-' + dataframe['semana_no'].astype(str) + '-1', format='%Y-%U-%w')
    
#     # Create a line plot
#     fig, ax = plt.subplots(figsize=(10, 6))
#     sns.lineplot(data=dataframe, x='date', y='precio_medio', ax=ax)
    
#     # Calculate the trend line using numpy's polyfit
#     trend_coefficients = np.polyfit(dataframe.index, dataframe['precio_medio'], deg=10)
#     trend_line = np.polyval(trend_coefficients, dataframe.index)

#     # Plot the trend line
#     ax.plot(dataframe['date'], trend_line, label='Trend Line', linestyle='--')
#     ax.set_xlabel('')
#     ax.set_ylabel('Average Price (in COP)')
#     ax.set_title(f'Evolution of price per product: {product}')
#     ax.grid(True)
#     # ax.set_xticks(ax.get_xticks()[::int(len(dataframe) / 10)])  # Show fewer x-axis ticks for readability
#     plt.xticks(rotation=30)
#     plt.tight_layout()

#     # Display the figure in Streamlit
#     st.pyplot(fig)

#     return None



def product_evolution(dataframe: pd.DataFrame, 
                              product: str):
    # Filter and preprocess data
    dataframe = dataframe.loc[dataframe['producto']==product, ['anho', 'semana_no', 'precio_medio']].groupby(['anho', 'semana_no']).median().reset_index()
    dataframe['date'] = pd.to_datetime(dataframe['anho'].astype(str) + '-' + dataframe['semana_no'].astype(str) + '-1', format='%Y-%U-%w')
    
    # Calculate the trend line using numpy's polyfit
    trend_coefficients = np.polyfit(dataframe.index, dataframe['precio_medio'], deg=10)
    trend_line = np.polyval(trend_coefficients, dataframe.index)

    # Create a Plotly figure
    fig = px.line(dataframe, x='date', y='precio_medio', title=f'Evolution of price per product: {product}')
    fig.add_scatter(x=dataframe['date'], y=trend_line, name='Trend Line', line=dict(dash='dash'))

    # Customize the layout
    fig.update_xaxes(title='Year', tickangle=30)
    fig.update_yaxes(title='Average Price (in COP)')
    fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
                      margin=dict(l=20, r=20, t=40, b=20),
                      plot_bgcolor='white', paper_bgcolor='black')

    # Display the Plotly figure in Streamlit
    st.plotly_chart(fig)

    return None


def category_evolution(dataframe: pd.DataFrame, 
                              categoria: str):
    # Filter and preprocess data
    dataframe = dataframe.loc[dataframe['categoria']==categoria, ['anho', 'semana_no', 'precio_medio']].groupby(['anho', 'semana_no']).median().reset_index()
    dataframe['date'] = pd.to_datetime(dataframe['anho'].astype(str) + '-' + dataframe['semana_no'].astype(str) + '-1', format='%Y-%U-%w')
    
    # Calculate the trend line using numpy's polyfit
    trend_coefficients = np.polyfit(dataframe.index, dataframe['precio_medio'], deg=10)
    trend_line = np.polyval(trend_coefficients, dataframe.index)

    # Create a Plotly figure
    fig = px.line(dataframe, x='date', y='precio_medio', title=f'Evolution of price per category: {categoria}')
    fig.add_scatter(x=dataframe['date'], y=trend_line, name='Trend Line', line=dict(dash='dash'))

    # Customize the layout
    fig.update_xaxes(title='Year', tickangle=30)
    fig.update_yaxes(title='Average Price (in COP)')
    fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
                      margin=dict(l=20, r=20, t=40, b=20),
                      plot_bgcolor='white', paper_bgcolor='black')

    # Display the Plotly figure in Streamlit
    st.plotly_chart(fig)

    return None


def all_category_evolution(dataframe: pd.DataFrame):
    # Filter and preprocess data
    dataframe = dataframe[['categoria','anho', 'semana_no', 'precio_medio']].groupby(['categoria','anho', 'semana_no']).median().reset_index()
    dataframe['date'] = pd.to_datetime(dataframe['anho'].astype(str) + '-' + dataframe['semana_no'].astype(str) + '-1', format='%Y-%U-%w')
    
    # Create a Plotly figure
    fig = px.line(dataframe, x='date', y='precio_medio', color='categoria')

    # Customize the layout
    fig.update_xaxes(title='Year', tickangle=30)
    fig.update_yaxes(title='Average Price (in COP)')
    fig.update_layout(
        legend=dict(
            orientation='h',  # Horizontal legend
            yanchor='bottom',  # Anchor at the bottom of the plot
            y=1.02,  # Move legend slightly above the plot
            xanchor='left',
            x=0.01
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='white', paper_bgcolor='black'
    )

    # Display the Plotly figure in Streamlit
    st.plotly_chart(fig)

    return None




# def city_evolution(dataframe: pd.DataFrame, 
#                              ciudad: str):
#     # Filter and preprocess data
#     dataframe = dataframe.loc[dataframe['ciudad']==ciudad, ['anho', 'semana_no', 'precio_medio']].groupby(['anho', 'semana_no']).median().reset_index()
#     dataframe['date'] = pd.to_datetime(dataframe['anho'].astype(str) + '-' + dataframe['semana_no'].astype(str) + '-1', format='%Y-%U-%w')
    
#     # Calculate the trend line using numpy's polyfit
#     trend_coefficients = np.polyfit(dataframe.index, dataframe['precio_medio'], deg=10)
#     trend_line = np.polyval(trend_coefficients, dataframe.index)

#     # Create a Plotly figure
#     fig = px.line(dataframe, x='date', y='precio_medio', title=f'Evolution of price per city: {ciudad.title()}')
#     fig.add_scatter(x=dataframe['date'], y=trend_line, name='Trend Line', line=dict(dash='dash'))

#     # Customize the layout
#     fig.update_xaxes(title='Year', tickangle=30)
#     fig.update_yaxes(title='Average Price (in COP)')
#     fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
#                       margin=dict(l=20, r=20, t=40, b=20),
#                       plot_bgcolor='white', paper_bgcolor='black')

#     # Display the Plotly figure in Streamlit
#     st.plotly_chart(fig)

#     return None

# def product_evolution_category(dataframe: pd.DataFrame, 
#                              categoria: str, 
#                              ciudad: str):
#     # Filter and preprocess data
#     filtered_data = dataframe[(dataframe['categoria'] == categoria.lower()) & (dataframe['ciudad'] == ciudad.lower())]
#     grouped_data = filtered_data[['anho', 'semana_no', 'ciudad','precio_medio']].groupby(['anho', 'semana_no', 'ciudad']).median().reset_index()
#     grouped_data['date'] = pd.to_datetime(grouped_data['anho'].astype(str) + '-' + grouped_data['semana_no'].astype(str) + '-1', format='%Y-%U-%w')
    
#     # Calculate the trend line using numpy's polyfit
#     trend_coefficients = np.polyfit(grouped_data.index, grouped_data['precio_medio'], deg=10)
#     trend_line = np.polyval(trend_coefficients, grouped_data.index)

#     # Create a Plotly figure with colored lines for different cities
#     fig = px.line(grouped_data, x='date', y='precio_medio', title=f'Evolution of price per product: {categoria.title()} in {ciudad.title()}')
#     fig.add_scatter(x=grouped_data['date'], y=trend_line, name='Trend Line', line=dict(dash='dash'))

#     # Customize the layout
#     fig.update_xaxes(title='Year', tickangle=30)
#     fig.update_yaxes(title='Average Price (in COP)')
#     fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
#                       margin=dict(l=20, r=20, t=40, b=20),
#                       plot_bgcolor='white', paper_bgcolor='black')

#     # Display the Plotly figure in Streamlit
#     st.plotly_chart(fig)

#     return None;


def product_city_evolution(dataframe: pd.DataFrame, 
                             producto: str, 
                             ciudad: str):
    # Filter and preprocess data
    filtered_data = dataframe[(dataframe['producto'] == producto) & (dataframe['ciudad'] == ciudad)]
    grouped_data = filtered_data[['anho', 'semana_no', 'ciudad','precio_medio']].groupby(['anho', 'semana_no', 'ciudad']).median().reset_index()
    grouped_data['date'] = pd.to_datetime(grouped_data['anho'].astype(str) + '-' + grouped_data['semana_no'].astype(str) + '-1', format='%Y-%U-%w')
    
    

    # Create a Plotly figure with colored lines for different cities
    fig = px.line(grouped_data, x='date', y='precio_medio', title=f'Evolution of price per product: {producto.title()} in {ciudad.title()}')
    try: 
        # Calculate the trend line using numpy's polyfit
        trend_coefficients = np.polyfit(grouped_data.index, grouped_data['precio_medio'], deg=10)
        trend_line = np.polyval(trend_coefficients, grouped_data.index)
        fig.add_scatter(x=grouped_data['date'], y=trend_line, name='Trend Line', line=dict(dash='dash'))
    
        
    # Customize the layout
        fig.update_xaxes(title='Year', tickangle=30)
        fig.update_yaxes(title='Average Price (in COP)')
        fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
                        margin=dict(l=20, r=20, t=40, b=20),
                        plot_bgcolor='white', paper_bgcolor='black')

        # Display the Plotly figure in Streamlit
        st.plotly_chart(fig)
    except: 
        print('Not enough data available')

    return None;



def product_region_evolution(dataframe: pd.DataFrame, 
                             producto: str, 
                             region: str):
    # Filter and preprocess data
    filtered_data = dataframe[(dataframe['producto'] == producto) & (dataframe['region'] == region)]
    grouped_data = filtered_data[['anho', 'semana_no', 'region','precio_medio']].groupby(['anho', 'semana_no', 'region']).median().reset_index()
    grouped_data['date'] = pd.to_datetime(grouped_data['anho'].astype(str) + '-' + grouped_data['semana_no'].astype(str) + '-1', format='%Y-%U-%w')
    
    

    # Create a Plotly figure with colored lines for different cities
    fig = px.line(grouped_data, x='date', y='precio_medio', title=f'Evolution of price per product: {producto.title()} in {region.title()}')
    try: 
        # Calculate the trend line using numpy's polyfit
        trend_coefficients = np.polyfit(grouped_data.index, grouped_data['precio_medio'], deg=10)
        trend_line = np.polyval(trend_coefficients, grouped_data.index)
        fig.add_scatter(x=grouped_data['date'], y=trend_line, name='Trend Line', line=dict(dash='dash'))
    
        
    # Customize the layout
        fig.update_xaxes(title='Year', tickangle=30)
        fig.update_yaxes(title='Average Price (in COP)')
        fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
                        margin=dict(l=20, r=20, t=40, b=20),
                        plot_bgcolor='white', paper_bgcolor='black')

        # Display the Plotly figure in Streamlit
        st.plotly_chart(fig)
    except: 
        print('Not enough data available')

    return None;



def all_category_evolution_city(dataframe: pd.DataFrame, ciudad: str):
    # Filter and preprocess data
    dataframe = dataframe[dataframe['ciudad'] == ciudad.lower()]
    dataframe = dataframe[['categoria','anho', 'semana_no', 'precio_medio']].groupby(['categoria','anho', 'semana_no']).median().reset_index()
    dataframe['date'] = pd.to_datetime(dataframe['anho'].astype(str) + '-' + dataframe['semana_no'].astype(str) + '-1', format='%Y-%U-%w')
    
    # Create a Plotly figure
    fig = px.line(dataframe, x='date', y='precio_medio', color='categoria')

    # Customize the layout
    fig.update_xaxes(title='Year', tickangle=30)
    fig.update_yaxes(title='Average Price (in COP)')
    fig.update_layout(
        legend=dict(
            orientation='h',  # Horizontal legend
            yanchor='bottom',  # Anchor at the bottom of the plot
            y=1.02,  # Move legend slightly above the plot
            xanchor='left',
            x=0.01
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='white', paper_bgcolor='black'
    )

    # Display the Plotly figure in Streamlit
    st.plotly_chart(fig)

    return None


def all_category_evolution_region(dataframe: pd.DataFrame, region: str):
    # Filter and preprocess data
    dataframe = dataframe[dataframe['region'] == region.lower()]
    dataframe = dataframe[['categoria','anho', 'semana_no', 'precio_medio']].groupby(['categoria','anho', 'semana_no']).median().reset_index()
    dataframe['date'] = pd.to_datetime(dataframe['anho'].astype(str) + '-' + dataframe['semana_no'].astype(str) + '-1', format='%Y-%U-%w')
    
    # Create a Plotly figure
    fig = px.line(dataframe, x='date', y='precio_medio', color='categoria')

    # Customize the layout
    fig.update_xaxes(title='Year', tickangle=30)
    fig.update_yaxes(title='Average Price (in COP)')
    fig.update_layout(
        legend=dict(
            orientation='h',  # Horizontal legend
            yanchor='bottom',  # Anchor at the bottom of the plot
            y=1.02,  # Move legend slightly above the plot
            xanchor='left',
            x=0.01
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='white', paper_bgcolor='black'
    )

    # Display the Plotly figure in Streamlit
    st.plotly_chart(fig)

    return None