"""
Description:
Model evaluation module that tests language models on datasets and computes performance metrics. Provides the
testAndEvaluate function which processes datasets, handles model API calls, calculates accuracy and F1 scores,
and tracks predictions with reasoning. Supports incremental result saving and comprehensive error handling.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date  : 2025/07/08
"""

import traceback
from sklearn.metrics import accuracy_score, f1_score
from tqdm import tqdm  # Import tqdm for the progress bar
from src.experimentsLibrary.models import models, api_callers
from src.experimentsLibrary.utils import clean, save_temp_predictions_to_json
import os
import re

from src.experimentsLibrary.logging_config import get_logger

logger = get_logger(__name__)

def testAndEvaluate(dataset, model, str_to_int_labels, int_to_str_labels, prompt_generator, response_checker=None):
    """
    Tests the model on a given dataset and evaluates its performance using accuracy and F1 scores.

    Args:
        dataset (list of dict): 
            The dataset to evaluate the model on. Each dictionary in the list should include:

        model (dict): 
            The model configuration.

        str_to_int_labels (function): 
            A function that converts string labels to integer labels. 
            Used to standardize model responses into label integers.

        int_to_str_labels (function): 
            A function that converts integer labels to string labels.
            Used for interpreting and logging results with meaningful class names.

        response_checker (function, optional): 
            A function to validate and clean the responses from the model. 
            It takes a response string as input and returns a dictionary with:
            - "modifiedResponse" (str): Cleaned and standardized response text.
            - "isValid" (bool): Whether the response is valid.
            Defaults to None.

    Returns:
        dict: A dictionary containing:
            - "accuracy" (float): The accuracy of the model on the dataset.
            - "f1_weighted" (float): The weighted F1 score across all classes.
            - "f1_per_class" (dict): A dictionary mapping class names (string) to their F1 scores.
            - "predictions" (list): A list of predictions for the dataset, where invalid predictions are marked as -1.
    """
    logger.debug(f"Starting testAndEvaluate for model: {model['name']}")
    predictions = []
    prediction_data = []  # To store each prediction with metadata
    labels = []

    # Wrap the dataset with tqdm for progress tracking
    for idx, data_point in enumerate(tqdm(dataset, desc=f"Evaluating model: {model['name']}", unit="data point")):
        systemPrompt, userPrompt = prompt_generator(data_point)
        labels.append(data_point["label"])
        try:
            # Use the mapping to call the appropriate function
            if model["API"] in api_callers:
                response, token_counts = api_callers[model["API"]](model, systemPrompt, userPrompt, response_checker=response_checker)
            else:
                raise ValueError(f"Unsupported API type: {model['API']}")

            # reasoning in the response will be inside the <reasoning> tag
            # Regular expression to capture predicted_text and reasoning
            if "<reasoning>" in response and "</reasoning>" in response:
                predicted_text, reasoning = response.split("<reasoning>")
                reasoning = reasoning.replace("</reasoning>", "").strip()
                predicted_text = predicted_text.strip()
            else:
                predicted_text = response.strip()
                reasoning = "No reasoning provided"

            # Process and store the prediction
            predictions.append(str_to_int_labels(clean(predicted_text)))         
            
        except Exception as e:
            logger.error(f"Error processing data point {idx + 1}: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")  # Logs the full traceback  # Logs the full traceback
            predictions.append(-1)  # Use "error" as a placeholder prediction in case of failure

        prediction_data.append({
            "index": idx + 1,
            "original_label": data_point["label"],
            "prediction": predictions[-1],
            "user_prompt": userPrompt,
            "system_prompt": systemPrompt,
            "predicted_text": predicted_text,  
            "reasoning": reasoning,
            "result": "CORRECT" if predictions[-1] == data_point["label"] else "WRONG"
        })

        # Save incremental results
        save_temp_predictions_to_json(prediction_data, file_path="predictions_gemma.json")

        # Calculate and log metrics
        logger.debug(f"Current Evaluation metrics for model: {model['name']}")

        # Filter out invalid predictions (-1) and unpack valid predictions and labels
        valid_predictions, valid_labels = zip(
            *[(pred, label) for pred, label in zip(predictions, labels) if pred != -1]
        )

        if valid_predictions:
            accuracy = accuracy_score(valid_labels, valid_predictions)
            # Calculate F1 scores
            f1_weighted = f1_score(valid_labels, valid_predictions, average="weighted")
            f1_per_class = f1_score(valid_labels, valid_predictions, average=None)
            unique_classes = sorted(set(labels))
            str_classes = [int_to_str_labels(class_label) for class_label in unique_classes]

            logger.info(f"Progress Metrics for model: {model['name']}")
            logger.info(f"Valid predictions: {len(valid_predictions)} out of {len(dataset)} total datapoints.")
            logger.info(f"Accuracy: {accuracy:.4f}")
            logger.info(f"Weighted F1 Score: {f1_weighted:.4f}")
            for class_label, f1 in zip(unique_classes, f1_per_class):
                    logger.info(f"F1 Score (Class {int_to_str_labels(class_label)}): {f1:.4f}")

    return {"accuracy": accuracy, "f1_weighted": f1_weighted, "f1_per_class": dict(zip(str_classes, f1_per_class)), "predictions": predictions}
