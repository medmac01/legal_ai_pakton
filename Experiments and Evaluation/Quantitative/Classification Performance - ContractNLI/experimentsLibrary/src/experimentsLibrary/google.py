"""
Description:
Google Gemini API integration module for accessing Google's generative AI models. Provides googleApiCall function
with comprehensive error handling, retry logic, and token usage tracking. Supports Google Gemini models with
configurable parameters, response validation, and exponential backoff for HTTP errors.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date  : 2025/07/08
"""

from google import genai
from google.genai import types

import os
import time
from typing import Tuple, Optional, Dict, Any, Callable

from src.experimentsLibrary.logging_config import get_logger
from src.experimentsLibrary.exceptions import InvalidOutputException

# Get a logger for this module
logging = get_logger(__name__, log_file = 'experimentsGoogle.log')

# Import libraries for retry logic
from httpx import HTTPStatusError
from tenacity import (retry, stop_after_attempt, wait_exponential, retry_if_exception_type)


client = None
if "GOOGLE_API_KEY" in os.environ:
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

@retry(
    stop=stop_after_attempt(5),  # Stop retrying after 5 attempts
    wait=wait_exponential(multiplier=10, min=1, max=600),  # Exponential backoff
    retry=retry_if_exception_type((InvalidOutputException, HTTPStatusError, Exception)),  # Retry only for specified exceptions
)
def googleApiCall(model, system_prompt, user_prompt, response_checker=None):

    if not client:
        logging.error("Google client not initialized. GOOGLE_API_KEY environment variable must be set.")
        return None
    
    try:
        # Combine system prompt and user prompt if system prompt exists
        content = user_prompt
        if system_prompt:
            content = f"{system_prompt}\n\n{user_prompt}"
        
        # Create the GenerateContentConfig object with all parameters
        generate_config = types.GenerateContentConfig(**model.get("args"))
        
        logging.debug(f"Sending request to Google Gemini with model: {model['id']} and config: {generate_config}")
        
        # Make the API call
        response = client.models.generate_content(
            model=model["id"],
            config=generate_config,
            contents=content
        )
        logging.debug("Request sent to Google Gemini successfully.")
        
        # Extract the response text
        response_text = response.text
        logging.debug(f"Response received: {response_text}")
        
        # Validate the response if a checker function is provided
        if response_checker:
            temp = response_checker(response_text)
            response_text, is_valid = temp["modifiedResponse"], temp["isValid"]
            if not is_valid:
                raise InvalidOutputException(f"Invalid response: {response_text}")
        
        # Extract token usage if available - fixing to access attributes directly
        usage_metadata = getattr(response, "usage_metadata", None)
        input_tokens = getattr(usage_metadata, "input_tokens", 0) if usage_metadata else 0
        output_tokens = getattr(usage_metadata, "output_tokens", 0) if usage_metadata else 0
        
        # Return the response and token usage
        return response_text, (input_tokens, output_tokens)
    
    except InvalidOutputException as e:
        logging.error(f"Invalid Response: {e}")
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
        logging.error(f"An error occurred while sending the request to Google Gemini: {e}")
        raise  # Raise the exception to trigger retry logic