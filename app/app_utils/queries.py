from app_utils import aws

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
	

def city_query():
    query = """
    SELECT DISTINCT ciudad
    FROM product_prices;
    """
    dataframe = run.queries_on_rds(query)
    return dataframe
