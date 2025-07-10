"""
Description:
Main initialization module for the experimentsLibrary package. This module sets up environment variables from .env files,
configures logging, and exports key components for model evaluation including the testAndEvaluate function, ContractNLI
dataset handling, model configurations, and result saving utilities.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date  : 2025/07/08
"""

################# ENVIRONMENTAL VARIABLES ############

from dotenv import load_dotenv, find_dotenv
import os

# Load environment variables from the .env file to the os.environ dict
load_dotenv(override=True)
# example access
# os.environ["OPENAI_API_KEY"]

######################################################

from src.experimentsLibrary.logging_config import get_logger

# Get a logger for this module
logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info("Init executed directly")

from src.experimentsLibrary.evaluation import testAndEvaluate
from src.experimentsLibrary.huggingfaceDatasets import ContractNLIDataset # type: ignore
from src.experimentsLibrary.models import models
from src.experimentsLibrary.utils import save_result_to_file

# Define what should be exported when `import experimentsLibrary` is used
__all__ = [
    "testAndEvaluate",
    "ContractNLIDataset",
    "models",
    "save_result_to_file"
]
