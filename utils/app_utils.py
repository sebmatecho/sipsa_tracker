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

def imputing_outliers(df_final, year, week):
	index = df_final[(df_final['year']==year)&(df_final['week']==week)].index[0]
	df_final.loc[index, 'sipsa'] = df_final.loc[index-5:index +5, 'sipsa'].median()
	return df_final


def sipsa_index(dataframe: pd.DataFrame): 

    index_weights =  {'verduras_hortalizas':0.094,
                        'frutas_frescas':0.050,
                        'tuberculos_raices_platanos':0.041,
                        'granos_cereales':0.186,
                        'huevos_lacteos':0.214,
                        'carnes':0.237,
                        'pescados':0.030, 
                        'productos_procesados':0.148}
    
    year_list, week_list, sipsa_index_list = [],[],[]

    # Filter the DataFrame for the desired year and week
    for year in dataframe['anho'].unique():
        
        for week in dataframe.loc[dataframe['anho']==year,'semana_no'].unique():
            
            df_filtered = dataframe[(dataframe['anho'] == year) & (dataframe['semana_no'] == week)]
            # Calculate the weighted sum for each category
            year_list.append(year)
            week_list.append(week)
            sipsa_index_list.append((df_filtered['precio_medio'] * df_filtered['categoria'].map(index_weights)).sum())

    df_final = pd.DataFrame({'year':year_list, 
                            'week': week_list, 
                            'sipsa': sipsa_index_list})
    df_final = df_final.sort_values(['year','week']).reset_index(drop=True)

    # outlier treatment - imputation
    df_final = imputing_outliers(df_final, year = 2016, week = 12)
    df_final = imputing_outliers(df_final, year = 2020, week = 18)
    df_final = imputing_outliers(df_final, year = 2021, week = 18)
    df_final = imputing_outliers(df_final, year = 2021, week = 19)
    df_final = imputing_outliers(df_final, year = 2021, week = 20)
    df_final = imputing_outliers(df_final, year = 2021, week = 48)
    df_final = imputing_outliers(df_final, year = 2021, week = 49)
    df_final = imputing_outliers(df_final, year = 2021, week = 50)

    df_final['date'] = pd.to_datetime(df_final['year'].astype(str) + '-' + df_final['week'].astype(str) + '-1', format='%Y-%U-%w')
    
    
    # fig = px.line(df_final.sort_values('date'), x='date', y='sipsa')
    #######
    df_final['month'] = df_final['date'].dt.month
    df_final = df_final[['sipsa','year', 'month']].groupby(['year','month']).median().reset_index()
    
    # Calculate the percentual difference
    df_final['date'] = pd.to_datetime(df_final['year'].astype(str) + '-' + df_final['month'].astype(str), format='%Y-%m')
    df_final["sipsa_index_percentual"] = df_final["sipsa"].pct_change() * 100
    fig = px.line(df_final.sort_values('date'), x='date', y='sipsa_index_percentual')
    
    # Display the Plotly figure in Streamlit
    st.plotly_chart(fig)
    # st.dataframe(df_final.sort_values('date'))
    return None;


