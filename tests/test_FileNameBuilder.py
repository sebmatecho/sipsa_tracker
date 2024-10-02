import pytest
from src.FileNameBuilder import FileNameBuilder
from unittest.mock import MagicMock


@pytest.fixture
def mock_s3():
    # Mock S3 resource
    s3 = MagicMock()
    return s3

@pytest.fixture
def file_name_builder(mock_s3, mocker):
    logger = mocker.MagicMock()  # Mock logger
    return FileNameBuilder(s3=mock_s3, logger=logger)

def test_first_format_paths(file_name_builder, mock_s3):
    # Mock bucket objects
    mock_s3.Bucket().objects.all.return_value = [
        MagicMock(key='reports/2012/week_10_file1.xls'),
        MagicMock(key='reports/2013/week_15_file2.xlsx'),
        MagicMock(key='reports/2018/week_19_file3.xlsx'),
        MagicMock(key='reports/2018/week_20_file4.xlsx'),
        MagicMock(key='reports/invalid/file.txt')
    ]

    result = file_name_builder.first_format_paths('test-bucket')

    assert len(result) == 3  # Three valid first format files
    assert 'reports/2012/week_10_file1.xls' in result
    assert 'reports/2013/week_15_file2.xlsx' in result
    assert 'reports/2018/week_19_file3.xlsx' in result
    assert 'reports/2018/week_20_file4.xlsx' not in result

def test_second_format_paths(file_name_builder, mock_s3):
    # Mock bucket objects
    mock_s3.Bucket().objects.all.return_value = [
        MagicMock(key='reports/2018/week_19_file1.xls'),
        MagicMock(key='reports/2018/week_20_file2.xlsx'),
        MagicMock(key='reports/2020/week_10_file3.xlsx'),
        MagicMock(key='reports/2024/week_11_file4.xlsx'),
        MagicMock(key='reports/invalid/file.txt')
    ]

    result = file_name_builder.second_format_paths('test-bucket')

    assert len(result) == 3  # Three valid second format files
    assert 'reports/2018/week_19_file1.xls' not in result  # Week 19 is part of first format
    assert 'reports/2018/week_20_file2.xlsx' in result
    assert 'reports/2020/week_10_file3.xlsx' in result
    assert 'reports/2024/week_11_file4.xlsx' in result

def test_first_format_paths_with_errors(file_name_builder, mock_s3, mocker):
    # Mock bucket objects
    mock_s3.Bucket().objects.all.return_value = [
        MagicMock(key='reports/2012/week_10_file1.xls'),
        MagicMock(key='reports/2013/invalid_name.xlsx')  # Invalid file name
    ]

    # Mock the logger to check for warnings
    mock_logger = mocker.patch.object(file_name_builder.logger, 'warning')

    result = file_name_builder.first_format_paths('test-bucket')

    assert len(result) == 1  # Only one valid file
    assert 'reports/2012/week_10_file1.xls' in result
    mock_logger.assert_called_once_with(
        "Error processing path reports/2013/invalid_name.xlsx: invalid literal for int() with base 10: 'name'"
    )

def test_second_format_paths_with_errors(file_name_builder, mock_s3, mocker):
    # Mock bucket objects
    mock_s3.Bucket().objects.all.return_value = [
        MagicMock(key='reports/2019/week_abc_file1.xls'),  # Invalid week number
        MagicMock(key='reports/2020/week_10_file2.xlsx')
    ]

    # Mock the logger to check for warnings
    mock_logger = mocker.patch.object(file_name_builder.logger, 'warning')

    result = file_name_builder.second_format_paths('test-bucket')

    assert len(result) == 1  # Only one valid file
    assert 'reports/2020/week_10_file2.xlsx' in result
    mock_logger.assert_called_once_with('Error processing path reports/2019/week_abc_file1.xls: invalid literal for int() with base 10: \'abc\'')
