"""
Description:
Data preprocessing module that handles data preparation tasks including train-test splitting with stratification and machine learning pipeline creation with standard scaling and classifier components.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date : 2025/07/08
"""

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

def prepare_data(df_preds, test_size=0.2, random_state=42):
    """Splits the input dataframe into features and target variable, and creates train-test split."""
    X = df_preds.drop(columns=["ground_truth"])
    y = df_preds["ground_truth"]
    
    # Create train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)
    
    return X_train, X_test, y_train, y_test

def create_pipeline():
    """Creates a machine learning pipeline with standard scaling and a placeholder classifier (it will be overridden)."""
    return Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression(max_iter=1000))
    ])