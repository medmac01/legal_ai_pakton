"""
Description:
OpenAI API integration module supporting both legacy (v0.28.0) and modern OpenAI API versions. Provides
openaiApiCall function with comprehensive error handling, retry logic, and token usage tracking. Supports
GPT models with configurable parameters, response validation, and version-specific API compatibility.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date  : 2025/07/08
"""

import openai
# Retrieve the OpenAI library version
openai_version = tuple(map(int, openai.__version__.split(".")))

import os
from src.experimentsLibrary.logging_config import get_logger
import time 

from src.experimentsLibrary.exceptions import InvalidOutputException

# Get a logger for this module
logging = get_logger(__name__)

# the following code is for open library version == 0.28 (the API structure has changed).
# suitable for automated calls as it has higher rate limits
if openai_version == (0, 28, 0):  # For version 0.28.0 
    
    from httpx import HTTPStatusError
    from tenacity import (retry, stop_after_attempt, wait_exponential, retry_if_exception_type)

    if "OPENAI_API_KEY" in os.environ:
        openai.api_key = os.environ["OPENAI_API_KEY"]

    if "BASE_URL" in os.environ:
        openai.api_base = os.environ["BASE_URL"]

    @retry(
        stop=stop_after_attempt(5), # Stop retrying after 5 attempts
        wait=wait_exponential(multiplier=10, min=1, max=600), # Exponential backoff 
        retry=retry_if_exception_type((InvalidOutputException, openai.APIError, HTTPStatusError, Exception)), # Retry only for specified exceptions
    )
    def openaiApiCall(model, system_prompt, user_prompt, response_checker=None): 
        """
        Sends a request to the OpenAI API using the ChatCompletion endpoint.

        Args:
            model (dict): 
                - Type: `dict`
                - Description: A dictionary containing model-specific configuration.
                - Keys:
                    - `"id"` (str): The model ID (e.g., "gpt-3.5-turbo" or "gpt-4").
                    - `"args"` (dict, optional): Additional arguments for the OpenAI API call 
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
                    - `prompt_tokens` (int): The number of tokens used in the input prompt.
                    - `completion_tokens` (int): The number of tokens used in the generated response.

            If an error occurs, returns `None`.
        """
        try:
            
            response = openai.ChatCompletion.create( # this is for the 0.28 version of openai
                model=model["id"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                **(model["args"] or {})  # Unpack args if provided, otherwise use an empty dictionary
            )
            logging.debug("Request sent to ChatGPT successfully.")
            
            # Explicitly check for HTTP status in response if necessary
            if response.get("status_code", 200) != 200:  # Example of status code inspection
                raise Exception(f"Non-200 status code received: {response['status_code']}")

            response_text = response['choices'][0]['message']['content']
            
            # Validate the response if a checker function is provided
            if response_checker:
                temp = response_checker(response_text)
                response_text, is_valid = temp["modifiedResponse"], temp["isValid"]
                if not is_valid:
                    raise InvalidOutputException(f"Invalid response: {response_text}")
            
            return response_text, (response.usage.prompt_tokens, response.usage.completion_tokens)
        
        except InvalidOutputException as e:
            logging.error(f"Invalid Response: {e}")
            raise  # Raise the exception to trigger retry logic
        except HTTPStatusError as e:
            # Handle rate-limiting errors
            # Check for 'Retry-After' header
            retry_after = int(e.response.headers.get("Retry-After", 0))
            if retry_after > 0:
                logging.error(f"Rate limit hit; retrying after {retry_after} seconds.")
                time.sleep(retry_after)
                raise  # Raise the exception to trigger retry logic
            else:
                logging.error("Rate limit hit; retrying with exponential backoff.")
                raise  # Raise the exception to trigger retry logic
        except openai.APIError as e:
            # Handle generic API or connection errors
            logging.error(f"API error: {e}")
            raise  # Raise the exception to trigger retry logic
        except Exception as e:
            # Handle unexpected errors
            logging.error(f"An error occurred while sending the request to ChatGPT: {e}")
            raise

# The following code is for the latest version (above 1.0) of the OpenAI library (the API calls have been updated).
# It has small limits on API calls and is not suitable for consecutive calls to GPT. The code for version 0.28 is preferred.
if openai_version > (0, 28, 0):  # For newer versions that 0.28.0     
    from openai import OpenAI, APIConnectionError, APIError, RateLimitError
    from httpx import HTTPStatusError
    from tenacity import (retry, stop_after_attempt, wait_exponential, retry_if_exception_type)

    # Initialize OpenAI client with API key from environment variables
    if "OPENAI_API_KEY" in os.environ:
        if "BASE_URL" in os.environ:
            openAIclient = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=os.environ["BASE_URL"])
        else:
            openAIclient = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    @retry(
        stop=stop_after_attempt(5), # Stop retrying after 5 attempts
        wait=wait_exponential(multiplier=5, min=1, max=60), # Exponential backoff with a delay range of 1 to 60 seconds
        retry=retry_if_exception_type((InvalidOutputException, RateLimitError, APIError, APIConnectionError, HTTPStatusError)), # Retry only for specified exceptions
    )
    def openaiApiCall(model, system_prompt, user_prompt, response_checker=None): 
        """
        Sends a request to the OpenAI API using the ChatCompletion endpoint.

        Args:
            model (dict): 
                - Type: `dict`
                - Description: A dictionary containing model-specific configuration.
                - Keys:
                    - `"id"` (str): The model ID (e.g., "gpt-3.5-turbo" or "gpt-4").
                    - `"args"` (dict, optional): Additional arguments for the OpenAI API call 
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
                    - `prompt_tokens` (int): The number of tokens used in the input prompt.
                    - `completion_tokens` (int): The number of tokens used in the generated response.

            If an error occurs, returns `None`.
        """
        try:
            response = openAIclient.chat.completions.create(
                model=model["id"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                **(model["args"] or {})  # Unpack args if provided, otherwise use an empty dictionary
            )
            logging.debug("Request sent to ChatGPT successfully.")
            
            response_text = response.choices[0].message.content
            logging.debug(f"response_text: {response_text}")
            # Validate the response if a checker function is provided
            if response_checker:
                temp = response_checker(response_text)
                response_text, is_valid = temp["modifiedResponse"], temp["isValid"]
                if not is_valid:
                    raise InvalidOutputException(f"Invalid response: {response_text}")
                
            return response_text, (response.usage.prompt_tokens, response.usage.completion_tokens)
        
        except InvalidOutputException as e:
            logging.error(f"Invalid Response: {e}")
            raise  # Raise the exception to trigger retry logic
        except (RateLimitError, HTTPStatusError) as e:
            # Handle rate-limiting errors
            # Check for 'Retry-After' header
            retry_after = int(e.response.headers.get("Retry-After", 0))
            if retry_after > 0:
                logging.error(f"Rate limit hit; retrying after {retry_after} seconds.")
                time.sleep(retry_after)
                raise  # Raise the exception to trigger retry logic
            else:
                logging.error("Rate limit hit; retrying with exponential backoff.")
                raise  # Raise the exception to trigger retry logic
        except (APIError, APIConnectionError) as e:
            # Handle generic API or connection errors
            logging.error(f"API error: {e}")
            raise  # Raise the exception to trigger retry logic
        except Exception as e:
            # Handle unexpected errors
            logging.error(f"An error occurred while sending the request to ChatGPT: {e}")
            return None # Return None to indicate failure