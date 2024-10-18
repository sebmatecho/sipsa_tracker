import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import pandas as pd
from io import BytesIO

def lineplot_per_category(dataframe: pd.DataFrame,
                          numerical_value: str, 
                          categorical_value: str,
                          city:str,
                          date_column: str = 'date',
                          frac: float = 0.2,
                          xlabel: str = 'Date',
                          ylabel: str = 'Smoothed Value',
                          title: str = None) -> None:
    """
    Creates a line plot with LOWESS smoothing for each category in the dataset,
    and allows the user to download the resulting plot.
    
    Args:
        dataframe (pd.DataFrame): The data to plot.
        numerical_value (str): The name of the numerical column to plot.
        categorical_value (str): The name of the categorical column for grouping.
        date_column (str): The name of the date column. Default is 'date'.
        frac (float): Smoothing parameter for LOWESS. Default is 0.2.
        xlabel (str): Label for the x-axis. Default is 'Date'.
        ylabel (str): Label for the y-axis. Default is 'Smoothed Value'.
        title (str): Custom title for the plot. Default is generated based on inputs.
    """
    
    # Check if necessary columns exist in the dataframe
    if not all(col in dataframe.columns for col in [numerical_value, categorical_value, date_column]):
        raise ValueError("One or more columns are missing in the provided dataframe.")
    
    # Set up the color palette based on the number of unique categories
    n_categories = dataframe[categorical_value].nunique()
    custom_palette = sns.color_palette("Paired", n_colors=n_categories)
    
    # Set up the figure size and style
    fig, ax = plt.subplots(figsize=(10, 6))

    fig.set_facecolor('#f5f5f5')  # Set figure background color (light gray)
    sns.set(style="dark", palette=custom_palette)
    
    # Plot each category with LOWESS smoothing
    for i, category in enumerate(dataframe[categorical_value].unique()):
        subset = dataframe[dataframe[categorical_value] == category]
        smoothed_values = sm.nonparametric.lowess(subset[numerical_value], subset[date_column], frac=frac)
        ax.plot(subset[date_column], smoothed_values[:, 1], label=category, color=custom_palette[i])
    
    # Add plot title and labels
    if not title:
        title = f'Lowess Smoothed Average {numerical_value} by {categorical_value} Over Time'
    ax.set_title(title, fontsize=14)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    
    # Set axis background color
    ax.set_facecolor('#eaeaf2')
    
    # Customize legend
    ax.legend(title=categorical_value.capitalize(), loc='upper left', bbox_to_anchor=(1, 1))
    
    # Display the plot with tight layout using Streamlit
    plt.tight_layout()
    st.pyplot(fig)

    # Save the plot to a BytesIO buffer
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)

    # Provide a download button for the plot
    st.download_button(
        label="Download Plot as PNG",
        data=buf,
        file_name=f"lineplot_per_category_{city}.png",
        mime="image/png"
    )
