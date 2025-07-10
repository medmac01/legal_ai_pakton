"""
Description:
Utility functions for model persistence including loading and saving trained machine learning models using pickle serialization for later use and deployment.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date : 2025/07/08
"""

import pickle
import os

# Function to load models for later use
def load_model(model_path):
    """Loads a saved model from a pickle file."""
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model

def save_models(overall_best_model, best_models, output_dir="models"):
    """Saves the best models to pickle files."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the overall best model
    with open(f"{output_dir}/best_overall_model.pkl", "wb") as f:
        pickle.dump(overall_best_model, f)
    
    # Save each best model by classifier type
    for classifier_type, model in best_models.items():
        with open(f"{output_dir}/best_{classifier_type.lower()}_model.pkl", "wb") as f:
            pickle.dump(model, f)
    
    print(f"Models saved in {output_dir} directory")