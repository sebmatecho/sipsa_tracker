
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
            'bogota', 'bucaramanga', 'cali', 'cartagena', 'duitama', 'ibague',
       'ipiales', 'medellin', 'neiva', 'pamplona', 'pasto', 'sogamoso',
       'tunja', 'villavicencio', 'barranquilla', 'buenaventura',
       'cartago', 'cucuta', 'manizales', 'monteria', 'palmira', 'pereira',
       'popayan', 'rionegro', 'san_gil', 'sincelejo', 'socorro', 'tulua',
       'valledupar', 'chiquinquira', 'marinilla', 'cajamarca',
       'carmen_de_viboral', 'el_santuario', 'la_ceja', 'san_vicente',
       'sonson', 'armenia', 'penol', 'santa_barbara', 'yarumal',
       'la_virginia', 'la_union', 'la_parada', 'la_dorada', 'charala',
       'guepsa', 'moniquira', 'puente_nacional', 'santana', 'velez',
       'caparrapi', 'nocaima', 'villeta', 'honda', 'ubate',
       'cartagena', 'yolombo',
       'yopal', 'malambo', 'el_carmen_de_viboral', 'santa_marta',
       'florencia', 'tuquerres', 'san_andres_de_tumaco', 'arauca',
       'consaca', 'sandona', 'ancuya', 'tibasosa',
       'san_sebastian_de_mariquita', 'san_vicente_ferrer'
        ]
        
        self.valid_products = [
            'acelga', 'ahuyama', 'ajo', 'ajo_importado', 'aji_dulce',
       'aji_topito_dulce', 'apio', 'arveja_verde_en_vaina',
       'arveja_verde_en_vaina_pastusa', 'berenjena', 'brocoli',
       'calabacin', 'calabaza', 'cebolla_cabezona_blanca',
       'cebolla_cabezona_blanca_bogotana',
       'cebolla_cabezona_blanca_importada',
       'cebolla_cabezona_blanca_pastusa',
       'cebolla_cabezona_blanca_peruana',
       'cebolla_cabezona_roja_importada', 'cebolla_cabezona_roja_ocanera',
       'cebolla_cabezona_roja_peruana', 'cebolla_junca',
       'cebolla_junca_aquitania', 'cebolla_junca_berlin',
       'cebolla_junca_tenerife', 'cebolla_junca_pastusa',
       'cebolla_puerro', 'cebollin_chino', 'chocolo_mazorca', 'cidra',
       'cilantro', 'coles', 'coliflor', 'espinaca', 'frijol_verde_bolo',
       'frijol_verde_cargamanto', 'frijol_verde_en_vaina', 'haba_verde',
       'habichuela', 'habichuela_larga', 'lechuga_batavia',
       'lechuga_crespa_morada', 'lechuga_crespa_verde', 'pepino_cohombro',
       'pepino_de_rellenar', 'perejil', 'pimenton', 'pimenton_verde',
       'remolacha', 'remolacha_bogotana', 'remolacha_regional',
       'repollo_blanco', 'repollo_blanco_bogotano',
       'repollo_blanco_valluno', 'repollo_morado',
       'repollo_verde_regional', 'rabano_rojo', 'tomate_riogrande',
       'tomate_riogrande_bumangues', 'tomate_riogrande_ocanero',
       'tomate_chonto', 'tomate_chonto_antioqueno',
       'tomate_chonto_valluno', 'tomate_larga_vida', 'tomate_rinon',
       'zanahoria', 'zanahoria_bogotana', 'zanahoria_larga_vida',
       'aguacate_hass', 'aguacate_comun', 'aguacate_papelillo', 'badea',
       'banano_uraba', 'banano_bocadillo', 'banano_criollo', 'borojo',
       'breva', 'ciruela_negra_chilena', 'ciruela_roja', 'coco',
       'curuba_larga', 'curuba_redonda', 'durazno_importado',
       'durazno_nacional', 'feijoa', 'fresa', 'granadilla', 'guanabana',
       'guayaba_agria', 'guayaba_comun', 'guayaba_manzana',
       'guayaba_pera', 'higo', 'kiwi', 'limon_tahiti', 'limon_comun',
       'limon_comun_cienaga', 'limon_comun_valluno', 'limon_mandarino',
       'lulo', 'mandarina_oneco', 'mandarina_arrayana', 'mandarina_comun',
       'mango_tommy', 'mango_comun', 'mango_de_azucar', 'mango_manzano',
       'mango_reina', 'manzana_roja_importada',
       'manzana_royal_gala_importada', 'maracuya',
       'manzana_verde_importada', 'maracuya_antioqueno',
       'maracuya_santandereano', 'melon_cantalup', 'mora_de_castilla',
       'naranja_valencia', 'naranja_comun', 'papaya_maradol',
       'papaya_hawaiana', 'papaya_melona', 'papaya_redonda', 'patilla',
       'pera_importada', 'pitahaya', 'pina_gold', 'pina_manzana',
       'pina_perolera', 'tangelo', 'tomate_de_arbol',
       'uchuva_con_cascara', 'uva_isabela', 'uva_importada', 'uva_negra',
       'uva_red_globe_nacional', 'uva_roja', 'uva_verde', 'zapote',
       'arracacha_amarilla', 'arracacha_blanca', 'papa_ica-huila',
       'papa_morasurco', 'papa_purace', 'papa_r-12_negra',
       'papa_r-12_roja', 'papa_capira', 'papa_criolla_limpia',
       'papa_criolla_sucia', 'papa_nevada', 'papa_parda_pastusa',
       'papa_roja_peruana', 'papa_ruby', 'papa_sabanera', 'papa_suprema',
       'papa_unica', 'platano_comino', 'platano_dominico_harton_maduro',
       'platano_dominico_harton_verde', 'platano_dominico_verde',
       'platano_guineo', 'platano_harton_maduro', 'platano_harton_verde',
       'platano_harton_verde_llanero', 'ulluco', 'yuca_ica',
       'yuca_chirosa', 'yuca_criolla', 'yuca_llanera', 'name_criollo',
       'name_diamante', 'name_espino', 'arroz_de_primera',
       'arroz_de_segunda', 'arroz_excelso', 'arroz_sopa_cristal',
       'arveja_amarilla_seca_importada', 'arveja_enlatada',
       'arveja_verde_seca_importada', 'cuchuco_de_cebada',
       'cuchuco_de_maiz', 'frijol_uribe_rosado', 'frijol_zaragoza',
       'frijol_bolon', 'frijol_cabeza_negra_importado',
       'frijol_cabeza_negra_nacional', 'frijol_calima',
       'frijol_cargamanto_blanco', 'frijol_cargamanto_rojo',
       'frijol_enlatado', 'frijol_nima_calima',
       'frijol_palomito_importado', 'frijol_radical',
       'garbanzo_importado', 'lenteja_importada', 'maiz_amarillo_cascara',
       'maiz_amarillo_trillado', 'maiz_blanco_retrillado',
       'maiz_blanco_trillado', 'maiz_pira', 'huevo_blanco_a',
       'huevo_blanco_aa', 'huevo_blanco_b', 'huevo_blanco_extra',
       'huevo_rojo_a', 'huevo_rojo_aa', 'huevo_rojo_b',
       'huevo_rojo_extra', 'leche_en_polvo', 'queso_campesino',
       'queso_costeno', 'queso_cuajada', 'queso_doble_crema',
       'alas_de_pollo_con_costillar', 'alas_de_pollo_sin_costillar',
       'carne_de_cerdo_en_canal', 'carne_de_cerdo_brazo_con_hueso',
       'carne_de_cerdo_brazo_sin_hueso', 'carne_de_cerdo_cabeza_de_lomo',
       'carne_de_cerdo_costilla', 'carne_de_cerdo_espinazo',
       'carne_de_cerdo_lomo_con_hueso', 'carne_de_cerdo_lomo_sin_hueso',
       'carne_de_cerdo_pernil_con_hueso',
       'carne_de_cerdo_pernil_sin_hueso', 'carne_de_cerdo_tocino_barriga',
       'carne_de_cerdo_tocino_papada', 'carne_de_res_en_canal',
       'carne_de_res_molida_murillo', 'carne_de_res_bola_de_brazo',
       'carne_de_res_bola_de_pierna', 'carne_de_res_bota',
       'carne_de_res_cadera', 'carne_de_res_centro_de_pierna',
       'carne_de_res_chatas', 'carne_de_res_cogote',
       'carne_de_res_costilla', 'carne_de_res_falda',
       'carne_de_res_lomo_de_brazo', 'carne_de_res_lomo_fino',
       'carne_de_res_morrillo', 'carne_de_res_muchacho',
       'carne_de_res_murillo', 'carne_de_res_paletero',
       'carne_de_res_pecho', 'carne_de_res_punta_de_anca',
       'carne_de_res_sobrebarriga', 'menudencias_de_pollo',
       'muslos_de_pollo_sin_rabadilla', 'pechuga_de_pollo',
       'pierna_pernil_con_rabadilla', 'pierna_pernil_sin_rabadilla',
       'piernas_de_pollo', 'pollo_entero_congelado_sin_visceras',
       'pollo_entero_fresco_sin_visceras', 'rabadillas_de_pollo',
       'almejas_con_concha', 'almejas_sin_concha',
       'bagre_rayado_en_postas_congelado',
       'bagre_rayado_entero_congelado', 'bagre_rayado_entero_fresco',
       'blanquillo_entero_fresco', 'bocachico_criollo_fresco',
       'bocachico_importado_congelado', 'cachama_de_cultivo_fresca',
       'calamar_anillos', 'calamar_blanco_entero',
       'calamar_morado_entero', 'camaron_tigre_precocido_seco',
       'camaron_titi_precocido_seco', 'capaz_magdalena_fresco',
       'cazuela_de_mariscos_paquete', 'corvina_filete_congelado_nacional',
       'langostino_16-20', 'merluza_filete_importado',
       'merluza_filete_nacional', 'mojarra_lora_entera_congelada',
       'mojarra_lora_entera_fresca', 'nicuro_fresco', 'palmitos_de_mar',
       'pargo_rojo_entero_congelado', 'pargo_rojo_platero',
       'pescado_cabezas', 'robalo_filete_congelado',
       'salmon_filete_congelado', 'sierra_entera_congelada',
       'tilapia_roja_entera_congelada', 'margarina',
       'tilapia_roja_entera_fresca', 'tilapia_filete_congelado',
       'toyo_blanco_filete_congelado', 'trucha_en_corte_mariposa',
       'trucha_entera_fresca', 'aceite_girasol', 'aceite_vegetal_mezcla',
       'avena_en_hojuelas', 'avena_molida', 'azucar_morena',
       'azucar_refinada', 'azucar_sulfitada', 'bocadillo_veleno',
       'cafe_instantaneo', 'cafe_molido', 'chocolate_amargo',
       'chocolate_dulce', 'chocolate_instantaneo', 'color_bolsita',
       'fecula_de_maiz', 'galletas_dulces_redondas_con_crema',
       'galletas_saladas_3_tacos', 'gelatina', 'harina_de_trigo',
       'harina_precocida_de_maiz', 'jugo_de_frutas',
       'jugo_instantaneo_sobre', 'lomitos_de_atun_en_lata', 'manteca',
       'mayonesa_doy_pack', 'panela_cuadrada_blanca',
       'panela_cuadrada_morena', 'panela_redonda_morena',
       'pastas_alimenticias', 'sal_yodada', 'salsa_de_tomate_doy_pack',
       'sardinas_en_lata', 'vinagre', 'papa_parda_para_lavar',
       'maiz_blanco_cascara', 'pargo_rojo_entero_fresco',
       'papa_tocarrena', 'manzana_nacional', 'maracuya_valluno',
       'pera_nacional', 'maiz_enlatado', 'muslos_de_pollo_con_rabadilla',
       'langostino_u12', 'sopa_de_pollo_caja', 'cebolla_cabezona_roja',
       'platano_harton_verde_ecuatoriano', 'repollo_morado_antioqueno',
       'maracuya_huilense', 'limon_comun_ecuatoriano', 'mango_costeno',
       'pollo_entero_fresco_con_visceras',
       'carne_de_cerdo_tocineta_plancha', 'queso_caqueta',
       'pollo_entero_congelado_con_visceras', 'aceite_soya', 'papa_rubi',
       'papa_superior', 'naranja_sweet', 'papa_betina', 'curuba',
       'gulupa', 'ahuyamin_sakata', 'repollo_verde', 'patilla_baby',
       'tomate_rinon_valluno', 'tomate_chonto_regional',
       'ciruela_negra_importada', 'ciruela_roja_importada',
       'galletas_saladas', 'ciruela_importada', 'papaya_tainung',
       'mango_yulima', 'maiz_amarillo_cascara_importado',
       'panela_en_pastilla', 'guayaba_pera_valluna',
       'basa_filete_congelado_importado', 'mango_kent',
       'panela_redonda_blanca', 'guayaba_atlantico', 'papa_san_felix',
       'platano_harton_verde_eje_cafetero', 'arroz_blanco_importado',
       'tilapia_lomitos', 'mostaza_doy_pack', 'c',
       'basa_entero_congelado_importado', 'papaya_paulina',
       'aceite_de_palma'
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
        return city in self.valid_cities
        # return True

    
    def validate_product(self, product: str) -> bool:
        """
        Check if the provided product name is valid.

        Args:
            product (str): The product name to validate.

        Returns:
            bool: True if the product is valid, otherwise False.
        """
        return product in self.valid_products
        # return True

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
        return unidecode(text.lower().replace(' ','_').replace(',','').replace('(','').replace(')',''))

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
                self.logger.warning(f"Invalid rows found and removed: {invalid_rows.shape[0]}")

            return valid_df
        except: 
            dataframe = pd.DataFrame()
            return dataframe
