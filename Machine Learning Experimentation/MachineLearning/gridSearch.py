"""
Description:
Grid search module that performs hyperparameter optimization using cross-validation to find the best model configuration for each classifier type and determines the overall best performing model.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date : 2025/07/08
"""

from sklearn.model_selection import KFold, GridSearchCV

from .preprocessing import create_pipeline

from .classifiersConfig import get_param_grid

def perform_grid_search(X_train, y_train):
    """Performs GridSearchCV with cross-validation to find the best model and keeps track of best model per classifier type."""
    pipeline = create_pipeline()
    param_grid = get_param_grid()
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    
    # Dictionary to store best models per classifier type
    best_models = {}
    best_scores = {}
    
    # Perform grid search for each classifier type separately
    for params in param_grid:
        classifier_type = params['classifier'][0].__class__.__name__
        print(f"\nPerforming grid search for {classifier_type}...")
        
        grid_search = GridSearchCV(
            estimator=pipeline,
            param_grid=[params],  # Only use the specific classifier's param grid
            scoring='f1_weighted',
            cv=cv,
            verbose=1,
            n_jobs=1
        )
        grid_search.fit(X_train, y_train)
        
        best_models[classifier_type] = grid_search.best_estimator_
        best_scores[classifier_type] = grid_search.best_score_
        print(f"Best {classifier_type} score: {grid_search.best_score_:.3f}")
    
    # Now find the overall best model
    best_classifier = max(best_scores, key=best_scores.get)
    overall_best_model = best_models[best_classifier]
    overall_best_score = best_scores[best_classifier]
    
    print(f"\nOverall best model: {best_classifier} with score: {overall_best_score:.3f}")
    
    return overall_best_model, best_models, best_scores