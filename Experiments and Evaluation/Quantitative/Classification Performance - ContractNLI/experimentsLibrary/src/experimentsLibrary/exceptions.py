"""
Description:
Custom exception classes and retry handling utilities for the experiments library. Defines InvalidOutputException
for handling invalid LLM responses and provides handle_retry function with configurable exponential backoff
and retry logic for robust error handling across API calls.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date  : 2025/07/08
"""

class InvalidOutputException(Exception):
    """Custom exception class for invalid output from the LLM"""
    pass

import time
from src.experimentsLibrary.logging_config import get_logger

# Get a logger for this module
logger = get_logger(__name__)

def handle_retry(errorMessage, retries, maxRetries, backoff=False):
    """
    Handles retries for different exceptions by logging the error, 
    applying a retry mechanism with optional exponential backoff, 
    and raising an exception when retries are exhausted.

    Args:
        errorMessage (str): Description of the error encountered.
        retries (int): Current number of retries attempted.
        maxRetries (int): Maximum number of retries allowed.
        backoff (bool): Whether to use exponential backoff for delays.

    Returns:
        int: Updated retry count.

    Raises:
        Exception: If retries exceed maxRetries.
    """
    logger.error(f"Error: {errorMessage}")
    retries += 1
    if retries >= maxRetries:
        logger.error("Max retries reached.")
        raise Exception("Max retries reached due to errors.")
    logger.debug(f"Retrying {retries}/{maxRetries} after a delay...")
    if backoff:
        time.sleep(2 ** retries)  # Exponential backoff
    else:
        time.sleep(1)  # Fixed delay
    return retries