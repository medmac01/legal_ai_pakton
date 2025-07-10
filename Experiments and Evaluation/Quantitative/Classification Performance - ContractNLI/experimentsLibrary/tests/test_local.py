import unittest
from src.experimentsLibrary.local import localApiCall
from src.experimentsLibrary.models import models
from src.experimentsLibrary.huggingfaceDatasets import ContractNLIDataset # type: ignore

from src.experimentsLibrary.logging_config import get_logger

# Get a logger for this module
logger = get_logger(__name__)

class TestLocalApiCall(unittest.TestCase):
    """
    Unit tests for the localApiCall function.
    """

    def test_simple_communication(self):
        """
        Test that localApiCall executes without errors and returns a valid response and token counts.
        """
        # Arrange
        model = models[5]
        prompt = "You are a helpful lawyer's assistant"
        query = "Give me a brief description about NDA contracts"

        # Act
        response_text, (input_tokens, output_tokens) = localApiCall(model, prompt, query)
        logger.info(f"Response Text: {response_text}")

        # Assert response text
        self.assertIsNotNone(response_text, "The response text should not be None.")
        self.assertIsInstance(response_text, str, "The response text should be a string.")
        self.assertGreater(len(response_text), 0, "The response text should not be empty.")

        # Assert token counts
        self.assertIsInstance(input_tokens, int, "Input tokens should be an integer.")
        self.assertIsInstance(output_tokens, int, "Output tokens should be an integer.")
        self.assertGreaterEqual(input_tokens, 0, "Input tokens should be non-negative.")
        self.assertGreaterEqual(output_tokens, 0, "Output tokens should be non-negative.")

    def test_empty_query(self):
        """
        Test that localApiCall handles an empty query string gracefully.
        """
        # Arrange
        model = models[5]
        prompt = "You are a helpful lawyer's assistant"
        query = ""

        # Act
        response_text, (input_tokens, output_tokens) = localApiCall(model, prompt, query)

        # Assert response text
        self.assertIsNotNone(response_text, "The response text should not be None.")
        self.assertIsInstance(response_text, str, "The response text should be a string.")
        self.assertGreater(len(response_text), 0, "The response text should not be empty.")

        # Assert token counts
        self.assertIsInstance(input_tokens, int, "Input tokens should be an integer.")
        self.assertIsInstance(output_tokens, int, "Output tokens should be an integer.")
        self.assertGreaterEqual(input_tokens, 0, "Input tokens should be non-negative.")
        self.assertGreaterEqual(output_tokens, 0, "Output tokens should be non-negative.")

    def test_one_contractNLI_sample(self):
        """
        Test that localApiCall executes without errors and returns a valid response for a contract NLI sample.
        """
        dataset_handler = ContractNLIDataset()

        # Arrange
        model = models[5]
        prompt_generator = dataset_handler.get_prompt_generator()
        prompt, query = prompt_generator(dataset_handler.dataset["test"][0])

        # Act
        response_text, (input_tokens, output_tokens) = localApiCall(model, prompt, query)
        logger.info(f"Model Answered: {response_text}")
        logger.info(f"Correct Answer: {dataset_handler.label_feature.int2str(dataset_handler.dataset['test'][0]['label']).upper()}")

        # Assert response text
        self.assertIsNotNone(response_text, "The response text should not be None.")
        self.assertIsInstance(response_text, str, "The response text should be a string.")
        self.assertGreater(len(response_text), 0, "The response text should not be empty.")

        # Assert token counts
        self.assertIsInstance(input_tokens, int, "Input tokens should be an integer.")
        self.assertIsInstance(output_tokens, int, "Output tokens should be an integer.")
        self.assertGreaterEqual(input_tokens, 0, "Input tokens should be non-negative.")
        self.assertGreaterEqual(output_tokens, 0, "Output tokens should be non-negative.")

if __name__ == "__main__":
    unittest.main()
