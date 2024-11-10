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

def affordability_category_by_city(category:str, 
								   city:str):
	query = f"""
WITH product_price AS (
    SELECT 
        pp.ciudad AS city, 
        pn.english_product AS product, 
        AVG(pp.precio_medio) AS avg_price, 
        pp.anho AS year, 
        date_trunc('year', to_date(pp.anho::text, 'YYYY')) + interval '1 week' * (pp.semana_no - 1) AS date
    FROM product_prices pp
    LEFT JOIN product_names pn ON pp.producto = pn.spanish_product
    LEFT JOIN category_names cn ON pp.categoria = cn.spanish_category
    WHERE cn.english_category = '{category}'
    AND pp.ciudad = '{city}'
    GROUP BY pp.ciudad, pn.english_product, pp.anho, pp.semana_no
),
income_data AS (
    SELECT city, year, AVG(monthly_income) AS avg_income
    FROM min_wages
    GROUP BY city, year
),
recent_data AS (
    -- Filter for records from the last 60 days
    SELECT *
    FROM product_price
    WHERE date >= CURRENT_DATE - INTERVAL '60 days'
),
affordability_data AS (
    SELECT 
        p.city, 
        p.product, 
        AVG(p.avg_price) AS avg_price,  -- Average price for each product over the last 60 days
        AVG(i.avg_income) AS avg_income,  -- Average income over the last 60 days (in case income varies)
        MAX(p.date) AS recent_date,  -- The most recent date for the product record
        (AVG(p.avg_price) / (AVG(i.avg_income) / 4)) * 100 AS affordability_index  -- Percentage of weekly income required to buy a unit
    FROM recent_data p
    JOIN income_data i 
        ON p.city = i.city AND p.year = i.year
    GROUP BY p.city, p.product
)
SELECT 
    city, 
    product, 
    avg_price, 
    avg_income, 
    recent_date, 
    affordability_index,
    RANK() OVER (PARTITION BY city ORDER BY affordability_index ASC) AS affordability_rank
FROM affordability_data
ORDER BY city, affordability_rank;
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


def major_price_changes_city_query(city:str,category:str= None):
    query = f"""
    WITH latest_two_weeks AS (
        SELECT 
            pp.ciudad AS city, 
            pn.english_product AS product, 
            pp.semana_no AS week, 
            pp.anho AS year, 
            AVG(pp.precio_medio) AS avg_price, 
            date_trunc('year', to_date(pp.anho::text, 'YYYY')) + interval '1 week' * (pp.semana_no - 1) AS date
        FROM product_prices pp
        LEFT JOIN product_names pn ON pp.producto = pn.spanish_product
		LEFT JOIN category_names cn ON pp.categoria = cn.spanish_category
        WHERE date_trunc('year', to_date(pp.anho::text, 'YYYY')) + interval '1 week' * (pp.semana_no - 1) >= (
            SELECT MAX(date_trunc('year', to_date(pp.anho::text, 'YYYY')) + interval '1 week' * (pp.semana_no - 1)) - interval '7 days' 
            FROM product_prices pp
        )
        AND pp.ciudad = '{city}'
		AND cn.english_category = '{category}'
        GROUP BY pp.ciudad, pn.english_product, pp.semana_no, pp.anho
    ),
    week_price_difference AS (
        SELECT 
            current.city,
            current.product,
            current.year,
            current.week,
            current.avg_price AS current_avg_price,
            previous.avg_price AS previous_avg_price,
            ((current.avg_price - previous.avg_price) / previous.avg_price) * 100 AS percentage_change
        FROM latest_two_weeks current
        LEFT JOIN latest_two_weeks previous 
            ON current.product = previous.product 
            AND current.city = previous.city
            AND (
                current.week = previous.week + 1 
                OR (current.week = 1 AND previous.week = 52 AND current.year = previous.year + 1)
            )
        
        WHERE previous.avg_price IS NOT NULL
    )
    -- Get top 20 most significant price increases and top 20 decreases
    (
        SELECT *
        FROM week_price_difference
        WHERE percentage_change > 0
        ORDER BY percentage_change DESC
        LIMIT 20
    )
    UNION ALL
    (
        SELECT *
        FROM week_price_difference
        WHERE percentage_change < 0
        ORDER BY percentage_change ASC
        LIMIT 20
    )
    ORDER BY percentage_change DESC;
    """
    dataframe = run.queries_on_rds(query = query) 
    dataframe['product'] = dataframe['product'].str.replace('_',' ').str.title()
    return dataframe


# def marketplaces_product_dynamics_query(product:str): 
# 	query = f"""
# WITH product_avg AS (
#     SELECT 
#         cn.english_product AS product,
#         AVG(pp.precio_medio) AS national_avg_price,
#         pp.anho AS year,
#         pp.semana_no AS week,
#         date_trunc('year', to_date(anho::text, 'YYYY')) + interval '1 week' * (semana_no - 1) AS date
#     FROM product_prices pp
#     LEFT JOIN product_names cn ON pp.producto = cn.spanish_product
# 	WHERE cn.english_product = '{product}'
#     GROUP BY cn.english_product, pp.anho, pp.semana_no
# )
# SELECT 
#     cn.english_product AS product,
#     pp.mercado,
#     AVG(pp.precio_medio) AS avg_price,
#     ca.national_avg_price,
#     pp.anho AS year,
#     pp.semana_no AS week,
#     date_trunc('year', to_date(anho::text, 'YYYY')) + interval '1 week' * (semana_no - 1) AS date
# FROM product_prices pp
# LEFT JOIN product_names cn ON pp.producto = cn.spanish_product
# JOIN product_avg ca ON cn.english_product = ca.product AND pp.anho = ca.year AND pp.semana_no = ca.week
# GROUP BY cn.english_product, pp.mercado, ca.national_avg_price, pp.anho, pp.semana_no
# ORDER BY cn.english_product, pp.mercado, pp.anho, pp.semana_no;
# 	"""
# 	dataframe = run.queries_on_rds(query)
# 	return dataframe

# def major_price_changes_city_query(city: str, category: str = None):

#     query = f"""
#     WITH latest_two_weeks AS (
#         SELECT 
#             pp.ciudad AS city, 
#             pn.english_product AS product, 
#             pp.semana_no AS week, 
#             pp.anho AS year, 
#             AVG(pp.precio_medio) AS avg_price, 
#             date_trunc('year', to_date(pp.anho::text, 'YYYY')) + interval '1 week' * (pp.semana_no - 1) AS date
#         FROM product_prices pp
#         LEFT JOIN product_names pn ON pp.producto = pn.spanish_product
#         WHERE date_trunc('year', to_date(pp.anho::text, 'YYYY')) + interval '1 week' * (pp.semana_no - 1) >= (
#             SELECT MAX(date_trunc('year', to_date(pp.anho::text, 'YYYY')) + interval '1 week' * (pp.semana_no - 1)) - interval '7 days' 
#             FROM product_prices pp
#         )
#         AND pp.ciudad = '{city}'
#     """
    
#     if category:
#         query += f""" AND pn.english_category = '{category}'\n"""

#     query += """
#         GROUP BY pp.ciudad, pn.english_product, pp.semana_no, pp.anho
#     ),
#     week_price_difference AS (
#         SELECT 
#             current.city,
#             current.product,
#             current.year,
#             current.week,
#             current.avg_price AS current_avg_price,
#             previous.avg_price AS previous_avg_price,
#             ((current.avg_price - previous.avg_price) / previous.avg_price) * 100 AS percentage_change
#         FROM latest_two_weeks current
#         LEFT JOIN latest_two_weeks previous 
#             ON current.product = previous.product 
#             AND current.city = previous.city
#             AND (
#                 current.week = previous.week + 1 
#                 OR (current.week = 1 AND previous.week = 52 AND current.year = previous.year + 1)
#             )
#         WHERE previous.avg_price IS NOT NULL
#     )
#     -- Get top 20 most significant price increases and top 20 decreases
#     (
#         SELECT *
#         FROM week_price_difference
#         WHERE percentage_change > 0
#         ORDER BY percentage_change DESC
#         LIMIT 20
#     )
#     UNION ALL
#     (
#         SELECT *
#         FROM week_price_difference
#         WHERE percentage_change < 0
#         ORDER BY percentage_change ASC
#         LIMIT 20
#     )
#     ORDER BY percentage_change DESC;
#     """

#     # Run the query and process the result
#     dataframe = run.queries_on_rds(query=query)
#     dataframe['product'] = dataframe['product'].str.replace('_', ' ').str.title()
#     return dataframe



def product_query():
	query = """
	SELECT DISTINCT english_product as product
	FROM product_names;
	"""
	dataframe = run.queries_on_rds(query)
	return dataframe

def category_query():
	query = """
	SELECT DISTINCT english_category as category
	FROM category_names;
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

def marketplace_count_query(): 
	query = """
    SELECT mercado, count(*) as mercado_count FROM product_prices 
    GROUP BY mercado
    ORDER BY mercado_count DESC;
	"""
	dataframe = run.queries_on_rds(query)
	return dataframe

