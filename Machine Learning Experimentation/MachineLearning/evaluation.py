"""
Description:
Model evaluation utilities that calculate various performance metrics including accuracy, F1 scores, and per-class performance metrics using cross-validation and test set evaluation.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date : 2025/07/08
"""

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
from sklearn.model_selection import cross_val_score

def calculate_metrics(model, X, y):
    """Calculate accuracy, weighted F1 score, and per-class F1 scores."""
    y_pred = model.predict(X)
    return {
        'accuracy': accuracy_score(y, y_pred),
        'f1_weighted': f1_score(y, y_pred, average='weighted'),
        'class_f1_scores': {
            str(label): metrics['f1-score']
            for label, metrics in classification_report(y, y_pred, output_dict=True).items()
            if isinstance(metrics, dict) and 'f1-score' in metrics
        }
    }

def evaluate_model(model, X_train, y_train, X_test, y_test, cv):
    """Evaluates a model using cross-validation and test set and returns metrics."""
    # Cross-validation metrics on training data
    cv_metrics = {
        'accuracy': cross_val_score(model, X_train, y_train, cv=cv, scoring='accuracy').mean(),
        'f1_weighted': cross_val_score(model, X_train, y_train, cv=cv, scoring='f1_weighted').mean()
    }
    
    # Training set metrics (direct fit on training data)
    train_metrics = calculate_metrics(model, X_train, y_train)
    
    # Test set metrics
    test_metrics = calculate_metrics(model, X_test, y_test)
    
    return {
        'cross_validation': cv_metrics,
        'train_metrics': train_metrics,
        'test_metrics': test_metrics,
        'test_confusion_matrix': confusion_matrix(y_test, model.predict(X_test)).tolist(),
        'test_classification_report': classification_report(y_test, model.predict(X_test), output_dict=True)
    }
