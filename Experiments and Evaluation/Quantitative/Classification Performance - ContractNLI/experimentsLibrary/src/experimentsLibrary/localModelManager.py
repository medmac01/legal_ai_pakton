"""
Description:
Local model management system for loading, caching, and configuring Hugging Face transformers models. Provides
localModelManager class with support for quantization levels, model caching, and efficient memory management.
Handles model authentication, loading with different precision levels, and maintains model instances globally.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date  : 2025/07/08
"""

from huggingface_hub import login
import os
import re
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from src.experimentsLibrary.logging_config import get_logger

logger = get_logger(__name__)


class localModelManager:
    """
    A class to manage the loading and caching of models and tokenizers.

    Attributes:
        models (dict): A dictionary to store models and tokenizers keyed by their names.
    """

    def __init__(self, model_cache_dir="model_cache"):
        """
        Initializes the ModelManager instance, sets up the model cache, and sets the quantization level.
        """

        self.model_cache_dir = model_cache_dir
        os.makedirs(self.model_cache_dir, exist_ok=True)

        HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
        if not HUGGINGFACE_TOKEN:
            raise EnvironmentError("HUGGINGFACE_TOKEN environment variable is not set.")
        # Login to Hugging Face
        login(token=HUGGINGFACE_TOKEN)

        self.models = {}  # Dictionary to store models and tokenizers by name
        logger.info("ModelManager initialized.")

    def get_model_and_tokenizer(self, model_id, quantization_level="no quantization"):
        """
        Retrieves the model and tokenizer for the given model name.
        If the model is not already cached, it will be loaded and added to the cache.

        Args:
            model_id (str): The name or path of the model to load.
            quantization_level (str): Determines the quantization level. Options are:
                - "no quantization": Load the model without quantization.
                - "lowest": Load the model with 16 bit accuracy.
                - "low": Apply 8-bit quantization with nf4.
                - "normal": Apply 4-bit quantization with nf4.
                - "high": Apply 4-bit quantization with nf4 and with double quantization.
                - "aggressive": Apply 4-bit quantization with double quantization and FP4.
        Returns:
            tuple: A tuple containing the model and tokenizer.

        Raises:
            ValueError: If the `model_id` is invalid or loading fails.
        """
        try:

            if quantization_level not in [
                "no quantization",
                "lowest",
                "low",
                "normal",
                "high",
                "aggressive",
            ]:
                raise ValueError(
                    "Invalid quantization_level. Choose from 'no quantization', 'lowest', 'low', 'normal', 'high' or 'aggressive'."
                )

            # Check if the model already exists in the cache
            if (
                model_id in self.models
                and self.models[model_id]["quantization_level"] == quantization_level
            ):
                logger.info(f"Model '{model_id}' retrieved from cache.")
                return (
                    self.models[model_id]["model"],
                    self.models[model_id]["tokenizer"]
                )

            # Check if model is in persistent storage
            sanitized_model_id = re.sub(r'[<>:"/\\|?*]', "_", model_id)
            model_path = os.path.join(
                self.model_cache_dir, sanitized_model_id, quantization_level
            )
            if os.path.exists(model_path):

                # if the weights of the model saved quantized, we dont need to quantize them again
                logger.info(
                    f"Model '{model_id}' found in local cache. Loading from disk..."
                )

                model = AutoModelForCausalLM.from_pretrained(
                    model_path, trust_remote_code=True, device_map="auto"
                )

                tokenizer = AutoTokenizer.from_pretrained(
                    model_path, padding_side="left"
                )

                #Set pad_token_id if it is None
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                    logger.info(f"Set tokenizer.pad_token_ = tokenizer.eos_token")

                logger.info(f"Model '{model_id}' loaded successfully from disk.")
                self.models[model_id] = {
                    "model": model,
                    "tokenizer": tokenizer,
                    "quantization_level": quantization_level,
                }
                logger.info(f"Model and tokenizer for '{model_id}' cached.")
                return model, tokenizer

            # Configure quantization
            # should check bfloat as well
            bnb_config = None
            if quantization_level == "low":
                bnb_config = BitsAndBytesConfig(
                    load_in_8bit=True,
                    bnb_4bit_use_double_quant=False,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.float16,
                )
                logger.info(
                    f"Quantization configuration (low) for model '{model_id}' initialized."
                )
            elif quantization_level == "normal":
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_use_double_quant=False,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.float16,
                )
                logger.info(
                    f"Quantization configuration (normal) for model '{model_id}' initialized."
                )
            elif quantization_level == "high":
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.float16,
                )
                logger.info(
                    f"Quantization configuration (high) for model '{model_id}' initialized."
                )
            elif quantization_level == "aggressive":
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="fp4",
                    bnb_4bit_compute_dtype=torch.float16,
                )
                logger.info(
                    f"Quantization configuration (aggressive) for model '{model_id}' initialized."
                )

            logger.info(f"Loading model '{model_id}'...")

            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if quantization_level == "lowest" else None,
                quantization_config=(
                    bnb_config
                    if quantization_level not in ["no quantization", "lowest"]
                    else None
                ),
                device_map="auto",
                trust_remote_code=True,
            )

            logger.info(f"Model '{model_id}' loaded successfully.")

            # Load the tokenizer
            logger.info(f"Loading tokenizer for model '{model_id}'...")
            tokenizer = AutoTokenizer.from_pretrained(
                model_id, trust_remote_code=True, padding_side="left"
            )

            #Set pad_token_id if it is None
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
                logger.info(f"Set tokenizer.pad_token_ = tokenizer.eos_token")

            logger.info(f"Tokenizer for model '{model_id}' loaded successfully.")

            # Save model to persistent storage
            logger.info(
                f"Saving model '{model_id}' to local cache at '{model_path}'..."
            )
            model.save_pretrained(model_path)
            tokenizer.save_pretrained(model_path)

            # Store the model and tokenizer in the cache
            self.models[model_id] = {
                "model": model,
                "tokenizer": tokenizer,
                "quantization_level": quantization_level,
            }
            logger.info(f"Model and tokenizer for '{model_id}' cached.")

            return model, tokenizer

        except Exception as e:
            logger.error(f"Error occurred while loading model '{model_id}': {e}")
            raise ValueError(
                f"Failed to load model '{model_id}'. Check the model path or configuration."
            ) from e


global_model_manager = localModelManager()
