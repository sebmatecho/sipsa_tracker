from src.logging_setup import setup_logger  
import pytest
import logging
import tempfile
import shutil
from unittest import mock
from pathlib import Path
from datetime import datetime
import sys

import pytest
import logging
import tempfile
import shutil
from unittest import mock
from pathlib import Path
from datetime import datetime
import sys

def test_setup_logger():
    # Mock the S3 resource
    mock_s3 = mock.Mock()

    # Use a temporary directory for logs
    with tempfile.TemporaryDirectory() as temp_log_dir:
        # Patch the Path.cwd() to return the temporary directory
        with mock.patch('pathlib.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path(temp_log_dir)

            # Call the setup_logger function
            logger, upload_log_to_s3 = setup_logger(s3=mock_s3)

            # Verify the logger is configured correctly
            assert isinstance(logger, logging.Logger), "Logger is not an instance of logging.Logger"
            assert logger.level == logging.INFO, "Logger level is not INFO"

            # Check that two handlers are added: StreamHandler and FileHandler
            handlers = logger.handlers
            assert len(handlers) == 2, f"Logger should have two handlers, found {len(handlers)}"
            handler_types = [type(h) for h in handlers]
            assert logging.StreamHandler in handler_types, "Logger should have a StreamHandler"
            assert logging.FileHandler in handler_types, "Logger should have a FileHandler"

            # Check that handlers have correct levels
            for handler in handlers:
                if isinstance(handler, logging.FileHandler):
                    assert handler.level == logging.INFO, "FileHandler level should be INFO"
                elif isinstance(handler, logging.StreamHandler):
                    assert handler.level == logging.ERROR, "StreamHandler level should be ERROR"

            # Log a test message
            logger.info("Test log message")

            # Construct expected log file path
            today_date = datetime.today().strftime(format='%m_%d_%Y')
            expected_log_file = Path(temp_log_dir) / 'logs' / f'sipsa_process_{today_date}.log'

            # Verify that the log file is created
            assert expected_log_file.exists(), f"Log file {expected_log_file} does not exist"

            # Read the log file and check the contents
            with open(expected_log_file, 'r') as f:
                log_contents = f.read()
                assert "Test log message" in log_contents, "Log file does not contain the test message"

            # Test the upload_log_to_s3 function
            # Mock the open function to read the log file
            with mock.patch('builtins.open', mock.mock_open(read_data=log_contents)) as mock_file:
                # Call the upload_log_to_s3 function
                bucket_name = 'test-bucket'
                upload_log_to_s3(bucket_name)

                # Verify that s3.Bucket().put_object() was called with correct parameters
                mock_s3.Bucket.assert_called_with(bucket_name)
                mock_s3.Bucket(bucket_name).put_object.assert_called_once()

                # Extract the arguments used in put_object
                called_args = mock_s3.Bucket(bucket_name).put_object.call_args[1]
                assert 'Key' in called_args, "'Key' not in put_object arguments"
                assert 'Body' in called_args, "'Body' not in put_object arguments"

                # Verify that the Key includes the s3_key_prefix and file_name
                s3_key_prefix = "logs/"
                file_name = f'sipsa_process_{today_date}.log'
                expected_s3_key = s3_key_prefix + file_name
                assert called_args['Key'] == expected_s3_key, f"S3 key is incorrect: {called_args['Key']}"

                # Verify that the Body is the log contents
                # Since we mocked open, we can't check the actual file contents here
                # But we can assume that the file was read correctly

            # Clean up handlers to avoid side effects
            for handler in logger.handlers[:]:
                handler.flush()
                handler.close()
                logger.removeHandler(handler)
