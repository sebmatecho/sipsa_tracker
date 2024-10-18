import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import pandas as pd
from io import BytesIO

def lineplot_per_category(dataframe: pd.DataFrame,
                          numerical_value: str, 
                          categorical_value: str,
                          city: str,
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
    
    # Define a fixed order for categories and corresponding color palette
    category_order = [
        'eggs_dairy',
        'fish',
        'fresh_fruits',
        'grains_cereals',
        'meats',
        'processed_products',
        'tubers_roots_plantains',
        'vegetables'
    ]

    category_labels = {
        'eggs_dairy': 'Eggs & Dairy',
        'fish': 'Fish',
        'fresh_fruits': 'Fresh Fruits',
        'grains_cereals': 'Grains & Cereals',
        'meats': 'Meats',
        'processed_products': 'Processed Products',
        'tubers_roots_plantains': 'Tubers, Roots & Plantains',
        'vegetables': 'Vegetables'
    }

    # Fixed color palette matching the desired order
    fixed_palette = [
        '#AEC7E8',  # light blue for eggs_dairy
        '#1F77B4',  # blue for fish
        '#98DF8A',  # light green for fresh_fruits
        '#2CA02C',  # green for grains_cereals
        '#FF9896',  # light pink for meats
        '#D62728',  # red for processed_products
        '#FFBB78',  # light orange for tubers_roots_plantains
        '#FF7F0E'   # orange for vegetables
    ]

    # Check if necessary columns exist in the dataframe
    if not all(col in dataframe.columns for col in [numerical_value, categorical_value, date_column]):
        raise ValueError("One or more columns are missing in the provided dataframe.")
    
    # Replace category values in the DataFrame
    dataframe[categorical_value] = dataframe[categorical_value].replace(category_labels)
    
    # Set up the figure size and style
    fig, ax = plt.subplots(figsize=(12, 8))

    fig.set_facecolor('#f5f5f5')  # Set figure background color (light gray)
    sns.set(style="dark")
    
    # Plot each category in the defined order with LOWESS smoothing
    for i, category in enumerate(category_order):
        if category_labels[category] in dataframe[categorical_value].values:
            subset = dataframe[dataframe[categorical_value] == category_labels[category]]
            smoothed_values = sm.nonparametric.lowess(subset[numerical_value], subset[date_column], frac=frac)
            ax.plot(subset[date_column], smoothed_values[:, 1], label=category_labels[category], color=fixed_palette[i])
    
    # Add plot title and labels with larger font size
    if not title:
        title = f'Price Evolution by Category ({city.capitalize()})'
    ax.set_title(title, fontsize=20, weight='bold')  # Larger title
    ax.set_xlabel(xlabel, fontsize=16)  # Larger x-axis label
    ax.set_ylabel(ylabel, fontsize=16)  # Larger y-axis label
    
    # Set axis background color
    ax.set_facecolor('#eaeaf2')
    
    # Set y-axis limit to ensure uniform comparison
    ax.set_ylim(0, 35000)
    
    # Customize legend to use fixed order with larger font size
    ax.legend(title="Category", loc='upper left', bbox_to_anchor=(1, 1), fontsize=14, title_fontsize=16)
    
    # Increase the font size for the ticks
    ax.tick_params(axis='both', labelsize=14)
    
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
