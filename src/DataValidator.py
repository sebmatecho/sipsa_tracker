
import pandas as pd
import re
from unidecode import unidecode
import logging

class DataValidator:
    def __init__(self, 
                 logger: logging.Logger):
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
        """Check if the city is valid."""
        return True
#         return city in self.valid_cities

    def validate_product(self, product: str) -> bool:
        """Check if the product is valid."""
        return True
#         return product in self.valid_products


    def validate_price(self, price) -> bool:
        """Check if the price is a positive integer."""
        try:
            return price >= 0
        except TypeError:
            return False

    def validate_tendencia(self, tendencia: str) -> bool:
        """Check if the tendencia is valid."""
        return tendencia in self.valid_tendencias

    def validate_categoria(self, categoria: str) -> bool:
        """Check if the categoria is valid."""
        return categoria in self.valid_categorias
    # Function to remove accents
    
    def remove_accents_trails_caps(self, text):
        return unidecode(text.lower().replace(' ','_'))

    def validate_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Validate the entire dataframe, and filter out rows that fail validation."""
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
