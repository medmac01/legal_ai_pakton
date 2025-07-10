"""
Description:
IBM WatsonX AI integration module for accessing foundation models on IBM's WatsonX platform. Provides
watsonxApiCall function with comprehensive error handling, retry logic, and token usage tracking. Supports
various IBM WatsonX models with configurable parameters and response validation.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date  : 2025/07/08
"""

import os
import time
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.foundation_models.schema import TextChatParameters
from tenacity import (retry, stop_after_attempt, wait_exponential, retry_if_exception_type)

from src.experimentsLibrary.exceptions import InvalidOutputException
from src.experimentsLibrary.logging_config import get_logger

# Get a logger for this module
logger = get_logger(__name__)

@retry(
    stop=stop_after_attempt(5),  # Stop retrying after 5 attempts
    wait=wait_exponential(multiplier=10, min=1, max=600),  # Exponential backoff
    retry=retry_if_exception_type((InvalidOutputException, Exception)),  # Retry for specific exceptions
)
def watsonxApiCall(model, system_prompt, user_prompt, response_checker=None):
    """
    Sends a request to the IBM WatsonX AI API.

    Args:
        model (dict): Dictionary containing model configuration.
            - 'id' (str): The model ID (e.g., "meta-llama/llama-3-405b-instruct").
            - 'args' (dict, optional): Additional parameters like temperature.
            - 'project_id' (str): The WatsonX project ID.
        system_prompt (str): The system prompt defining context or instructions.
        user_prompt (str): The user input query.
        response_checker (function, optional): Function to validate and modify the response.

    Returns:
        tuple: (response_text, (input_tokens, output_tokens))
            - response_text (str): The content of the AI's response.
            - token_usage (tuple): A tuple containing token counts (estimated).

    Raises:
        Exception: If an error occurs during the API call.
    """
    try:
        # Get credentials from environment variables
        if not all(k in os.environ for k in ["WATSONX_URL", "WATSONX_API_KEY"]):
            raise ValueError("Environment variables WATSONX_URL and WATSONX_API_KEY must be set")

        # Initialize WatsonX credentials
        credentials = Credentials(
            url=os.environ["WATSONX_URL"],
            api_key=os.environ["WATSONX_API_KEY"],
        )

        # Get project ID from the model config or environment
        project_id = model.get("project_id") or os.environ.get("WATSONX_PROJECT_ID")
        if not project_id:
            raise ValueError("project_id must be provided in model config or WATSONX_PROJECT_ID environment variable")

        # Prepare parameters
        params = TextChatParameters(**model.get("args", {}))

        # Initialize the model
        watsonx_model = ModelInference(
            model_id=model["id"],
            credentials=credentials,
            project_id=project_id,
            params=params
        )

        # Format messages based on the model's expected structure
        if "messages_format" in model:
            # Use the model's custom messages format
            messages = model["messages_format"](user_prompt)
        else:
            # Default format with system and user messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

        # Record the start time to calculate tokens per second
        start_time = time.time()

        # Make the API call
        response = watsonx_model.chat(messages=messages)
        logger.debug("Request sent to WatsonX successfully")

        # Extract the content from the response
        response_text = response["choices"][0]["message"]["content"]

        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        # Estimate tokens (since WatsonX might not return explicit token counts)
        # This is a rough estimate based on words
        input_tokens = len((system_prompt + " " + user_prompt).split())
        output_tokens = len(response_text.split())

        logger.debug(f"WatsonX response received. Elapsed time: {elapsed_time:.2f}s")
        
        # Validate the response if a checker function is provided
        if response_checker:
            temp = response_checker(response_text)
            response_text, is_valid = temp["modifiedResponse"], temp["isValid"]
            if not is_valid:
                raise InvalidOutputException(f"Invalid response: {response_text}")

        return response_text, (input_tokens, output_tokens)

    except InvalidOutputException as e:
        logger.error(f"Invalid Response: {e}")
        raise  # Raise the exception to trigger retry logic
    except Exception as e:
        logger.error(f"An error occurred while sending the request to WatsonX: {e}")
        raise  # Raise the exception to trigger retry logic