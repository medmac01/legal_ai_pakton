"""
Description:
AWS Bedrock API integration module for accessing foundation models hosted on Amazon Bedrock. Provides bedrockApiCall
function with support for various model formats (prompt-based and message-based), comprehensive error handling,
retry logic for rate limiting, and token usage tracking. Supports models like Llama, Mistral, and Claude.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date  : 2025/07/08
"""

import boto3, json
from botocore.exceptions import ClientError
import os
from src.experimentsLibrary.logging_config import get_logger
import time 

from src.experimentsLibrary.exceptions import InvalidOutputException, handle_retry

# Get a logger for this module
logger = get_logger(__name__)

def is_rate_limit_error(err):
    """
    Checks if an exception is caused by exceeding API rate limits.

    Args:
        err (Exception): Exception object to check.

    Returns:
        bool: True if the error is a rate limit error; False otherwise.
    """
    if isinstance(err, ClientError):
        error_code = err.response["Error"]["Code"]
        return error_code == "ThrottlingException" or error_code == "RequestLimitExceeded"
    return False

def bedrockApiCall(model, system_prompt, user_prompt, maxRetries = 5, response_checker=None):
    """
    Invokes the Bedrock API with retries for specific exceptions, 
    such as rate limit errors or invalid outputs. Ensures the client 
    connection is closed properly after use.

    Args:
        model (dict): Model configuration, including the `id` and `prompt_format`.
        system_prompt (str): System-level instructions for the model.
        user_prompt (str): User-level input for the model.
        maxRetries (int): Maximum number of retries for failed requests.
        response_checker (callable, optional): A function to validate the response. 
            It should accept a response string and return a dict with the modified string and a boolean. 
            The string may be modified to isolate the desired output.
            The boolean indicates whether the response is valid.
            If none is given no validation happens
            output dict {"modifiedResponse": string, "isValid": boolean}

    Returns:
        tuple: (response_text, (input_tokens, output_tokens)).
            - response_text (str): Generated text from the LLM.
            - (input_tokens, output_tokens) (tuple): Token counts for the request.

    Raises:
        Exception: If retries are exhausted.
    """
        
    # Create a Bedrock Runtime client in the AWS Region of your choice.
    client = boto3.client(
        service_name="bedrock-runtime",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name=os.environ["AWS_REGION_NAME"],
    )

    # Check if the model uses prompt-based or message-based formatting
    if "prompt_format" in model:
        # Use the prompt-based format (Llama, Mistral)
        prompt = model["prompt_format"].format(SYSTEM_PROMPT=system_prompt, USER_PROMPT=user_prompt)
        request = json.dumps({**model["args"], "prompt": prompt})  # Merge default args
    elif "messages_format" in model:
        # Use the messages-based format (Claude)
        messages = model["messages_format"](user_prompt)
        request = json.dumps({**model["args"], "anthropic_version": "bedrock-2023-05-31", "system": str(system_prompt), "messages": messages})  # Merge default args
    else:
        raise ValueError("Model configuration missing 'prompt_format' or 'messages_format' key")
    
    retries = 0

    # retry in case of an error until you succeed 
    while retries < maxRetries:
        try:
            # Invoke the model with the request
            response = client.invoke_model(modelId=model["id"], body=request)
            time.sleep(1)  # Brief pause between requests
            
            # Retrieve token counts from the response headers
            input_tokens = int(response['ResponseMetadata']['HTTPHeaders']['x-amzn-bedrock-input-token-count'])
            output_tokens = int(response['ResponseMetadata']['HTTPHeaders']['x-amzn-bedrock-output-token-count'])
            
            # Decode the response body
            model_response = json.loads(response["body"].read())
            
            # Extract response text based on model type, as they return differently formatted outputs
            response_text = model["response_extractor"](model_response)
            
            logger.debug("bedrockApiCall completed successfully")


            # Validate the response if a checker function is provided
            if response_checker:
                temp = response_checker(response_text)
                response_text, is_valid = temp["modifiedResponse"], temp["isValid"]
                if not is_valid:
                    raise InvalidOutputException(f"Invalid response: {response_text}")

            # Return the response text and token counts
            return response_text, (input_tokens, output_tokens)

        except InvalidOutputException as e:
            retries = handle_retry(str(e), retries, maxRetries, backoff=True)
        except ClientError as e:
            if is_rate_limit_error(e):
                retries = handle_retry("Rate limit error detected.", retries, maxRetries, backoff=True)
            else:
                retries = handle_retry(e.response["Error"]["Message"], retries, maxRetries)
        except Exception as e:
            retries = handle_retry(str(e), retries, maxRetries)
        
        finally:
            # Ensure the client connection is closed
            client.close()