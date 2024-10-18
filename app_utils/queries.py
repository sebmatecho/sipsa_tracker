def test_query(city:str): 
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
	return query 
	 