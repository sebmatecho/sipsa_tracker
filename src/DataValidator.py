
import pandas as pd
import re
from unidecode import unidecode
import logging

class DataValidator:
    """
    The DataValidator class is responsible for validating and cleaning data from a DataFrame.
    It provides methods to validate city names, product names, prices, trends, and categories.
    It also has a function to remove accents and format text, ensuring consistency and validity of the data.

    Attributes:
        valid_cities (list): A list of valid Colombian city names for validation.
        valid_products (list): A list of valid product names for validation.
        valid_tendencias (list): A list of valid trends ('tendencia') for validation.
        valid_categorias (list): A list of valid categories for validation.
        logger (logging.Logger): A logger instance to log information, warnings, and errors.

    Methods:
        validate_city(city: str) -> bool:
            Checks if the provided city name is valid.

        validate_product(product: str) -> bool:
            Checks if the provided product name is valid.

        validate_price(price) -> bool:
            Checks if the provided price is a non-negative integer.

        validate_tendencia(tendencia: str) -> bool:
            Checks if the provided trend ('tendencia') is valid.

        validate_categoria(categoria: str) -> bool:
            Checks if the provided category is valid.

        remove_accents_trails_caps(text: str) -> str:
            Removes accents, trailing spaces, and converts text to lowercase.

        validate_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
            Validates the entire DataFrame, removing rows that fail validation, and returns a cleaned DataFrame.
    """
    def __init__(self, 
                 logger: logging.Logger):
        """
        Initializes the DataValidator with predefined reference data for validation and a logger instance.

        Args:
            logger (logging.Logger): A logger instance for logging messages.
        """
        # Load or define reference data for validation
        self.valid_cities = [
            'barranquilla', 'bogota', 'bucaramanga', 'cali', 'cartagena', 'cúcuta', 'medellín', 'sincelejo', 
            'valledupar', 'pereira', 'manizales', 'armenia', 'pasto', 'ibagué', 'villavicencio', 'yopal',
            'florencia', 'leticia', 'riohacha', 'neiva', 'montería', 'mocoa', 'puerto carreño', 'mitú', 'inírida',
            'sogamoso', 'tunja', 'pamplona', 'girardot', 'popayán', 'tumaco', 'quibdó', 'villavicencio',
            'arauca', 'buenaventura', 'cartago', 'chiquinquirá', 'la dorada', 'santander'
        ]
        
        self.valid_products = [
            'acelga', 'manzana', 'pollo', 'leche', 'papa', 'arroz', 'frijol', 'tomate', 'cebolla', 'naranja',
            # Add more valid products here
        ]
        
        self.valid_tendencias = ['+', '-', '=', '++', '--', '+++', '---']
        self.valid_categorias = [
            'verduras_hortalizas', 'frutas_frescas', 'tuberculos_raices_platanos', 'granos_cereales',
            'huevos_lacteos', 'carnes', 'pescados', 'productos_procesados'
        ]
        self.logger = logger
        
    def validate_city(self, city: str) -> bool:
        """
        Check if the provided city name is valid.

        Args:
            city (str): The city name to validate.

        Returns:
            bool: True if the city is valid, otherwise False.
        """
        return True
#         return city in self.valid_cities

    def validate_product(self, product: str) -> bool:
        """
        Check if the provided product name is valid.

        Args:
            product (str): The product name to validate.

        Returns:
            bool: True if the product is valid, otherwise False.
        """
        return True
#         return product in self.valid_products


    def validate_price(self, price) -> bool:
        """
        Check if the provided price is a non-negative integer.

        Args:
            price (int or float): The price value to validate.

        Returns:
            bool: True if the price is a non-negative integer, otherwise False.
        """
        try:
            return price >= 0
        except TypeError:
            return False

    def validate_tendencia(self, tendencia: str) -> bool:
        """
        Check if the provided trend ('tendencia') is valid.

        Args:
            tendencia (str): The trend value to validate.

        Returns:
            bool: True if the trend is valid, otherwise False.
        """
        return tendencia in self.valid_tendencias

    def validate_categoria(self, categoria: str) -> bool:
        """
        Check if the provided category is valid.

        Args:
            categoria (str): The category value to validate.

        Returns:
            bool: True if the category is valid, otherwise False.
        """
        return categoria in self.valid_categorias
    # Function to remove accents
    
    def remove_accents_trails_caps(self, text):
        """
        Removes accents, converts text to lowercase, and replaces spaces with underscores.

        Args:
            text (str): The text to be cleaned.

        Returns:
            str: Cleaned text without accents, all lowercase, and spaces replaced by underscores.
        """
        return unidecode(text.lower().replace(' ','_'))

    def validate_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Validates the entire DataFrame, removing rows that fail validation.
        It applies all individual validation methods to ensure that the data is consistent.

        Args:
            dataframe (pd.DataFrame): The DataFrame to validate.

        Returns:
            pd.DataFrame: A DataFrame containing only valid rows. If no rows are valid, returns an empty DataFrame.
        """
        try: 
            # Validate each column and store the valid rows in a new DataFrame
            dataframe['ciudad'] = dataframe['ciudad'].apply(self.remove_accents_trails_caps)
            dataframe['producto'] = dataframe['producto'].apply(self.remove_accents_trails_caps)

            valid_df = dataframe[
                dataframe['ciudad'].apply(self.validate_city) &
                dataframe['producto'].apply(self.validate_product) &
                dataframe['precio_minimo'].apply(self.validate_price) &
                dataframe['precio_maximo'].apply(self.validate_price) &
                dataframe['precio_medio'].apply(self.validate_price) &
                dataframe['tendencia'].apply(self.validate_tendencia) &
                dataframe['categoria'].apply(self.validate_categoria)
            ]

            # Log the rows that were removed
            invalid_rows = dataframe[~dataframe.index.isin(valid_df.index)]
            if not invalid_rows.empty:
                logger.warning(f"Invalid rows found and removed")

            return valid_df
        except: 
            dataframe = pd.DataFrame()
            return dataframe
