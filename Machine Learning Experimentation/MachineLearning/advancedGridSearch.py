"""
Description:
Advanced grid search module that provides comprehensive hyperparameter tuning with flexible machine learning pipelines. Supports multiple classifiers, preprocessing options, feature selection, and dimensionality reduction with extended parameter grids for thorough model optimization.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date : 2025/07/08
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import os
import json
from datetime import datetime
from sklearn.model_selection import cross_val_score, KFold, GridSearchCV, RandomizedSearchCV, StratifiedKFold, train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score, roc_auc_score, precision_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest, f_classif, SelectFromModel
from sklearn.decomposition import PCA

# Import additional classifiers if available
try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    
try:
    from lightgbm import LGBMClassifier
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

try:
    # from catboost import CatBoostClassifier
    # CATBOOST_AVAILABLE = True
    CATBOOST_AVAILABLE = False
except ImportError:
    CATBOOST_AVAILABLE = False

def create_pipeline():
    """Creates a flexible machine learning pipeline with preprocessing and a placeholder classifier."""
    return Pipeline([
        ('scaler', StandardScaler()),  # Default scaler, will be replaced in grid search
        ('feature_selection', 'passthrough'),  # Optional feature selection step
        ('dim_reduction', 'passthrough'),  # Optional dimensionality reduction step
        ('classifier', LogisticRegression(max_iter=1000))  # Default classifier, will be replaced in grid search
    ])

def get_param_grid(use_extended=False):
    """Returns a parameter grid for hyperparameter tuning of multiple classifiers.
    
    Args:
        use_extended: If True, use extended parameter ranges and additional classifiers
    """
    # Define preprocessing options
    preprocessing = {
        'scaler': [StandardScaler(), MinMaxScaler(), RobustScaler()],
        'feature_selection': ['passthrough', SelectKBest(score_func=f_classif, k=10), 
                             SelectFromModel(RandomForestClassifier(n_estimators=100, random_state=42))],
        'dim_reduction': ['passthrough', PCA(n_components=0.95, random_state=42)]
    }
    
    # Base parameter grid
    base_param_grid = [
        # Logistic Regression
        {
            'classifier': [LogisticRegression(max_iter=1000, random_state=42)],
            'classifier__C': [0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0],
            'classifier__solver': ['lbfgs', 'liblinear', 'saga'],
            'classifier__penalty': ['l1', 'l2', 'elasticnet', None],
            'classifier__class_weight': [None, 'balanced'],
            'scaler': preprocessing['scaler'],
            'feature_selection': preprocessing['feature_selection'] if use_extended else ['passthrough'],
            'dim_reduction': preprocessing['dim_reduction'] if use_extended else ['passthrough']
        },
        # Decision Tree
        {
            'classifier': [DecisionTreeClassifier(random_state=42)],
            'classifier__max_depth': [None, 5, 10, 15, 20],
            'classifier__min_samples_split': [2, 5, 10, 15],
            'classifier__min_samples_leaf': [1, 2, 4, 8],
            'classifier__max_features': [None, 'sqrt', 'log2'],
            'classifier__class_weight': [None, 'balanced'],
            'scaler': preprocessing['scaler'],
            'feature_selection': preprocessing['feature_selection'] if use_extended else ['passthrough'],
            'dim_reduction': preprocessing['dim_reduction'] if use_extended else ['passthrough']
        },
        # Random Forest
        {
            'classifier': [RandomForestClassifier(random_state=42)],
            'classifier__n_estimators': [50, 100, 200, 300],
            'classifier__max_depth': [None, 5, 10, 15, 20],
            'classifier__min_samples_split': [2, 5, 10],
            'classifier__min_samples_leaf': [1, 2, 4],
            'classifier__max_features': [None, 'sqrt', 'log2'],
            'classifier__bootstrap': [True, False],
            'classifier__class_weight': [None, 'balanced', 'balanced_subsample'],
            'scaler': preprocessing['scaler'],
            'feature_selection': preprocessing['feature_selection'] if use_extended else ['passthrough'],
            'dim_reduction': preprocessing['dim_reduction'] if use_extended else ['passthrough']
        },
        # Gradient Boosting
        {
            'classifier': [GradientBoostingClassifier(random_state=42)],
            'classifier__n_estimators': [50, 100, 200],
            'classifier__learning_rate': [0.01, 0.05, 0.1, 0.2],
            'classifier__max_depth': [3, 5, 7, 9],
            'classifier__min_samples_split': [2, 5, 10],
            'classifier__min_samples_leaf': [1, 2, 4],
            'classifier__subsample': [0.8, 0.9, 1.0],
            'classifier__max_features': [None, 'sqrt', 'log2'],
            'scaler': preprocessing['scaler'],
            'feature_selection': preprocessing['feature_selection'] if use_extended else ['passthrough'],
            'dim_reduction': preprocessing['dim_reduction'] if use_extended else ['passthrough']
        },
        # SVM
        {
            'classifier': [SVC(random_state=42, probability=True)],
            'classifier__C': [0.01, 0.1, 1.0, 10.0, 100.0],
            'classifier__kernel': ['linear', 'rbf', 'poly'],
            'classifier__gamma': ['scale', 'auto', 0.01, 0.1],
            'classifier__degree': [2, 3, 4],  # Only for poly kernel
            'classifier__class_weight': [None, 'balanced'],
            'scaler': preprocessing['scaler'],  # SVM works best with scaled features
            'feature_selection': preprocessing['feature_selection'] if use_extended else ['passthrough'],
            'dim_reduction': preprocessing['dim_reduction'] if use_extended else ['passthrough']
        },
        # MLP (Neural Network)
        {
            'classifier': [MLPClassifier(max_iter=1000, random_state=42)],
            'classifier__hidden_layer_sizes': [(50,), (100,), (50, 50), (100, 50), (100, 100)],
            'classifier__activation': ['relu', 'tanh', 'logistic'],
            'classifier__alpha': [0.0001, 0.001, 0.01, 0.1],
            'classifier__learning_rate': ['constant', 'adaptive', 'invscaling'],
            'classifier__solver': ['adam', 'sgd'],
            'classifier__early_stopping': [True, False],
            'scaler': preprocessing['scaler'],  # Neural networks require scaling
            'feature_selection': preprocessing['feature_selection'] if use_extended else ['passthrough'],
            'dim_reduction': preprocessing['dim_reduction'] if use_extended else ['passthrough']
        },
        # AdaBoost
        {
            'classifier': [AdaBoostClassifier(random_state=42)],
            'classifier__n_estimators': [50, 100, 200],
            'classifier__learning_rate': [0.01, 0.1, 0.5, 1.0],
            'classifier__algorithm': ['SAMME', 'SAMME.R'],
            'scaler': preprocessing['scaler'],
            'feature_selection': preprocessing['feature_selection'] if use_extended else ['passthrough'],
            'dim_reduction': preprocessing['dim_reduction'] if use_extended else ['passthrough']
        }
    ]
    
    # Add XGBoost if available
    if XGBOOST_AVAILABLE and use_extended:
        base_param_grid.append({
            'classifier': [XGBClassifier(random_state=42)],
            'classifier__n_estimators': [50, 100, 200],
            'classifier__learning_rate': [0.01, 0.05, 0.1, 0.2],
            'classifier__max_depth': [3, 5, 7, 9],
            'classifier__min_child_weight': [1, 3, 5],
            'classifier__gamma': [0, 0.1, 0.2],
            'classifier__subsample': [0.8, 0.9, 1.0],
            'classifier__colsample_bytree': [0.8, 0.9, 1.0],
            'classifier__reg_alpha': [0, 0.1, 1.0],
            'classifier__reg_lambda': [0.1, 1.0, 10.0],
            'scaler': preprocessing['scaler'],
            'feature_selection': preprocessing['feature_selection'],
            'dim_reduction': preprocessing['dim_reduction']
        })
    
    # Add LightGBM if available
    if LIGHTGBM_AVAILABLE and use_extended:
        base_param_grid.append({
            'classifier': [LGBMClassifier(random_state=42)],
            'classifier__n_estimators': [50, 100, 200],
            'classifier__learning_rate': [0.01, 0.05, 0.1, 0.2],
            'classifier__max_depth': [3, 5, 7, 9, -1],  # -1 means no limit
            'classifier__num_leaves': [31, 63, 127],
            'classifier__min_child_samples': [20, 50, 100],
            'classifier__subsample': [0.8, 0.9, 1.0],
            'classifier__colsample_bytree': [0.8, 0.9, 1.0],
            'classifier__reg_alpha': [0, 0.1, 1.0],
            'classifier__reg_lambda': [0, 0.1, 1.0],
            'scaler': preprocessing['scaler'],
            'feature_selection': preprocessing['feature_selection'],
            'dim_reduction': preprocessing['dim_reduction']
        })
    
    # Add CatBoost if available
    if CATBOOST_AVAILABLE and use_extended:
        base_param_grid.append({
            'classifier': [CatBoostClassifier(random_state=42, verbose=0)],
            'classifier__iterations': [100, 200, 500],
            'classifier__learning_rate': [0.01, 0.05, 0.1],
            'classifier__depth': [4, 6, 8, 10],
            'classifier__l2_leaf_reg': [1, 3, 5, 10],
            'classifier__border_count': [32, 64, 128],
            'scaler': preprocessing['scaler'],
            'feature_selection': preprocessing['feature_selection'],
            'dim_reduction': preprocessing['dim_reduction']
        })
    
    return base_param_grid

def perform_grid_search(X_train, y_train, search_type="grid", n_iter=50, use_extended=False, scoring='f1_weighted', n_jobs=1, verbose=1):
    """Performs GridSearchCV or RandomizedSearchCV with cross-validation to find the best model.
    
    Args:
        X_train: Training features
        y_train: Training target
        search_type: Type of search to perform ('grid' or 'randomized')
        n_iter: Number of iterations for RandomizedSearchCV
        use_extended: Whether to use extended parameter grid
        scoring: Scoring metric to use
        n_jobs: Number of parallel jobs
        verbose: Verbosity level
    
    Returns:
        overall_best_model, best_models, best_scores
    """
    pipeline = create_pipeline()
    param_grid = get_param_grid(use_extended=use_extended)
    
    # Use StratifiedKFold for better handling of imbalanced datasets
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    # Dictionary to store best models per classifier type
    best_models = {}
    best_scores = {}
    
    # Perform search for each classifier type separately
    for params in param_grid:
        classifier_type = params['classifier'][0].__class__.__name__
        print(f"\nPerforming {search_type} search for {classifier_type}...")
        
        if search_type.lower() == "grid":
            search = GridSearchCV(
                estimator=pipeline,
                param_grid=[params],  # Only use the specific classifier's param grid
                scoring=scoring,
                cv=cv,
                verbose=verbose,
                n_jobs=n_jobs,
                return_train_score=True
            )
        else:  # Randomized search
            search = RandomizedSearchCV(
                estimator=pipeline,
                param_distributions=params,
                n_iter=n_iter,
                scoring=scoring,
                cv=cv,
                verbose=verbose,
                n_jobs=n_jobs,
                random_state=42,
                return_train_score=True
            )
        
        try:
            search.fit(X_train, y_train)
            
            best_models[classifier_type] = search.best_estimator_
            best_scores[classifier_type] = search.best_score_
            print(f"Best {classifier_type} score: {search.best_score_:.3f}")
            print(f"Best parameters: {search.best_params_}")
        except Exception as e:
            print(f"Error fitting {classifier_type}: {str(e)}")
            continue
    
    # Find the overall best model
    if best_scores:
        best_classifier = max(best_scores, key=best_scores.get)
        overall_best_model = best_models[best_classifier]
        overall_best_score = best_scores[best_classifier]
        
        print(f"\nOverall best model: {best_classifier} with score: {overall_best_score:.3f}")
    else:
        print("No successful models found!")
        overall_best_model = None
    
    return overall_best_model, best_models, best_scores

def get_feature_importance(estimator, feature_names):
    """Gets feature importance if available and returns as DataFrame."""
    # Get the actual classifier from the pipeline
    if hasattr(estimator, 'named_steps'):
        if 'classifier' in estimator.named_steps:
            classifier = estimator.named_steps['classifier']
        else:
            return pd.DataFrame({'Feature': ['N/A'], 'Importance': [0]})
    else:
        classifier = estimator
    
    # Handle different types of feature importance
    if hasattr(classifier, 'coef_'):
        # For linear models like LogisticRegression
        if len(classifier.coef_.shape) > 1 and classifier.coef_.shape[0] > 1:
            # Multi-class case: average absolute coefficients across classes
            importances = np.mean(np.abs(classifier.coef_), axis=0)
        else:
            importances = np.abs(classifier.coef_[0] if len(classifier.coef_.shape) > 1 else classifier.coef_)
            
        # Handle feature selection/transformation in the pipeline
        if hasattr(estimator, 'named_steps') and 'feature_selection' in estimator.named_steps:
            if estimator.named_steps['feature_selection'] != 'passthrough':
                # Get selected feature indices/names if available
                if hasattr(estimator.named_steps['feature_selection'], 'get_support'):
                    mask = estimator.named_steps['feature_selection'].get_support()
                    selected_features = np.array(feature_names)[mask]
                    feature_importance = pd.DataFrame({'Feature': selected_features, 'Importance': importances})
                    return feature_importance.sort_values(by='Importance', ascending=False)
        
        feature_importance = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
        return feature_importance.sort_values(by='Importance', ascending=False)
        
    elif hasattr(classifier, 'feature_importances_'):
        # For tree-based models
        importances = classifier.feature_importances_
        
        # Handle feature selection in the pipeline
        if hasattr(estimator, 'named_steps') and 'feature_selection' in estimator.named_steps:
            if estimator.named_steps['feature_selection'] != 'passthrough':
                # Get selected feature indices/names if available
                if hasattr(estimator.named_steps['feature_selection'], 'get_support'):
                    mask = estimator.named_steps['feature_selection'].get_support()
                    selected_features = np.array(feature_names)[mask]
                    feature_importance = pd.DataFrame({'Feature': selected_features, 'Importance': importances})
                    return feature_importance.sort_values(by='Importance', ascending=False)
        
        feature_importance = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
        return feature_importance.sort_values(by='Importance', ascending=False)
    else:
        # If no feature importance available
        return pd.DataFrame({'Feature': ['N/A'], 'Importance': [0]})

def calculate_metrics(model, X, y):
    """Calculate comprehensive metrics including accuracy, precision, recall, F1, and AUC."""
    y_pred = model.predict(X)
    
    # For probability-based metrics (like ROC AUC), check if the model supports predict_proba
    metrics = {
        'accuracy': accuracy_score(y, y_pred),
        'precision_weighted': precision_score(y, y_pred, average='weighted'),
        'recall_weighted': recall_score(y, y_pred, average='weighted'),
        'f1_weighted': f1_score(y, y_pred, average='weighted'),
        'class_f1_scores': {
            str(label): metrics['f1-score']
            for label, metrics in classification_report(y, y_pred, output_dict=True).items()
            if isinstance(metrics, dict) and 'f1-score' in metrics
        }
    }
    
    # Add ROC AUC if possible (for binary classification or models with predict_proba)
    if hasattr(model, 'predict_proba'):
        try:
            # For binary classification
            if len(np.unique(y)) == 2:
                y_proba = model.predict_proba(X)[:, 1]
                metrics['roc_auc'] = roc_auc_score(y, y_proba)
            # For multiclass
            else:
                y_proba = model.predict_proba(X)
                metrics['roc_auc'] = roc_auc_score(y, y_proba, multi_class='ovr')
        except Exception as e:
            print(f"Couldn't calculate ROC AUC: {str(e)}")
    
    return metrics

def evaluate_model(model, X_train, y_train, X_test, y_test, cv):
    """Evaluates a model using cross-validation and test set and returns comprehensive metrics."""
    # Cross-validation metrics on training data
    cv_metrics = {
        'accuracy': cross_val_score(model, X_train, y_train, cv=cv, scoring='accuracy').mean(),
        'f1_weighted': cross_val_score(model, X_train, y_train, cv=cv, scoring='f1_weighted').mean(),
        'precision_weighted': cross_val_score(model, X_train, y_train, cv=cv, scoring='precision_weighted').mean(),
        'recall_weighted': cross_val_score(model, X_train, y_train, cv=cv, scoring='recall_weighted').mean()
    }
    
    # Try to get ROC AUC CV score if model supports predict_proba
    if hasattr(model, 'predict_proba'):
        try:
            cv_metrics['roc_auc'] = cross_val_score(model, X_train, y_train, cv=cv, scoring='roc_auc').mean()
        except Exception as e:
            print(f"Couldn't calculate ROC AUC for CV: {str(e)}")
    
    # Training set metrics (direct fit)
    model.fit(X_train, y_train)
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

def save_models(overall_best_model, best_models, output_dir="models"):
    """Saves the best models to pickle files."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the overall best model if it exists
    if overall_best_model is not None:
        with open(f"{output_dir}/best_overall_model.pkl", "wb") as f:
            pickle.dump(overall_best_model, f)
    
    # Save each best model by classifier type
    for classifier_type, model in best_models.items():
        with open(f"{output_dir}/best_{classifier_type.lower()}_model.pkl", "wb") as f:
            pickle.dump(model, f)
    
    print(f"Models saved in {output_dir} directory")

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
        'models': {}
    }
    
    # Add overall best model info if it exists
    if overall_best_model is not None:
        results['overall_best_model'] = {
            'type': overall_best_model.named_steps['classifier'].__class__.__name__,
            'parameters': str(overall_best_model.get_params()),
            'cv_score': float(best_scores[overall_best_model.named_steps['classifier'].__class__.__name__])
        }
    
    # Create a StratifiedKFold object for consistent evaluation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    # For each classifier, log its parameters, importance, and evaluation metrics
    for classifier_type, model in best_models.items():
        # Get feature importance
        feature_importance = get_feature_importance(model, X_train.columns)
        
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
        
        # First display overall best model if exists
        if overall_best_model is not None:
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
        # Write header with more metrics
        f.write("Model,CV_Accuracy,CV_F1_Weighted,CV_Precision,CV_Recall")
        if 'roc_auc' in next(iter(results['models'].values()))['evaluation']['cross_validation']:
            f.write(",CV_ROC_AUC")
        f.write(",Test_Accuracy,Test_F1_Weighted,Test_Precision,Test_Recall")
        if 'roc_auc' in next(iter(results['models'].values()))['evaluation']['test_metrics']:
            f.write(",Test_ROC_AUC")
        
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
            
            f.write(f"{classifier_type},{cv_metrics['accuracy']:.6f},{cv_metrics['f1_weighted']:.6f}")
            f.write(f",{cv_metrics.get('precision_weighted', 'N/A')},{cv_metrics.get('recall_weighted', 'N/A')}")
            
            if 'roc_auc' in cv_metrics:
                f.write(f",{cv_metrics['roc_auc']:.6f}")
            
            f.write(f",{test_metrics['accuracy']:.6f},{test_metrics['f1_weighted']:.6f}")
            f.write(f",{test_metrics.get('precision_weighted', 'N/A')},{test_metrics.get('recall_weighted', 'N/A')}")
            
            if 'roc_auc' in test_metrics:
                f.write(f",{test_metrics['roc_auc']:.6f}")
            
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

def meta_learning(df_preds, test_size=0.2, search_type="grid", n_iter=50, use_extended=False, 
                  scoring='f1_weighted', n_jobs=1, save_dir="results"):
    """
    Main function to execute enhanced meta-learning pipeline with train-test split, model storage, 
    logging, and visualization.
    
    Args:
        df_preds: DataFrame with features and 'ground_truth' target column
        test_size: Proportion of data to use for testing
        search_type: 'grid' or 'randomized'
        n_iter: Number of iterations for randomized search
        use_extended: Whether to use extended parameter grid with preprocessing steps
        scoring: Scoring metric for model selection
        n_jobs: Number of parallel jobs (-1 for all processors)
        save_dir: Directory to save results
    
    Returns:
        overall_best_model, best_models, model_metrics
    """
    # Create main output directory
    os.makedirs(save_dir, exist_ok=True)
    
    # Prepare the data with train-test split
    X_train, X_test, y_train, y_test = prepare_data(df_preds, test_size=test_size)
    print(f"Data split into train set ({len(X_train)} samples) and test set ({len(X_test)} samples)")
    
    # Display class distribution
    train_dist = pd.Series(y_train).value_counts(normalize=True)
    test_dist = pd.Series(y_test).value_counts(normalize=True)
    print("Class distribution:")
    print("Train:", dict(train_dist.round(3)))
    print("Test:", dict(test_dist.round(3)))
    
    # Perform search on training data only
    overall_best_model, best_models, best_scores = perform_grid_search(
        X_train, y_train, 
        search_type=search_type,
        n_iter=n_iter,
        use_extended=use_extended,
        scoring=scoring,
        n_jobs=n_jobs
    )
    
    # Save models if we found any
    if overall_best_model is not None:
        save_models(overall_best_model, best_models, output_dir=f"{save_dir}/models")
        
        # Log results with comprehensive metrics, including test set evaluation
        model_metrics = log_results(
            overall_best_model, best_models, best_scores, 
            X_train, y_train, X_test, y_test, 
            output_dir=f"{save_dir}/logs"
        )
        
        # Plot CV vs Test comparison
        plot_cv_vs_test_comparison(model_metrics, output_dir=f"{save_dir}/plots")
        
        # Plot per-class F1 scores
        plot_per_class_cv_test(model_metrics, output_dir=f"{save_dir}/plots")
        
        print("\nMeta-learning pipeline completed successfully!")
        return overall_best_model, best_models, model_metrics
    else:
        print("\nMeta-learning pipeline completed with no successful models.")
        return None, best_models, {}

# Example usage:
"""
# Advanced usage with RandomizedSearchCV
overall_best, best_models, metrics = meta_learning(
    df_preds, 
    test_size=0.2,
    search_type="randomized",  # Use RandomizedSearchCV instead of GridSearchCV
    n_iter=100,  # Number of parameter settings to try
    use_extended=True,  # Use extended parameter grid with preprocessing
    scoring='roc_auc',  # Use ROC AUC as scoring metric
    n_jobs=-1  # Use all available cores
)
"""