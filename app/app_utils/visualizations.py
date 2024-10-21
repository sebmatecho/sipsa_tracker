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

def city_composition_visualization(dataframe: pd.DataFrame):
    """
    Visualizes the number of records per year for each city using a stacked bar chart. The function sorts cities by the total count of records, 
    replaces city names to Title case for better readability, and allows the user to download the resulting plot.
    
    Args:
        dataframe (pd.DataFrame): A DataFrame with the following columns:
            - 'city': City name in snake_case format.
            - 'year': Year of the records.
            - 'num_records': Number of records for each city per year.
    
    The function sorts cities by the total count of records in descending order, converts city names from snake_case to Title case, 
    creates a stacked bar chart to represent the number of records per year for each city, and displays the plot in Streamlit. 
    The user can also download the plot as a PNG image.
    """
    # Calculate total records per city for sorting purposes
    city_totals = dataframe.groupby('city')['num_records'].sum().sort_values(ascending=False)

    # Convert city names to Title case for better readability
    dataframe['city'] = dataframe['city'].str.replace('_', ' ').str.title()

    # Re-order the cities in the dataframe according to total record counts in descending order
    sorted_cities = city_totals.index.str.replace('_', ' ').str.title()
    dataframe['city'] = pd.Categorical(dataframe['city'], categories=sorted_cities, ordered=True)
    df_sorted = dataframe.sort_values('city')

    # Pivot the DataFrame for better visualization - Grouped by city and years as values
    df_pivot = df_sorted.pivot(index='city', columns='year', values='num_records').fillna(0)

    # Set up the figure size and style
    plt.figure(figsize=(16, 10))
    sns.set(style="whitegrid")

    # Plot the data
    ax = df_pivot.plot(kind='bar', stacked=True, figsize=(16, 10), colormap="tab20")

    # Add titles and labels
    plt.title('Number of Records per Year and per City (Sorted by Total Count)', fontsize=20)
    plt.xlabel('City', fontsize=16)
    plt.ylabel('Number of Records', fontsize=16)
    plt.xticks(rotation=90, ha='right', fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(title="Year", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)

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
        file_name="number_of_records_per_year_and_city.png",
        mime="image/png"
    )

def category_composition_visualization(dataframe: pd.DataFrame):
    """
    Visualizes the number of records per year for each category using a stacked bar chart. The function sorts cities by the total count of records, 
    replaces category names to Title case for better readability, and allows the user to download the resulting plot.
    
    Args:
        dataframe (pd.DataFrame): A DataFrame with the following columns:
            - 'category': category.
            - 'year': Year of the records.
            - 'num_records': Number of records for each category per year.
    
    The function sorts cities by the total count of records in descending order, converts category names from snake_case to Title case, 
    creates a stacked bar chart to represent the number of records per year for each category, and displays the plot in Streamlit. 
    The user can also download the plot as a PNG image.
    """
    # Calculate total records per category for sorting purposes
    category_totals = dataframe.groupby('category')['num_records'].sum().sort_values(ascending=False)

    # Convert category names to Title case for better readability
    dataframe['category'] = dataframe['category'].str.replace('_', ' ').str.title()

    # Re-order the cities in the dataframe according to total record counts in descending order
    sorted_cities = category_totals.index.str.replace('_', ' ').str.title()
    dataframe['category'] = pd.Categorical(dataframe['category'], categories=sorted_cities, ordered=True)
    df_sorted = dataframe.sort_values('category')

    # Pivot the DataFrame for better visualization - Grouped by category and years as values
    df_pivot = df_sorted.pivot(index='category', columns='year', values='num_records').fillna(0)

    # Set up the figure size and style
    plt.figure(figsize=(16, 10))
    sns.set(style="whitegrid")

    # Plot the data
    ax = df_pivot.plot(kind='bar', stacked=True, figsize=(16, 10), colormap="tab20")

    # Add titles and labels
    plt.title('Number of Records per Year and per category (Sorted by Total Count)', fontsize=20)
    plt.xlabel('category', fontsize=16)
    plt.ylabel('Number of Records', fontsize=16)
    plt.xticks(rotation=90, ha='right', fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(title="Year", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)

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
        file_name="number_of_records_per_year_and_category.png",
        mime="image/png"
    )


def lineplot_per_category_nationwide(dataframe: pd.DataFrame,
                                     numerical_value: str, 
                                     categorical_value: str,
                                     date_column: str = 'date',
                                     frac: float = 0.2,
                                     xlabel: str = 'Date',
                                     ylabel: str = 'Average Price',
                                     title: str = None) -> None:
    """
    Creates a line plot with LOWESS smoothing for each category in the dataset,
    includes shaded areas indicating different presidencies, and adds separate boxes for major events and category legends.
    
    Args:
        dataframe (pd.DataFrame): The data to plot.
        numerical_value (str): The name of the numerical column to plot.
        categorical_value (str): The name of the categorical column for grouping.
        date_column (str): The name of the date column. Default is 'date'.
        frac (float): Smoothing parameter for LOWESS. Default is 0.2.
        xlabel (str): Label for the x-axis. Default is 'Date'.
        ylabel (str): Label for the y-axis. Default is 'Average Price'.
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
    fig, ax = plt.subplots(figsize=(10, 8))

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
        title = f'Price Evolution by Category (Nationwide)'
    ax.set_title(title, fontsize=20, weight='bold')  # Larger title
    ax.set_xlabel(xlabel, fontsize=16)  # Larger x-axis label
    ax.set_ylabel(ylabel, fontsize=16)  # Larger y-axis label
    
    # Set axis background color
    ax.set_facecolor('#eaeaf2')
    
    # Set y-axis limit to ensure uniform comparison
    ax.set_ylim(0, 28000)
    
    # Increase the font size for the ticks
    ax.tick_params(axis='both', labelsize=14)

    # Adding shaded areas for presidential terms
    presidential_periods = [
        ('2012-01-01', '2014-08-07', '#d3d3d3', 'Santos I'),  # Light gray
        ('2014-08-07', '2018-08-07', '#b0c4de', 'Santos II'),  # Light steel blue
        ('2018-08-07', '2022-08-07', '#add8e6', 'Duque'),      # Light blue
        ('2022-08-07', '2024-12-31', '#87cefa', 'Petro')       # Sky blue
    ]

    for start, end, color, label in presidential_periods:
        ax.axvspan(pd.to_datetime(start), pd.to_datetime(end), color=color, alpha=0.2)
        # Place the president names in the shaded areas with larger text
        ax.text(
            pd.to_datetime(start) + (pd.to_datetime(end) - pd.to_datetime(start)) / 2,
            ax.get_ylim()[1] * 0.9,  # Place at 90% of the y-axis height
            label,
            ha='center', fontsize=16, color='black', weight='bold'
        )
    
    # Adding vertical lines for major events with different colors
    events = [
        ('2013-08-19', 'National Strike (19 days)', '#d62728'),  # Red for strikes
        ('2016-05-30', 'National Strike (13 days)', '#d62728'),  # Red for strikes
        ('2016-11-24', 'Peace Deal with FARC', '#2ca02c'),  # Green for Peace Deal
        ('2019-11-20', 'National Strike (14 days)', '#d62728'),  # Red for strikes
        ('2020-03-01', 'COVID-19', '#1f77b4'),         # Blue for COVID-19
        ('2021-04-28', 'National Strike (48 days)', '#d62728'),  # Red for strikes
        ('2024-09-01', 'National Strike (6 days)', '#d62728'),  # Red for the recent strike during Petro's term
    ]

    event_legend_labels = []
    for event_date, event_label, color in events:
        ax.axvline(pd.to_datetime(event_date), color=color, linestyle='--', linewidth=2)
        event_legend_labels.append((plt.Line2D([], [], color=color, linestyle='--', linewidth=2), event_label))

    # Adding both legends in the right pane without overlapping the plot
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.75, box.height])  # Adjust plot size to fit legends

    category_legend = plt.legend(title="Category", handles=ax.get_legend_handles_labels()[0], loc='center left', bbox_to_anchor=(1.02, 0.8), fontsize=12, title_fontsize=14)
    ax.add_artist(category_legend)  # Add category legend to the figure

    plt.legend(*zip(*event_legend_labels), loc='center left', bbox_to_anchor=(1.02, 0.5), title="Major Events", fontsize=12, title_fontsize=14)

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
        file_name=f"lineplot_per_category.png",
        mime="image/png"
    )



