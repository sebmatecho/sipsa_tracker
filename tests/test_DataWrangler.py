import pytest
import pandas as pd
from unittest import mock
from io import BytesIO
from botocore.exceptions import ClientError
import logging
from src.DataWrangler import DataWrangler

import pytest
import pandas as pd
from unittest import mock
from io import BytesIO
import logging

import pytest
import pandas as pd
from unittest import mock
from io import BytesIO
import logging

def test_first_format_data_extraction():
    # Mock S3 resource and bucket
    mock_s3 = mock.Mock()
    mock_bucket = mock.Mock()
    mock_s3.Bucket.return_value = mock_bucket

    # Create a sample Excel file in memory
    sample_data = {
        'Column1': ['Data1', 'Data2', 'Data3'],
        'Column2': [1, 2, 3]
    }
    sample_df = pd.DataFrame(sample_data)
    excel_file = BytesIO()
    sample_df.to_excel(excel_file, index=False)
    excel_file.seek(0)

    # Mock S3 object to return the Excel file
    mock_object = mock.Mock()
    mock_object.get.return_value = {'Body': excel_file}
    mock_bucket.Object.return_value = mock_object

    # Initialize DataWrangler with mock S3
    data_wrangler = DataWrangler(bucket_name='test-bucket', s3=mock_s3, logger=logging.getLogger('test_logger'))

    # Mock the regex filtering to return the sample_df
    with mock.patch('pandas.read_excel') as mock_read_excel:
        # First attempt with openpyxl
        mock_read_excel.return_value = sample_df.copy()

        result_df = data_wrangler.first_format_data_extraction('path/to/test_file.xlsx')

        # Ensure read_excel was called with openpyxl engine
        mock_read_excel.assert_called_with(mock.ANY, engine='openpyxl')

        # Check that result_df matches the filtered sample_df
        # Since the method applies a regex filter, adjust the sample data accordingly
        filtered_df = sample_df[sample_df['Column1'].str.contains(r'[a-zA-Z]', regex=True)]
        pd.testing.assert_frame_equal(result_df.reset_index(drop=True), filtered_df.reset_index(drop=True))

    # Test fallback to xlrd
    with mock.patch('pandas.read_excel') as mock_read_excel:
        # Simulate openpyxl failing
        mock_read_excel.side_effect = [Exception("openpyxl error"), sample_df.copy()]

        result_df = data_wrangler.first_format_data_extraction('path/to/test_file.xlsx')

        # Ensure read_excel was called twice, first with openpyxl, then xlrd
        assert mock_read_excel.call_count == 2
        calls = [mock.call(mock.ANY, engine='openpyxl'), mock.call(mock.ANY, engine='xlrd')]
        mock_read_excel.assert_has_calls(calls)

        # Check that result_df matches the filtered sample_df
        filtered_df = sample_df[sample_df['Column1'].str.contains(r'[a-zA-Z]', regex=True)]
        pd.testing.assert_frame_equal(result_df.reset_index(drop=True), filtered_df.reset_index(drop=True))

    # Test empty DataFrame scenario
    with mock.patch('pandas.read_excel') as mock_read_excel:
        mock_read_excel.return_value = pd.DataFrame()

        result_df = data_wrangler.first_format_data_extraction('path/to/empty_file.xlsx')

        # Check that result_df is empty
        assert result_df.empty, "The result should be an empty DataFrame when the file has no data"

    # Test exception handling when reading fails with both engines
    with mock.patch('pandas.read_excel') as mock_read_excel:
        mock_read_excel.side_effect = Exception("Both engines failed")

        result_df = data_wrangler.first_format_data_extraction('path/to/corrupt_file.xlsx')

        # Check that result_df is empty
        assert result_df.empty, "The result should be an empty DataFrame when reading fails"

def test_building_complete_report():
    # Mock DataWrangler methods and properties
    data_wrangler = DataWrangler(bucket_name='test-bucket', s3=None, logger=logging.getLogger('test_logger'))
    data_wrangler.categories_dict = {1: 'Fruits', 2: 'Vegetables'}

    # Mock the file paths
    data_wrangler.first_format_paths = mock.Mock(return_value=['path/to/first_format_file1.xlsx'])
    data_wrangler.second_format_paths = mock.Mock(return_value=['path/to/second_format_file1.xlsx'])

    # Mock the data extraction and transformation methods
    sample_first_format_data = pd.DataFrame({
        'producto': ['Product A'],
        'ciudad': ['City1'],
        'precio_minimo': [100],
        'precio_maximo': [150],
        'precio_medio': [125],
        'tendencia': ['+'],
        'categoria': ['Fruits'],
        'mercado': [None],
        'semana_no': [1],
        'anho': [2021]
    })

    sample_second_format_data = pd.DataFrame({
        'producto': ['Product B'],
        'ciudad': ['City2'],
        'precio_minimo': [200],
        'precio_maximo': [250],
        'precio_medio': [225],
        'tendencia': ['-'],
        'categoria': ['Vegetables'],
        'mercado': [None],
        'semana_no': [2],
        'anho': [2021]
    })

    data_wrangler.first_format_data_extraction = mock.Mock(return_value=sample_first_format_data)
    data_wrangler.first_format_data_transformation = mock.Mock(return_value=sample_first_format_data)
    data_wrangler.second_format_data_extraction = mock.Mock(return_value=sample_second_format_data)

    # Call the method
    result_df = data_wrangler.building_complete_report()

    # Check that result_df contains data from both formats
    assert not result_df.empty, "The result should not be an empty DataFrame"
    assert len(result_df) == 2, "The result should contain two rows"

    # Verify that the data includes both products
    assert 'Product A' in result_df['producto'].values, "'Product A' should be in the result DataFrame"
    assert 'Product B' in result_df['producto'].values, "'Product B' should be in the result DataFrame"

    
