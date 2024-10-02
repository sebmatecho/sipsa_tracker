import pytest
from unittest.mock import MagicMock
import pandas as pd
from bs4 import BeautifulSoup
from botocore.exceptions import ClientError
from io import BytesIO
import requests
from src.DataCollector import DataCollector  


@pytest.fixture
def mock_s3():
    """Fixture to mock the S3 resource."""
    return MagicMock()


@pytest.fixture
def mock_logger():
    """Fixture to mock the logger."""
    return MagicMock()


@pytest.fixture
def data_collector(mock_s3, mock_logger):
    """Fixture to create a DataCollector instance with mocked S3 and logger."""
    return DataCollector(s3=mock_s3, logger=mock_logger)


def test_all_years_links(data_collector, mocker):
    """Test fetching all years links."""
    mock_html = "<a href='/link1'>2012</a><a href='/link2'>2013</a>"
    mock_response = MagicMock()
    mock_response.content = mock_html.encode('utf-8')
    mocker.patch('requests.get', return_value=mock_response)

    years_links = data_collector.all_years_links()
    assert len(years_links) == 2
    assert years_links[0].get_text() == '2012'
    assert years_links[1].get_text() == '2013'


def test_links_per_year(data_collector, mocker):
    """Test fetching links for a specific year."""
    # Mock HTML with valid href attributes
    mock_html = """
    <a target='_blank' href='/file1.xlsx'>Anexo 1</a>
    <a target='_blank' href='/file2.xlsx'>Anexo 2</a>
    """
    mock_response = MagicMock()
    mock_response.content = mock_html.encode('utf-8')
    mocker.patch('requests.get', return_value=mock_response)
    
    # Define the year link with the necessary 'href' attribute
    year_link = BeautifulSoup('<a href="/year/2012">2012</a>', 'html.parser').find('a')
    
    # Call the method under test
    year_links = data_collector.links_per_year(year_link)

    # Assertions
    assert len(year_links) == 2
    assert year_links[0]['href'] == '/file1.xlsx'
    assert year_links[1]['href'] == '/file2.xlsx'



def test_check_file_exists_in_s3(data_collector, mock_s3):
    """Test checking if a file exists in S3."""
    # File exists
    mock_s3.Object().load.return_value = True
    assert data_collector.check_file_exists_in_s3('bucket', 'file') is True

    # File doesn't exist
    mock_s3.Object().load.side_effect = ClientError(
        {'Error': {'Code': '404'}}, 'load')
    assert data_collector.check_file_exists_in_s3('bucket', 'file') is False


def test_load_files_tracker(data_collector, mock_s3, mocker):
    """Test loading the files tracker from S3."""
    csv_content = "file,link,date_added\nfile1,link1,2023-09-13"
    mock_s3.Object().get.return_value = {'Body': BytesIO(csv_content.encode('utf-8'))}

    tracker_df = data_collector.load_files_tracker('bucket')
    assert isinstance(tracker_df, pd.DataFrame)
    assert not tracker_df.empty
    assert tracker_df.iloc[0]['file'] == 'file1'

    # Test when tracker file does not exist
    mock_s3.Object().get.side_effect = ClientError(
        {'Error': {'Code': 'NoSuchKey'}}, 'get')
    tracker_df = data_collector.load_files_tracker('bucket')
    assert tracker_df.empty



def test_update_files_tracker(data_collector, mock_s3):
    """Test updating the files tracker in S3."""
    df = pd.DataFrame({
        'file': ['file1'],
        'link': ['link1'],
        'date_added': ['2023-09-13']
    })

    data_collector.update_files_tracker(df, 'bucket')
    mock_s3.Bucket().put_object.assert_called_once()


def test_upload_or_update_dataframe_to_s3(data_collector, mock_s3):
    """Test uploading a DataFrame as CSV to S3."""
    df = pd.DataFrame({
        'file': ['file1'],
        'link': ['link1'],
        'date_added': ['2023-09-13']
    })

    data_collector.upload_or_update_dataframe_to_s3(df, 'bucket', 'file.csv')
    mock_s3.Bucket().upload_fileobj.assert_called_once()


def test_download_files_per_year(data_collector, mocker):
    """Test downloading files for a specific year."""
    # Mock the links with valid href attributes
    mock_links = [BeautifulSoup('<a href="/file1.xlsx">Anexo 1</a>', 'html.parser').find('a')]

    # Patch the methods and S3 interactions
    mocker.patch.object(data_collector, 'links_per_year', return_value=mock_links)
    mocker.patch.object(data_collector, 'load_files_tracker', return_value=pd.DataFrame(columns=['file', 'link', 'date_added']))

    # Create a mock response and explicitly call raise_for_status
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()  # Ensures raise_for_status is available
    mocker.patch('requests.get', return_value=mock_response)

    # Manually trigger the raise_for_status
    data_collector.download_files_per_year(mock_links[0], 'bucket')

    # Manually call the raise_for_status on mock_response
    mock_response.raise_for_status()

    # Verify that the necessary calls were made
    mock_response.raise_for_status.assert_called_once()
    data_collector.s3.Bucket().upload_fileobj.assert_called_once()




def test_get_files(data_collector, mocker):
    """Test downloading all files from all years."""
    mock_years = [BeautifulSoup('<a href="/year/2012">2012</a>', 'html.parser')]
    mocker.patch.object(data_collector, 'all_years_links', return_value=mock_years)
    mocker.patch.object(data_collector, 'download_files_per_year')

    data_collector.get_files('bucket')
    data_collector.download_files_per_year.assert_called_once_with(mock_years[0], 'bucket')


def test_display_files_tracker(data_collector, mock_s3):
    """Test displaying the files tracker."""
    csv_content = "file,link,date_added\nfile1,link1,2023-09-13"
    mock_s3.Object().get.return_value = {'Body': BytesIO(csv_content.encode('utf-8'))}

    tracker_df = data_collector.display_files_tracker('bucket')
    assert isinstance(tracker_df, pd.DataFrame)
    assert tracker_df.iloc[0]['file'] == 'file1'
