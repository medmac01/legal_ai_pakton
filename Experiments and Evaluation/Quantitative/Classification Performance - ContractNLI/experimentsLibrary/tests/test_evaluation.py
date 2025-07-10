import unittest
from src.experimentsLibrary.evaluation import testAndEvaluate
from src.experimentsLibrary.huggingfaceDatasets import ContractNLIDataset
from src.experimentsLibrary.logging_config import get_logger
from src.experimentsLibrary.models import models
from src.experimentsLibrary.utils import save_result_to_file
from datetime import datetime

# Get a logger for this module
logger = get_logger(__name__)

class TestTestAndEvaluate(unittest.TestCase):
    """
    Unit test for the testAndEvaluate function to ensure no errors occur during execution.
    """

    def setUp(self):
        """
        Set up a minimal dataset and model configuration for testing.
        """
        logger.info("Initializing evaluation unit test...")
        self.dataset_handler = ContractNLIDataset()

    def test_no_errors_in_test_and_evaluate(self):
        """
        Test that testAndEvaluate runs without raising any errors.
        """
        try:
            # Execute the function
            str_to_int_function = self.dataset_handler.get_str_to_int_function()
            int_to_str_function = self.dataset_handler.get_int_to_str_function()
            prompt_generator = self.dataset_handler.get_prompt_generator()
            result = testAndEvaluate(self.dataset_handler.dataset["test"].select(range(10)), models[0], str_to_int_function, int_to_str_function, prompt_generator, response_checker=self.dataset_handler.responseChecker)
            logger.info(f"Result of testAndEvaluate: {result}")
            


            # Check that the result is a dictionary and contains expected keys
            self.assertIsInstance(result, dict, "Result should be a dictionary.")
            self.assertIn("accuracy", result, "Result should include 'accuracy'.")
            self.assertIn("f1_weighted", result, "Result should include 'f1_weighted'.")
            
            logger.info(f"Saving Result to file: {result}")

            save_result_to_file(result, {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "model": "Llama-3.1-8B"}, "unitTest_results.json", mode="a")
        except Exception as e:
            self.fail(f"testAndEvaluate raised an exception: {str(e)}")


if __name__ == "__main__":
    unittest.main()
