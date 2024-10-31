from app_utils import aws
from typing import List, Union
import pandas as pd
run = aws.AppDataManager()

def city_composition_query(): 
	query = f"""
	SELECT 
    ciudad AS city, 
    anho AS year,
    COUNT(*) AS num_records
FROM product_prices
GROUP BY city, year
ORDER BY num_records;
	"""
	dataframe = run.queries_on_rds(query)
	return dataframe 

def category_composition_query(): 
	query = f"""
	SELECT 
    english_category as category, 
    anho AS year,
    COUNT(*) AS num_records
FROM product_prices pp
LEFT JOIN category_names pn ON pp.categoria = pn.spanish_category
GROUP BY category, year
ORDER BY num_records;
	"""
	dataframe = run.queries_on_rds(query)
	return dataframe 



def price_category_query(city:str): 
	query = f"""
	SELECT 
		AVG(precio_medio) as mean_price,
		english_category as category,
		date_trunc('year', to_date(anho::text, 'YYYY')) + interval '1 week' * (semana_no - 1) as date
	FROM product_prices pp
	LEFT JOIN product_names pn ON pp.producto = pn.spanish_product
	LEFT JOIN category_names cn ON pp.categoria = cn.spanish_category
	WHERE ciudad = '{city}'
	GROUP BY english_category, date
	ORDER BY date;
	"""
	dataframe = run.queries_on_rds(query)
	return dataframe 
	
def nation_wide_trend():
	query = f"""
	SELECT 
		AVG(precio_medio) as mean_price,
		english_category as category,
		date_trunc('year', to_date(anho::text, 'YYYY')) + interval '1 week' * (semana_no - 1) as date
	FROM product_prices pp
	LEFT JOIN product_names pn ON pp.producto = pn.spanish_product
	LEFT JOIN category_names cn ON pp.categoria = cn.spanish_category
	-- WHERE ciudad = 'bogota'
	GROUP BY english_category, date
	ORDER BY date;
	"""
	dataframe = run.queries_on_rds(query)
	return dataframe


def product_evolution_query(product:str):
	query = f"""
	SELECT 
    pn.english_product AS product,
    AVG(pp.precio_medio) AS avg_price,
    pp.anho AS year,
    pp.semana_no AS week,
    date_trunc('year', to_date(pp.anho::text, 'YYYY')) + interval '1 week' * (pp.semana_no - 1) AS date
FROM product_prices pp
LEFT JOIN product_names pn ON pp.producto = pn.spanish_product
WHERE pn.english_product = '{product}'
GROUP BY pn.english_product, pp.anho, pp.semana_no
ORDER BY pn.english_product, pp.anho, pp.semana_no;
	"""
	dataframe = run.queries_on_rds(query)
	return dataframe

def product_evolution_query_by_city(product:str, cities: Union[str, List[str]]):
		
    # If `cities` is a single string, convert it into a list
    if isinstance(cities, str):
        cities = [cities]
	
    cities = "','".join(cities)

    query = f"""
	SELECT 
    pn.english_product AS product,
    AVG(pp.precio_medio) AS avg_price,
    pp.anho AS year,
	pp.ciudad as city,
    pp.semana_no AS week,
    date_trunc('year', to_date(pp.anho::text, 'YYYY')) + interval '1 week' * (pp.semana_no - 1) AS date
FROM product_prices pp
LEFT JOIN product_names pn ON pp.producto = pn.spanish_product
WHERE pn.english_product = '{product}'
AND ciudad IN ('{cities}')
GROUP BY pp.ciudad, pn.english_product, pp.anho, pp.semana_no
ORDER BY pn.english_product, pp.anho, pp.semana_no;
	"""
    dataframe = run.queries_on_rds(query)
    return dataframe

def product_price_evolution(product:str):
	
	query = f"""
SELECT 
    pn.english_product AS product,
    pp.ciudad AS city,
    AVG(pp.precio_medio) AS avg_price,
    date_trunc('year', to_date(pp.anho::text, 'YYYY')) + interval '1 week' * (pp.semana_no - 1) AS date
FROM product_prices pp
LEFT JOIN product_names pn ON pp.producto = pn.spanish_product
WHERE pn.english_product = '{product}'
GROUP BY pn.english_product, pp.ciudad, pp.anho, pp.semana_no
ORDER BY pn.english_product, pp.ciudad, pp.anho, pp.semana_no;

	"""
	dataframe = run.queries_on_rds(query)
	return dataframe

def marketplaces_dynamics_query(): 
	query = """
WITH category_avg AS (
    SELECT 
        cn.english_category AS category,
        AVG(pp.precio_medio) AS national_avg_price,
        pp.anho AS year,
        pp.semana_no AS week,
        date_trunc('year', to_date(anho::text, 'YYYY')) + interval '1 week' * (semana_no - 1) AS date
    FROM product_prices pp
    LEFT JOIN category_names cn ON pp.categoria = cn.spanish_category
    GROUP BY cn.english_category, pp.anho, pp.semana_no
)
SELECT 
    cn.english_category AS category,
    pp.mercado,
    AVG(pp.precio_medio) AS avg_price,
    ca.national_avg_price,
    pp.anho AS year,
    pp.semana_no AS week,
    date_trunc('year', to_date(anho::text, 'YYYY')) + interval '1 week' * (semana_no - 1) AS date
FROM product_prices pp
LEFT JOIN category_names cn ON pp.categoria = cn.spanish_category
JOIN category_avg ca ON cn.english_category = ca.category AND pp.anho = ca.year AND pp.semana_no = ca.week
GROUP BY cn.english_category, pp.mercado, ca.national_avg_price, pp.anho, pp.semana_no
ORDER BY cn.english_category, pp.mercado, pp.anho, pp.semana_no;
	"""
	dataframe = run.queries_on_rds(query)
	return dataframe


def marketplaces_product_dynamics_query(product:str): 
	query = f"""
WITH product_avg AS (
    SELECT 
        cn.english_product AS product,
        AVG(pp.precio_medio) AS national_avg_price,
        pp.anho AS year,
        pp.semana_no AS week,
        date_trunc('year', to_date(anho::text, 'YYYY')) + interval '1 week' * (semana_no - 1) AS date
    FROM product_prices pp
    LEFT JOIN product_names cn ON pp.producto = cn.spanish_product
	WHERE cn.english_product = '{product}'
    GROUP BY cn.english_product, pp.anho, pp.semana_no
)
SELECT 
    cn.english_product AS product,
    pp.mercado,
    AVG(pp.precio_medio) AS avg_price,
    ca.national_avg_price,
    pp.anho AS year,
    pp.semana_no AS week,
    date_trunc('year', to_date(anho::text, 'YYYY')) + interval '1 week' * (semana_no - 1) AS date
FROM product_prices pp
LEFT JOIN product_names cn ON pp.producto = cn.spanish_product
JOIN product_avg ca ON cn.english_product = ca.product AND pp.anho = ca.year AND pp.semana_no = ca.week
GROUP BY cn.english_product, pp.mercado, ca.national_avg_price, pp.anho, pp.semana_no
ORDER BY cn.english_product, pp.mercado, pp.anho, pp.semana_no;
	"""
	dataframe = run.queries_on_rds(query)
	return dataframe


def product_query():
	query = """
	SELECT DISTINCT english_product as product
	FROM product_names;
	"""
	dataframe = run.queries_on_rds(query)
	return dataframe

def product_query_by_city(cities: Union[str, List[str]]):
    """
    Queries the distinct products available in the given cities.

    Args:
        cities (Union[str, List[str]]): A single city as a string or a list of city names.

    Returns:
        pd.DataFrame: A DataFrame containing the distinct products available in the specified city/cities.
    """
    # If `cities` is a single string, convert it into a list
    if isinstance(cities, str):
        cities = [cities]

    # Join the list of cities into a single string for the SQL query
    cities = "','".join(cities)
    
    query = f"""
    SELECT DISTINCT english_product as product
    FROM product_prices pp
    LEFT JOIN product_names pn ON pp.producto = pn.spanish_product
    WHERE ciudad IN ('{cities}');
    """
    
    dataframe = run.queries_on_rds(query)
    return dataframe





def city_query():
    query = """
    SELECT DISTINCT ciudad
    FROM product_prices;
    """
    dataframe = run.queries_on_rds(query)
    return dataframe


