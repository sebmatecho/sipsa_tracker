import pytest
import pandas as pd
import logging
from src.DataValidator import DataValidator

@pytest.fixture
def data_validator():
    # Mock logger
    logger = logging.getLogger('test_logger')
    return DataValidator(logger)

def test_validate_city(data_validator):
    # Test valid city
    assert data_validator.validate_city('bogota') is True
    # Test invalid city
    assert data_validator.validate_city('invalid_city') is False

def test_validate_product(data_validator):
    # Test valid product
    assert data_validator.validate_product('acelga') is True
    # Test invalid product
    assert data_validator.validate_product('invalid_product') is False

def test_validate_price(data_validator):
    # Test valid prices
    assert data_validator.validate_price(100) is True
    assert data_validator.validate_price(0) is True
    # Test invalid prices
    assert data_validator.validate_price(-1) is False
    assert data_validator.validate_price('invalid_price') is False

def test_validate_tendencia(data_validator):
    # Test valid tendencia
    assert data_validator.validate_tendencia('+') is True
    assert data_validator.validate_tendencia('+++') is True
    # Test invalid tendencia
    assert data_validator.validate_tendencia('invalid') is False

def test_validate_categoria(data_validator):
    # Test valid categoria
    assert data_validator.validate_categoria('verduras_hortalizas') is True
    # Test invalid categoria
    assert data_validator.validate_categoria('invalid_category') is False

def test_remove_accents_trails_caps(data_validator):
    # Test cleaning of text
    result = data_validator.remove_accents_trails_caps('Bogotá')
    assert result == 'bogota'

def test_validate_dataframe(data_validator, mocker):
    # Create a mock dataframe
    data = {
        'ciudad': ['Bogotá', 'invalid_city'],
        'producto': ['acelga', 'invalid_product'],
        'precio_minimo': [100, -1],
        'precio_maximo': [200, 300],
        'precio_medio': [150, 250],
        'tendencia': ['+', 'invalid'],
        'categoria': ['verduras_hortalizas', 'invalid_category']
    }
    df = pd.DataFrame(data)

    # Patch the logger to check logging behavior
    mock_logger = mocker.patch.object(data_validator.logger, 'warning')

    # Validate the dataframe
    valid_df = data_validator.validate_dataframe(df)

    # Check that only valid rows are returned
    assert len(valid_df) == 1
    assert valid_df.iloc[0]['ciudad'] == 'bogota'
    assert valid_df.iloc[0]['producto'] == 'acelga'

    # Check if logger was called for invalid rows
    invalid_row_count = 1  # There is 1 invalid row in the mock data
    mock_logger.assert_called_once_with(f"Invalid rows found and removed: {invalid_row_count}")
