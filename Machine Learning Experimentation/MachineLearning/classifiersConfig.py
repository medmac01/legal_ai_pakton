"""
Description:
Configuration module that defines parameter grids for hyperparameter tuning of multiple machine learning classifiers including Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, SVM, K-Nearest Neighbors, and Neural Networks.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date : 2025/07/08
"""

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression

def get_param_grid():
    """Returns a parameter grid for hyperparameter tuning of multiple classifiers."""
    return [
        {
            'classifier': [LogisticRegression(random_state=42)],
            'classifier__C': [0.01, 0.05, 0.1, 1.0, 10.0],
            'classifier__solver': ['liblinear', 'saga'],   # ['lbfgs', 'newton-cg', 'sag'] only with l2
            'classifier__penalty': ['l1', 'l2'],
            'classifier__class_weight': [None, 'balanced'],
            'classifier__max_iter': [100, 200, 1000]
        },
        {
            'classifier': [DecisionTreeClassifier(random_state=42)],
            'classifier__max_depth': [None, 5, 10, 15],
            'classifier__min_samples_split': [2, 5, 10],
            'classifier__min_samples_leaf': [1, 2, 3, 4],
            'classifier__criterion': ['gini', 'entropy'],
            'classifier__class_weight': [None, 'balanced'],
            'classifier__max_features': [None, 'sqrt', 'log2'],
            'classifier__max_leaf_nodes': [None, 5, 10, 15]
        },
        {
            'classifier': [RandomForestClassifier(random_state=42)],
            'classifier__n_estimators': [10, 50, 100, 200],
            'classifier__max_depth': [None, 5, 10, 15],
            'classifier__class_weight': [None, 'balanced'],
            'classifier__criterion': ['gini', 'entropy'],
            'classifier__min_samples_split': [2, 5],
            'classifier__min_samples_leaf': [1, 2],
            'classifier__max_features': [None, 'sqrt', 'log2']
        },
        {
            'classifier': [GradientBoostingClassifier(random_state=42)],
            'classifier__n_estimators': [50, 100],
            'classifier__learning_rate': [0.01, 0.1, 0.2],
            'classifier__max_depth': [3, 5, 7]
        },
        {
            'classifier': [SVC(random_state=42)],
            'classifier__C': [0.01, 0.1, 1.0, 10.0],
            'classifier__kernel': ['linear', 'rbf', 'poly', 'sigmoid'],
            'classifier__gamma': ['scale', 'auto', 0.004, 0.4],
            'classifier__class_weight': [None, 'balanced'],
            'classifier__degree': [2, 3, 4]  # Only relevant for poly kernel
        },
        {
            'classifier': [MLPClassifier(max_iter=2000, random_state=42, early_stopping=True, n_iter_no_change=10)],
            'classifier__hidden_layer_sizes': [(10,), (50,), (50, 50)], # , (100,)
            'classifier__activation': ['relu', 'tanh'],
            'classifier__alpha': [0.0001, 0.01],
            'classifier__solver': ['adam', 'sgd'],
            'classifier__learning_rate': ['constant', 'invscaling', 'adaptive'],
            'classifier__learning_rate_init': [0.001, 0.01]
        },
        {
            'classifier': [GaussianNB()],
            'classifier__var_smoothing': [1e-09, 1e-08, 1e-07]
        },
        {
            'classifier': [KNeighborsClassifier()],
            'classifier__n_neighbors': [3, 5, 7, 11, 17],
            'classifier__weights': ['uniform', 'distance'],
            'classifier__metric': ['euclidean', 'manhattan', 'minkowski']
        }
    ]