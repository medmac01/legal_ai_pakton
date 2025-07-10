"""
Description:
Logging and results management module that handles feature importance extraction, model parameter logging, performance metrics storage, and comprehensive result tracking for machine learning experiments.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date : 2025/07/08
"""

import pandas as pd
import numpy as np

from datetime import datetime
import os

from sklearn.model_selection import KFold

import json

from .evaluation import evaluate_model

def get_feature_importance(estimator, feature_names):
    """Gets feature importance if available and returns as DataFrame."""
    if hasattr(estimator, 'coef_'):
        importances = np.abs(estimator.coef_[0])
        feature_importance = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
        return feature_importance.sort_values(by='Importance', ascending=False)
    elif hasattr(estimator, 'feature_importances_'):
        importances = estimator.feature_importances_
        feature_importance = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
        return feature_importance.sort_values(by='Importance', ascending=False)
    else:
        return pd.DataFrame({'Feature': ['N/A'], 'Importance': [0]})

def log_results(overall_best_model, best_models, best_scores, X_train, y_train, X_test, y_test, output_dir="logs"):
    """Logs the parameters, coefficients, and scores to a JSON file."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate a timestamp for the log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{output_dir}/meta_learning_results_{timestamp}.json"
    
    # Create a dictionary to store all results
    results = {
        'timestamp': timestamp,
        'train_test_info': {
            'train_size': len(X_train),
            'test_size': len(X_test),
            'train_class_distribution': pd.Series(y_train).value_counts().to_dict(),
            'test_class_distribution': pd.Series(y_test).value_counts().to_dict()
        },
        'overall_best_model': {
            'type': overall_best_model.named_steps['classifier'].__class__.__name__,
            'parameters': str(overall_best_model.get_params()),
            'cv_score': float(best_scores[overall_best_model.named_steps['classifier'].__class__.__name__])
        },
        'models': {}
    }
    
    # Create a KFold object for consistent evaluation
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    
    # For each classifier, log its parameters, importance, and evaluation metrics
    for classifier_type, model in best_models.items():
        classifier = model.named_steps['classifier']
        
        # Get feature importance
        feature_importance = get_feature_importance(classifier, X_train.columns)
        
        # Get comprehensive evaluation metrics
        eval_metrics = evaluate_model(model, X_train, y_train, X_test, y_test, cv)
        
        # Store in results dictionary
        results['models'][classifier_type] = {
            'parameters': str({k: v for k, v in model.get_params().items() if k.startswith('classifier__')}),
            'cv_score': float(best_scores[classifier_type]),
            'feature_importances': feature_importance.to_dict('records'),
            'evaluation': eval_metrics
        }
    
    # Write results to JSON file
    with open(log_file, "w") as f:
        json.dump(results, f, indent=4)
    
    print(f"Results logged to {log_file}")
    
    # Also create a simple text summary focused on the key metrics
    metrics_summary_file = f"{output_dir}/metrics_summary_{timestamp}.txt"
    with open(metrics_summary_file, "w") as f:
        f.write("META-LEARNING METRICS SUMMARY\n")
        f.write("============================\n\n")
        f.write(f"Date/Time: {timestamp}\n\n")
        f.write(f"Train size: {len(X_train)}, Test size: {len(X_test)}\n\n")
        
        # First display overall best model
        best_model_type = overall_best_model.named_steps['classifier'].__class__.__name__
        best_cv = results['models'][best_model_type]['evaluation']['cross_validation']
        best_test = results['models'][best_model_type]['evaluation']['test_metrics']
        
        f.write("OVERALL BEST MODEL METRICS\n")
        f.write(f"Model: {best_model_type}\n")
        f.write("Cross-Validation Metrics:\n")
        f.write(f"  Accuracy: {best_cv['accuracy']:.4f}\n")
        f.write(f"  F1 Weighted: {best_cv['f1_weighted']:.4f}\n")
        f.write("Test Set Metrics:\n")
        f.write(f"  Accuracy: {best_test['accuracy']:.4f}\n")
        f.write(f"  F1 Weighted: {best_test['f1_weighted']:.4f}\n")
        f.write("Per-class F1 scores (Test):\n")
        for class_label, score in best_test['class_f1_scores'].items():
            f.write(f"  Class {class_label}: {score:.4f}\n")
        f.write("\n")
        
        # Then display comparison of all models
        f.write("ALL MODELS COMPARISON\n")
        f.write("Model          | CV Accuracy | CV F1   | Test Accuracy | Test F1\n")
        f.write("---------------|-------------|---------|--------------|--------\n")
        
        for classifier_type, details in results['models'].items():
            cv_metrics = details['evaluation']['cross_validation']
            test_metrics = details['evaluation']['test_metrics']
            
            f.write(f"{classifier_type.ljust(15)}| {cv_metrics['accuracy']:.4f}     | {cv_metrics['f1_weighted']:.4f} | {test_metrics['accuracy']:.4f}       | {test_metrics['f1_weighted']:.4f}\n")
    
    print(f"Metrics summary written to {metrics_summary_file}")
    
    # Create a CSV file for easy import into spreadsheets
    csv_file = f"{output_dir}/metrics_{timestamp}.csv"
    with open(csv_file, "w") as f:
        # Write header
        f.write("Model,CV_Accuracy,CV_F1_Weighted,Test_Accuracy,Test_F1_Weighted")
        
        # Determine all class labels across all models
        all_classes = set()
        for model_details in results['models'].values():
            all_classes.update(model_details['evaluation']['test_metrics']['class_f1_scores'].keys())
        
        # Add class-specific headers
        for class_label in sorted(all_classes):
            f.write(f",Test_F1_Class_{class_label}")
        f.write("\n")
        
        # Write data for each model
        for classifier_type, details in results['models'].items():
            cv_metrics = details['evaluation']['cross_validation']
            test_metrics = details['evaluation']['test_metrics']
            
            f.write(f"{classifier_type},{cv_metrics['accuracy']:.6f},{cv_metrics['f1_weighted']:.6f},{test_metrics['accuracy']:.6f},{test_metrics['f1_weighted']:.6f}")
            
            # Add class-specific F1 scores
            for class_label in sorted(all_classes):
                if class_label in test_metrics['class_f1_scores']:
                    f.write(f",{test_metrics['class_f1_scores'][class_label]:.6f}")
                else:
                    f.write(",N/A")  # In case a model doesn't predict a certain class
            f.write("\n")
    
    print(f"Metrics CSV file written to {csv_file}")
    
    # Return metrics dictionaries for plotting
    model_metrics = {model_name: {
        'cv': details['evaluation']['cross_validation'],
        'test': details['evaluation']['test_metrics']
    } for model_name, details in results['models'].items()}
    
    return model_metrics