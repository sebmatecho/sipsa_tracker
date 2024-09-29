
import logging
import sys
from pathlib import Path

# Configure logging
def setup_logger():
    """
    Sets up and configures a logger for the application.

    This function creates a logger that outputs log messages both to the console (stdout) and a log file. 
    It ensures the log directory and file are created if they do not already exist.

    The log messages include the timestamp, log level, and message. The log level is set to `INFO` for 
    both console and file handlers, meaning that messages of level `INFO` and higher will be recorded.

    Returns:
        logger (logging.Logger): Configured logger object for the application.

    Logging Details:
        - Log Directory: A directory named 'logs' is created in the current working directory if it does not exist.
        - Log File: Logs are written to 'sipsa_process.log' in the 'logs' directory.
        - Log Format: '%(asctime)s - %(levelname)s - %(message)s'
        - Log Levels: Both console and file handlers are set to `INFO`.
        - Handlers:
            - Console (`stdout`) Handler: Outputs logs to the console.
            - File Handler: Outputs logs to 'sipsa_process.log' with overwrite mode (`mode='w'`).
    
    Example Usage:
        >>> logger = setup_logger()
        >>> logger.info("Logger is successfully configured.")

    Last update:
        Sept 28, 2024. 
    """
    
    # Create logfile path
    log_path = Path.cwd()/'logs'
    if not log_path.exists():
        print(f'{log_path} created successfully')
        log_path.mkdir(parents = True, 
                   exist_ok = True)
        
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create handlers
    c_handler = logging.StreamHandler(sys.stdout)
    f_handler = logging.FileHandler(log_path/'sipsa_process.log', mode='w')

    # Set levels
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.INFO)

    # Create formatters and add them to handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger
