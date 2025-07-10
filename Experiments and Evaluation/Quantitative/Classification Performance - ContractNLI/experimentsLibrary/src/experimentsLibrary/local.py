"""
Description:
Local model execution module for running language models locally using transformers. Provides localApiCall function
with comprehensive error handling, retry logic, and support for various model architectures. Handles tokenization,
prompt formatting, and model inference with configurable parameters and response validation.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date  : 2025/07/08
"""

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import torch
import traceback
from src.experimentsLibrary.exceptions import InvalidOutputException
from src.experimentsLibrary.localModelManager import global_model_manager   

from src.experimentsLibrary.logging_config import get_logger
logger = get_logger(__name__)

@retry(
    stop=stop_after_attempt(5),  # Stop retrying after 5 attempts
    wait=wait_exponential(multiplier=10, min=1, max=600),  # Exponential backoff
    retry=retry_if_exception_type((InvalidOutputException, ValueError, RuntimeError, Exception)),  # Retry for specific exceptions
)
def localApiCall(model, system_prompt, user_prompt, response_checker=None):
    """
    Generates a response using a local model with retry logic for handling exceptions.

    Args:
        model (dict): Dictionary containing model configuration.
        system_prompt (str): The system prompt defining the model's role or context.
        user_prompt (str): The user input query.
        response_checker (function, optional): Function to validate and modify the response.

    Returns:
        str: The model's response text.
    """
    try:

        # Get model and tokenizer based on the model name, create it if there isnt already one
        modelObj, tokenizer = global_model_manager.get_model_and_tokenizer(model['id'], model['quantization_level'])

        # Determine message structure
        if "prompt_format" in model and "system" in model["prompt_format"] and "user" in model["prompt_format"]:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        elif "prompt_format" in model and "user" in model["prompt_format"]:
            messages = [
                {"role": "user", "content": system_prompt + user_prompt},
            ]
        else:
            raise ValueError("Invalid model configuration: 'prompt_format' must contain 'user' and/or 'system'.")

        # should handle the tokenizers where the chat template doesnt exist
        if not hasattr(tokenizer, "chat_template") or tokenizer.chat_template is None:
            if all("role" in msg and "content" in msg for msg in messages):
                # Concatenate messages in a basic format
                prompt = ""
                for msg in messages:
                    if msg["role"] == "system":
                        prompt += f"System: {msg['content']}\n"
                    elif msg["role"] == "user":
                        prompt += f"User: {msg['content']}\n"
                    elif msg["role"] == "assistant":
                        prompt += f"Assistant: {msg['content']}\n"
                    else:
                        raise ValueError(f"Unknown role in message: {msg['role']}")
            else:
                raise ValueError("Invalid messages structure: All messages must have 'role' and 'content'.")
        else:
            prompt = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )

        # Tokenize and move to CUDA
        first_device = next(modelObj.parameters()).device
        encoded_input = tokenizer(prompt, return_tensors="pt", padding=True).to(first_device)

        # Prepare generation arguments
        generation_args = {
            **model["args"],
            "do_sample": True,
            "input_ids": encoded_input.input_ids,  # Keep as PyTorch tensor
            "attention_mask": encoded_input.attention_mask,  # Keep as PyTorch tensor
            "pad_token_id": tokenizer.pad_token_id,
            "eos_token_id": tokenizer.eos_token_id
        }

        if "prompt_format" in model and "eos_token_needed" in model["prompt_format"]:
            generation_args["eos_token_id"] = [tokenizer.eos_token_id, tokenizer.convert_tokens_to_ids("<|eot_id|>")]

        #Generate output
        with torch.no_grad():
            output = modelObj.generate(**generation_args)

        # Extract and decode response
        response_start = encoded_input.input_ids.size(-1)
        response = output[0][response_start:] if response_start < output[0].size(0) else output[0]
        output_text = tokenizer.decode(response, skip_special_tokens=True)
        logger.info("input prompt: %s", prompt)
        logger.info("output: %s", output_text)
        # Validate the response if a checker function is provided
        if response_checker:
            temp = response_checker(output_text)
            output_text, is_valid = temp["modifiedResponse"], temp["isValid"]
            if not is_valid:
                raise InvalidOutputException(f"Invalid response: {output_text}")

        # Calculate input and output token counts
        input_tokens = encoded_input.input_ids.numel()  # Total number of input tokens
        output_tokens = response.numel()  # Total number of output tokens
        return output_text.strip(), (input_tokens, output_tokens)

    except ValueError as e:
        logger.error(f"ValueError: {e}\nTraceback: {traceback.format_exc()}", exc_info=True)
        raise  # Raise exception to trigger retry logic
    except RuntimeError as e:
        logger.error(f"RuntimeError (likely CUDA-related): {e}\nTraceback: {traceback.format_exc()}", exc_info=True)
        raise  # Raise exception to trigger retry logic
    except InvalidOutputException as e:
        logger.error(f"InvalidOutputException: {e}")
        raise  # Raise exception to trigger retry logic
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Raise exception to trigger retry logic
