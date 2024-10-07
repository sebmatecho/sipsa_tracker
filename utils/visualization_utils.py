import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import pandas as pd

def lineplot_per_category(dataframe: pd.DataFrame,
                          numerical_value: str, 
                          categorical_value: str,
                          date_column: str = 'date',
                          frac: float = 0.2,
                          xlabel: str = 'Date',
                          ylabel: str = 'Smoothed Value',
                          title: str = None) -> None:
    """
    Creates a line plot with LOWESS smoothing for each category in the dataset.
    
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
    plt.figure(figsize=(10, 6))

    plt.gcf().set_facecolor('#f5f5f5')  # Set figure background color (light gray)
    sns.set(style="dark", palette=custom_palette)
    
    # Plot each category with LOWESS smoothing
    for i, category in enumerate(dataframe[categorical_value].unique()):
        subset = dataframe[dataframe[categorical_value] == category]
        smoothed_values = sm.nonparametric.lowess(subset[numerical_value], subset[date_column], frac=frac)
        plt.plot(subset[date_column], smoothed_values[:, 1], label=category, color=custom_palette[i])
    
    # Add plot title and labels
    if not title:
        title = f'Lowess Smoothed Average {numerical_value} by {categorical_value} Over Time'
    plt.title(title, fontsize=14)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    
    # Set axis background color
    plt.gca().set_facecolor('#eaeaf2')
    
    # Customize legend
    plt.legend(title=categorical_value.capitalize(), loc='upper left', bbox_to_anchor=(1, 1))
    
    # Display the plot with tight layout
    plt.tight_layout()
    plt.show()



def lineplot_per_category_grid(dataframe: pd.DataFrame, 
                          numerical_value: str, 
                          categorical_value: str, 
                          ax,  # Axis argument for each subplot
                          title: str = None, 
                          xlabel: str = None, 
                          ylabel: str = None, 
                          frac: float = 0.2,
                          show_legend: bool = True):  # Add show_legend parameter
    """
    Plot a LOWESS-smoothed lineplot per category on the given axis with consistent colors.
    
    Args:
        dataframe (pd.DataFrame): Data to plot.
        numerical_value (str): Column with numerical values (e.g., 'mean_price').
        categorical_value (str): Column with categorical values (e.g., 'category').
        ax (matplotlib.axes._subplots.AxesSubplot): Axis to plot on.
        title (str): Title of the plot.
        xlabel (str): Label for the x-axis.
        ylabel (str): Label for the y-axis.
        frac (float): Fraction for LOWESS smoothing (default is 0.2).
        show_legend (bool): Whether or not to display the legend (default is True).
    """
    # Get the unique categories and set a fixed color palette
    categories = dataframe[categorical_value].unique()
    custom_palette = sns.color_palette("Paired", n_colors=len(categories))
    palette_dict = {category: custom_palette[i] for i, category in enumerate(categories)}
    
    # Plot each category with LOWESS smoothing
    for category in categories:
        subset = dataframe[dataframe[categorical_value] == category]
        if not subset.empty:
            smoothed_values = sm.nonparametric.lowess(subset[numerical_value], subset['date'], frac=frac)
            ax.plot(subset['date'], smoothed_values[:, 1], label=category, color=palette_dict[category])
    
    # Add title and labels
    if title:
        ax.set_title(title, fontsize=12)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)
    
    # Set axis background color
    ax.set_facecolor('#eaeaf2')
    
    # Add legend only if show_legend is True
    if show_legend:
        ax.legend(title=categorical_value.capitalize(), loc='upper left', bbox_to_anchor=(1, 1))
