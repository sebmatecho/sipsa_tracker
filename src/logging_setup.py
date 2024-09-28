
import logging
import sys
from pathlib import Path

# Configure logging
def setup_logger():
    
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


