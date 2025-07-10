"""
Description:
Utility functions for data processing, file operations, and result management. Provides clean function for text
preprocessing, save_result_to_file for JSON result storage, and various helper functions for data manipulation
and temporary file management across the experiments library.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date  : 2025/07/08
"""

import string
import json
import os

# clean the response word removing spaces and punctuation
def clean(response):
    return response.replace('"', '').replace("'", '').strip().lower().translate(str.maketrans('', '', string.punctuation))

def save_result_to_file(result, additional_info, file_path="results.json", mode="a"):
    """
    Saves a result and additional information into a file in JSON format.

    Args:
        result (dict): The result JSON object to save.
        additional_info (dict): Additional information to include with the result.
        file_path (str): Path to the file where the data should be saved.
        mode (str): File write mode, either "a" (append) or "w" (overwrite).
            Default is "a" (append).
    
    Raises:
        ValueError: If `mode` is not "a" or "w".
    """
    if mode not in {"a", "w"}:
        raise ValueError("Invalid mode. Use 'a' for append or 'w' for overwrite.")

    # Combine result and additional info into one dictionary
    combined_data = {
        "result": result,
        "additional_info": additional_info
    }

    # Check if the file already exists and mode is append
    if mode == "a" and os.path.exists(file_path):
        # Append to existing file
        with open(file_path, "r+", encoding="utf-8") as file:
            try:
                # Load existing data
                existing_data = json.load(file)
                if isinstance(existing_data, list):
                    existing_data.append(combined_data)
                else:
                    # If existing data is not a list, convert it to a list
                    existing_data = [existing_data, combined_data]
            except json.JSONDecodeError:
                # If file is empty or invalid, start fresh
                existing_data = [combined_data]

            # Write back to the file
            file.seek(0)
            json.dump(existing_data, file, indent=4)
    else:
        # Overwrite or create new file
        with open(file_path, mode, encoding="utf-8") as file:
            json.dump([combined_data], file, indent=4)

    print(f"Data saved to {file_path}")

# example usage
# result = {"prediction": "ENTAILMENT", "confidence": 0.92}
# additional_info = {"timestamp": "2024-11-25 15:45:00", "model": "Llama-3.1-8B"}

# save_result_to_file(result, additional_info, "results.json", mode="a")

"""
Formatting utilities for rag
"""
from typing import Dict, Any, List, Optional, Union

from langchain_core.documents import Document

def format_documents(documents: List[Document]) -> str:

    if not documents:
        return "No documents were retrieved."
    
    # Format each document with <Document> tags
    formatted_docs = []
    
    for i, doc in enumerate(documents):
        formatted_docs.append(f"<Span index='{i+1}'/>\n{doc.page_content}\n</Span>")
    
    all_docs = "\n\n".join(formatted_docs)
    return f"<Spans>\n{all_docs}\n</Spans>"

from src.experimentsLibrary.logging_config import get_logger

logger = get_logger(__name__)

def save_temp_predictions_to_json(predictions, file_path="predictions.json"):
    """Helper function to save predictions to a JSON file."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(predictions, f, ensure_ascii=False, indent=4)
        logger.info(f"Predictions successfully saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving predictions to JSON: {e}")
