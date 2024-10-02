import pytest
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import MagicMock
from src.DataIngestor import DataIngestor

@pytest.fixture
def mock_engine(mocker):
    """
    Fixture that returns a mock SQLAlchemy engine.
    """
    return mocker.Mock()

@pytest.fixture
def mock_logger(mocker):
    """
    Fixture that returns a mock logger.
    """
    return mocker.Mock()

@pytest.fixture
def data_ingestor(mock_engine, mock_logger):
    """
    Fixture that returns an instance of the DataIngestor class with a mock engine and logger.
    """
    return DataIngestor(engine=mock_engine, logger=mock_logger)

def test_insert_dataframe_to_db_success(data_ingestor, mocker):
    """
    Test the successful insertion of a DataFrame into the database.
    """
    # Mock DataFrame
    mock_df = pd.DataFrame({'column1': [1, 2], 'column2': ['A', 'B']})

    # Patch the to_sql method
    mock_to_sql = mocker.patch.object(mock_df, 'to_sql', autospec=True)

    # Call the method
    data_ingestor.insert_dataframe_to_db(mock_df, 'test_table')

    # Check if to_sql was called with correct parameters
    mock_to_sql.assert_called_once_with('test_table', 
                                        data_ingestor.engine, 
                                        if_exists='append', 
                                        index=False, 
                                        chunksize=500)

    # Check if the logger info was called
    data_ingestor.logger.info.assert_called_once_with('Data successfully inserted into test_table.')

def test_insert_dataframe_to_db_failure(data_ingestor, mocker):
    """
    Test the case where an SQLAlchemyError occurs during the insertion.
    """
    # Mock DataFrame
    mock_df = pd.DataFrame({'column1': [1, 2], 'column2': ['A', 'B']})

    # Patch the to_sql method to raise an error
    mock_to_sql = mocker.patch.object(mock_df, 'to_sql', autospec=True)
    mock_to_sql.side_effect = SQLAlchemyError("Mocked SQLAlchemy Error")

    # Call the method and check for an exception
    with pytest.raises(SQLAlchemyError):
        data_ingestor.insert_dataframe_to_db(mock_df, 'test_table')

    # Check if the logger error was called
    data_ingestor.logger.error.assert_called_once_with("Error inserting data: Mocked SQLAlchemy Error")
    
def test_engine_dispose_called(data_ingestor, mocker):
    """
    Test if the engine.dispose method is called after inserting the DataFrame.
    """
    # Mock DataFrame
    mock_df = pd.DataFrame({'column1': [1, 2], 'column2': ['A', 'B']})

    # Patch the to_sql method
    mocker.patch.object(mock_df, 'to_sql', autospec=True)

    # Patch the dispose method of the engine
    mock_dispose = mocker.patch.object(data_ingestor.engine, 'dispose')

    # Call the method
    data_ingestor.insert_dataframe_to_db(mock_df, 'test_table')

    # Check if dispose was called
    mock_dispose.assert_called_once()
