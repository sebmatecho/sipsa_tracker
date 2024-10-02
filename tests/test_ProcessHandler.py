import pytest
import pandas as pd
from unittest.mock import MagicMock, patch, ANY
from pandas.testing import assert_frame_equal
from src.ProcessHandler import ProcessHandler
from pathlib import Path


def test_update_files_tracker_with_rds_load():
    # Mock dependencies
    s3_mock = MagicMock()
    engine_mock = MagicMock()
    logger_mock = MagicMock()

    # Mock the load_files_tracker method
    with patch.object(ProcessHandler, 'load_files_tracker') as mock_load_files_tracker:
        # Set up the mock to return a predefined DataFrame
        mock_load_files_tracker.return_value = pd.DataFrame({
            'file': ['file1.xls', 'file2.xls'],
            'rds_load': ['no', 'no']
        })

        # Initialize ProcessHandler
        process_handler = ProcessHandler(
            s3=s3_mock,
            engine=engine_mock,
            bucket_name='test-bucket',
            table_name='test-table',
            logger=logger_mock
        )

    # Mock the update_files_tracker method to prevent actual S3 interaction
    process_handler.update_files_tracker = MagicMock()

    # Test updating an existing file
    process_handler.update_files_tracker_with_rds_load('file1.xls')

    # Assertions
    assert process_handler.files_tracker_df.loc[
        process_handler.files_tracker_df['file'] == 'file1.xls', 'rds_load'
    ].values[0] == 'yes'

    # Test adding a new file
    process_handler.update_files_tracker_with_rds_load('file3.xls')

    # Assertions
    assert 'file3.xls' in process_handler.files_tracker_df['file'].values
    assert process_handler.files_tracker_df.loc[
        process_handler.files_tracker_df['file'] == 'file3.xls', 'rds_load'
    ].values[0] == 'yes'

    # Ensure update_files_tracker was called twice
    assert process_handler.update_files_tracker.call_count == 2
    process_handler.update_files_tracker.assert_called_with(
        process_handler.files_tracker_df, 'test-bucket'
    )



def test_querying_db():
    # Mock dependencies
    s3_mock = MagicMock()
    engine_mock = MagicMock()
    logger_mock = MagicMock()

    # Create a mock connection
    conn_mock = MagicMock()
    engine_mock.begin.return_value.__enter__.return_value = conn_mock

    # Mock the load_files_tracker method
    with patch.object(ProcessHandler, 'load_files_tracker') as mock_load_files_tracker:
        # Set up the mock to return a predefined DataFrame
        mock_load_files_tracker.return_value = pd.DataFrame({
            'file': ['file1.xls', 'file2.xls'],
            'rds_load': ['no', 'no']
        })

        # Initialize ProcessHandler
        process_handler = ProcessHandler(
            s3=s3_mock,
            engine=engine_mock,
            bucket_name='test-bucket',
            table_name='test-table',
            logger=logger_mock
        )

    # Mock pd.read_sql
    test_df = pd.DataFrame({'col1': [1, 2], 'col2': ['A', 'B']})
    with patch('pandas.read_sql', return_value=test_df) as mock_read_sql:
        # Execute the method
        result_df = process_handler.querying_db("SELECT * FROM test_table")

        # Assertions
        mock_read_sql.assert_called_once_with(sql="SELECT * FROM test_table", con=conn_mock)
        pd.testing.assert_frame_equal(result_df, test_df)


def test_executing_process():
    # Mock dependencies
    s3_mock = MagicMock()
    engine_mock = MagicMock()
    logger_mock = MagicMock()

    # Mock the load_files_tracker method
    with patch.object(ProcessHandler, 'load_files_tracker') as mock_load_files_tracker:
        # Set up the mock to return a predefined DataFrame
        mock_load_files_tracker.return_value = pd.DataFrame({
            'file': ['file1.xls', 'file2.xlsx'],
            'rds_load': ['no', 'no']
        })

        # Initialize ProcessHandler
        process_handler = ProcessHandler(
            s3=s3_mock,
            engine=engine_mock,
            bucket_name='test-bucket',
            table_name='test-table',
            logger=logger_mock
        )

    # Mock methods called within executing_process
    process_handler.get_files = MagicMock()
    process_handler.first_format_paths = MagicMock(return_value=['path/to/file1.xls'])
    process_handler.second_format_paths = MagicMock(return_value=['path/to/file2.xlsx'])
    process_handler.download_file_from_sipsa = MagicMock()
    process_handler.first_format_data_extraction = MagicMock(return_value=pd.DataFrame({'data': [1, 2, 3]}))
    process_handler.first_format_data_transformation = MagicMock(return_value=pd.DataFrame({'transformed': [1, 2, 3]}))
    process_handler.validate_dataframe = MagicMock(side_effect=lambda df: df)  # Return the DataFrame as is
    process_handler.insert_dataframe_to_db = MagicMock()
    process_handler.update_files_tracker_with_rds_load = MagicMock()
    process_handler.second_format_data_extraction = MagicMock(return_value=pd.DataFrame({'data': [4, 5, 6]}))

    # Since the method uses tqdm, we'll patch it to prevent unnecessary output during testing
    with patch('tqdm.tqdm', lambda x: x):
        # Execute the method
        result_df = process_handler.executing_process(output_dataframe=True)

    # Assertions
    process_handler.get_files.assert_called_once_with('test-bucket')
    process_handler.first_format_paths.assert_called_once_with(bucket_name='test-bucket')
    process_handler.second_format_paths.assert_called_once_with(bucket_name='test-bucket')

    # Check that the first format file was processed
    process_handler.first_format_data_extraction.assert_called_once_with('path/to/file1.xls')
    process_handler.first_format_data_transformation.assert_called_once_with(
        process_handler.first_format_data_extraction.return_value,
        'path/to/file1.xls'
    )
    process_handler.validate_dataframe.assert_any_call(ANY)
    process_handler.insert_dataframe_to_db.assert_any_call(
        dataframe=ANY,
        table_name='test-table'
    )
    process_handler.update_files_tracker_with_rds_load.assert_any_call('file1.xls')

    # Check that the second format file was processed
    process_handler.second_format_data_extraction.assert_called_once_with('path/to/file2.xlsx')
    process_handler.validate_dataframe.assert_any_call(ANY)
    process_handler.insert_dataframe_to_db.assert_any_call(
        dataframe=ANY,
        table_name='test-table'
    )
    process_handler.update_files_tracker_with_rds_load.assert_any_call('file2.xlsx')

    # Alternatively, inspect the call arguments to verify the DataFrames
    insert_calls = process_handler.insert_dataframe_to_db.call_args_list
    assert len(insert_calls) == 2

    # Extract call arguments
    first_call_kwargs = insert_calls[0].kwargs
    second_call_kwargs = insert_calls[1].kwargs

    # Compare DataFrames using assert_frame_equal
    assert_frame_equal(
        first_call_kwargs['dataframe'],
        process_handler.first_format_data_transformation.return_value
    )
    assert first_call_kwargs['table_name'] == 'test-table'

    assert_frame_equal(
        second_call_kwargs['dataframe'],
        process_handler.second_format_data_extraction.return_value
    )
    assert second_call_kwargs['table_name'] == 'test-table'

    # Check the result DataFrame
    expected_df = pd.concat([
        process_handler.first_format_data_transformation.return_value,
        process_handler.second_format_data_extraction.return_value
    ], ignore_index=True)
    pd.testing.assert_frame_equal(result_df.reset_index(drop=True), expected_df.reset_index(drop=True))