"""
Logging configuration for Fogbound.
"""
import logging
import os
from datetime import datetime

def setup_logger(name: str, log_file: str = None, level=logging.INFO):
    """
    Set up a logger with both file and console output.
    
    Args:
        name: Logger name (usually __name__)
        log_file: Path to log file (if None, uses logs/collector.log)
        level: Logging level
        
    Returns:
        Configured logger
    """
    # create logs directory if it doesn't exist
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # use default log file if not specified
    if log_file is None:
        log_file = os.path.join(logs_dir, 'collector.log')
    
    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # prevent duplicate handlers if logger already exists
    if logger.handlers:
        return logger
    
    # create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # file handler -> logs everything
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # console handler -> only INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger