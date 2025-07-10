import unittest
from src.experimentsLibrary.huggingfaceDatasets import ContractNLIDataset

from src.experimentsLibrary.logging_config import get_logger

# Get a logger for this module
logger = get_logger(__name__)


class TestContractNLIDataset(unittest.TestCase):
    """
    Integration tests for the ContractNLIDataset class without mocking.
    """

    def setUp(self):
        """
        Set up the ContractNLIDataset instance for tests.
        Ensures HUGGINGFACE_TOKEN is set in the environment.
        """
        logger.info("Initializing ContractNLIDataset instance...")
        self.dataset_handler = ContractNLIDataset()
        logger.info("ContractNLIDataset initialized successfully.")

    def test_initialization(self):
        """
        Test that the ContractNLIDataset initializes correctly and loads the dataset.
        """
        logger.info("Testing initialization of ContractNLIDataset...")
        # Assert the dataset is loaded
        self.assertIsNotNone(self.dataset_handler.dataset, "Dataset should not be None.")
        logger.info("Dataset is loaded successfully.")
        
        self.assertIn("train", self.dataset_handler.dataset, "Dataset should have a 'train' split.")
        logger.info("'train' split is available in the dataset.")
        
        self.assertIn("test", self.dataset_handler.dataset, "Dataset should have a 'test' split.")
        logger.info("'test' split is available in the dataset.")

    def test_describe_dataset(self):
        """
        Test the describe_dataset method outputs dataset details without errors.
        """
        logger.info("Testing describe_dataset method...")
        try:
            self.dataset_handler.describe_dataset()
            logger.info("describe_dataset executed successfully.")
        except Exception as e:
            logger.error(f"describe_dataset raised an exception: {e}")
            self.fail(f"describe_dataset raised an exception: {e}")

    def test_analyze_class_distribution(self):
        """
        Test the analyze_class_distribution method outputs class distribution without errors.
        """
        logger.info("Testing analyze_class_distribution method...")
        try:
            self.dataset_handler.analyze_class_distribution()
            logger.info("analyze_class_distribution executed successfully.")
        except Exception as e:
            logger.error(f"analyze_class_distribution raised an exception: {e}")
            self.fail(f"analyze_class_distribution raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()
