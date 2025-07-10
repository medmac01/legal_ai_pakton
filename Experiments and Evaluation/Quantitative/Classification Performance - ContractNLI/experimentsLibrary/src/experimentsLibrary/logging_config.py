"""
Description:
Centralized logging configuration module for the experiments library. Provides get_logger function that creates
standardized loggers with both console and file output handlers. Supports configurable log levels, custom log
files, and consistent formatting across the entire application.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date  : 2025/07/8
"""

import logging

def get_logger(name: str, log_file: str = 'experiments.log', level: int = logging.DEBUG) -> logging.Logger:
    """
    Configures and returns a logger with console and file handlers.

    Args:
        name (str): Name of the logger (usually `__name__`).
        log_file (str): Path to the log file. Defaults to 'experiments.log'.
        level (int): Logging level (e.g., logging.DEBUG, logging.INFO). Defaults to logging.DEBUG.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding duplicate handlers
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(
            "[%(asctime)s]  [%(levelname)s]  [%(message)s]",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)

        # File handler
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            "[%(asctime)s]  [%(levelname)s]  [%(message)s]",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)

        # Add handlers to logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger



# example usage:

# from logging_config import get_logger

# logger = get_logger(__name__)

# logger.info("This is an info message from example_function.")
# logger.warning("This is a warning message from example_function.")