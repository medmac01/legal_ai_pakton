"""
Description:
Main meta-learning pipeline module that orchestrates the complete machine learning workflow including data preparation, optional PCA, sampling strategies, model training, evaluation, and result visualization.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date : 2025/07/08
"""

from collections import Counter
import os

from .sampling import oversampling_data, undersampling_data
from .preprocessing import prepare_data
from .pca import apply_pca
from .gridSearch import perform_grid_search

from .utils import save_models
from .logging import log_results
from .plotting import plot_cv_vs_test_comparison, plot_per_class_cv_test

def meta_learning(df_preds, 
                  test_size=0.2, 
                  save_dir="results",
                  use_pca=False,
                  pca_variance_threshold=0.95,
                  do_oversample=False,
                  do_undersample=False):
    """
    Main function to execute meta-learning pipeline with train-test split,
    optional PCA, optional oversampling/undersampling, 
    model storage, logging, and visualization.
    """
    # Create main output directory
    os.makedirs(save_dir, exist_ok=True)
    
    # 1) Train/test split
    X_train, X_test, y_train, y_test = prepare_data(df_preds, test_size=test_size)
    print(f"Data split into train set ({len(X_train)} samples) and test set ({len(X_test)} samples)")
    
    # 2) Display class distribution
    print("Initial class distribution in TRAIN:", Counter(y_train))
    print("Initial class distribution in TEST:", Counter(y_test))
    
    if do_oversample:
        print("\n---- Oversampling training data ----")
        X_train, y_train = oversampling_data(X_train, y_train)
    
    if do_undersample:
        print("\n---- Undersampling training data ----")
        X_train, y_train = undersampling_data(X_train, y_train)
    
    if use_pca:
        print("\n---- PCA Dimensionality Reduction ----")
        X_train, X_test = apply_pca(X_train, X_test, 
                                    pca_variance_threshold=pca_variance_threshold,
                                    plot_variance=True)  # or False for no plot
    
    # 5) Grid search to find best models
    overall_best_model, best_models, best_scores = perform_grid_search(X_train, y_train)
    
    # 6) Save models
    save_models(overall_best_model, best_models, output_dir=f"{save_dir}/models")
    
    # 7) Log results with test set evaluation
    model_metrics = log_results(
        overall_best_model, best_models, best_scores, 
        X_train, y_train, X_test, y_test, 
        output_dir=f"{save_dir}/logs"
    )
    
    # 8) Plot CV vs Test comparison
    plot_cv_vs_test_comparison(model_metrics, output_dir=f"{save_dir}/plots")
    
    # 9) Plot per-class F1 scores
    plot_per_class_cv_test(model_metrics, output_dir=f"{save_dir}/plots")
    
    print("\nMeta-learning pipeline completed!")
    return overall_best_model, best_models, model_metrics

# Example usage:
# Basic usage without rebalancing or PCA:
# overall_best, best_models, model_metrics = meta_learning(
#     df_preds, 
#     test_size=0.2,
#     use_pca=False,
#     do_oversample=False,
#     do_undersample=False
# )

# # With oversampling:
# overall_best, best_models, model_metrics = meta_learning(
#     df_preds,
#     test_size=0.2,
#     use_pca=False,
#     do_oversample=True
# )

# # With undersampling:
# overall_best, best_models, model_metrics = meta_learning(
#     df_preds,
#     test_size=0.2,
#     use_pca=False,
#     do_undersample=True
# )

# # With PCA + oversampling:
# overall_best, best_models, model_metrics = meta_learning(
#     df_preds,
#     test_size=0.2,
#     use_pca=True,
#     pca_variance_threshold=0.95,
#     do_oversample=True
# )