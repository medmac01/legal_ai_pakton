"""
Description:
Anthropic API integration module for Claude language models. Provides anthropicApiCall function with comprehensive
error handling, retry logic, and token usage tracking. Supports Claude-3 Sonnet and Opus models with configurable
parameters, response validation, and exponential backoff for rate limiting and API errors.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date  : 2025/07/08
"""

import anthropic
import os
import time
from typing import Tuple, Optional, Dict, Any, Callable

from src.experimentsLibrary.logging_config import get_logger
from src.experimentsLibrary.exceptions import InvalidOutputException

# Get a logger for this module
logging = get_logger(__name__, log_file = 'anthropic.log')

# Import libraries for retry logic
from httpx import HTTPStatusError
from tenacity import (retry, stop_after_attempt, wait_exponential, retry_if_exception_type)

# Initialize Anthropic client with API key from environment variables
anthropic_client = None
if "ANTHROPIC_API_KEY" in os.environ:
    anthropic_client = anthropic.Anthropic(
        api_key=os.environ["ANTHROPIC_API_KEY"],
    )

@retry(
    stop=stop_after_attempt(5),  # Stop retrying after 5 attempts
    wait=wait_exponential(multiplier=10, min=1, max=600),  # Exponential backoff
    retry=retry_if_exception_type((InvalidOutputException, anthropic.APIError, anthropic.APIConnectionError, anthropic.RateLimitError, HTTPStatusError, Exception)),  # Retry only for specified exceptions
)
def anthropicApiCall(model, system_prompt, user_prompt, response_checker=None):
    """
    Sends a request to the Anthropic API using the Messages endpoint.

    Args:
        model (dict): 
            - Type: `dict`
            - Description: A dictionary containing model-specific configuration.
            - Keys:
                - `"id"` (str): The model ID (e.g., "claude-3-sonnet-20240229" or "claude-3-opus-20240229").
                - `"args"` (dict, optional): Additional arguments for the Anthropic API call 
                (e.g., temperature, max_tokens, top_p).
        
        system_prompt (str): 
            - Type: `str`
            - Description: The system prompt to guide the AI's behavior, defining its role 
            or context (e.g., "You are a helpful assistant.").

        user_prompt (str): 
            - Type: `str`
            - Description: The input query or task provided by the user.

        response_checker (function, optional): 
            - Type: `callable`
            - Description: An optional function to validate and modify the response from 
            the API.
            - Input: Takes the API response as input.
            - Output: Returns a dictionary with:
                - `"modifiedResponse"` (str): The potentially modified response.
                - `"isValid"` (bool): Indicates whether the response is valid.
            - Default: `None` (no validation applied).

    Returns:
        tuple:
            - `response_text` (str): The content of the AI's response.
            - `token_usage` (tuple): A tuple containing:
                - `input_tokens` (int): The number of tokens used in the input.
                - `output_tokens` (int): The number of tokens used in the generated response.

        If an error occurs, returns `None`.
    """
    if not anthropic_client:
        logging.error("Anthropic client not initialized. ANTHROPIC_API_KEY environment variable must be set.")
        return None
    
    try:
        # Prepare API call arguments
        api_args = {
            "model": model["id"],
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt
                        }
                    ]
                }
            ]
        }
        
        # Add any additional arguments from model["args"] if provided
        if model.get("args"):
            api_args.update(model["args"])
        
        logging.debug(f"Sending request to Claude with args: {api_args}")
        # Make the API call
        response = anthropic_client.messages.create(**api_args)
        logging.debug("Request sent to Claude successfully.")
        
        # Extract the response text
        response_text = response.content[0].text
        logging.debug(f"Response received: {response_text}")
        # Validate the response if a checker function is provided
        if response_checker:
            temp = response_checker(response_text)
            response_text, is_valid = temp["modifiedResponse"], temp["isValid"]
            if not is_valid:
                raise InvalidOutputException(f"Invalid response: {response_text}")
        
        # Return the response and token usage
        return response_text, (response.usage.input_tokens, response.usage.output_tokens)
    
    except InvalidOutputException as e:
        logging.error(f"Invalid Response: {e}")
        raise  # Raise the exception to trigger retry logic
    except anthropic.RateLimitError as e:
        # Handle rate-limiting errors
        retry_after = int(getattr(e, "retry_after", 0) or 0)
        if retry_after > 0:
            logging.error(f"Rate limit hit; retrying after {retry_after} seconds.")
            time.sleep(retry_after)
        else:
            logging.error("Rate limit hit; retrying with exponential backoff.")
        raise  # Raise the exception to trigger retry logic
    except (anthropic.APIError, anthropic.APIConnectionError) as e:
        # Handle generic API or connection errors
        logging.error(f"API error: {e}")
        raise  # Raise the exception to trigger retry logic
    except HTTPStatusError as e:
        # Handle HTTP status errors
        retry_after = int(e.response.headers.get("Retry-After", 0))
        if retry_after > 0:
            logging.error(f"HTTP error with retry-after: {retry_after} seconds.")
            time.sleep(retry_after)
        else:
            logging.error(f"HTTP error: {e}")
        raise  # Raise the exception to trigger retry logic
    except Exception as e:
        # Handle unexpected errors
        logging.error(f"An error occurred while sending the request to Claude: {e}")
        raise  # Raise the exception to trigger retry logic