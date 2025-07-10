"""
Description:
Principal Component Analysis (PCA) module that provides dimensionality reduction functionality with data scaling, variance preservation control, and optional visualization of explained variance ratios.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date : 2025/07/08
"""

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

def apply_pca(X_train, X_test, 
              pca_variance_threshold=0.95, 
              plot_variance=True):
    """
    Scales X_train and X_test, applies PCA to preserve a specified fraction
    of cumulative variance, and returns the dimension-reduced data.

    Parameters
    ----------
    X_train : pd.DataFrame or np.ndarray
        Training feature set.
    X_test : pd.DataFrame or np.ndarray
        Test feature set.
    pca_variance_threshold : float
        Fraction of cumulative variance to preserve (e.g. 0.95 for 95%).
    plot_variance : bool
        Whether to plot the explained variance ratio curve.

    Returns
    -------
    X_train_reduced : pd.DataFrame
        Reduced training feature set (as a DataFrame).
    X_test_reduced : pd.DataFrame
        Reduced test feature set (as a DataFrame).
    """

    # Convert to numeric arrays if DataFrames
    if isinstance(X_train, pd.DataFrame):
        X_train_vals = X_train.values
    else:
        X_train_vals = X_train

    if isinstance(X_test, pd.DataFrame):
        X_test_vals = X_test.values
    else:
        X_test_vals = X_test

    # 1) Scale the data
    pca_scaler = StandardScaler()
    X_train_scaled = pca_scaler.fit_transform(X_train_vals)
    X_test_scaled = pca_scaler.transform(X_test_vals)

    # 2) Fit PCA on training data
    pca = PCA()
    pca.fit(X_train_scaled)

    # 3) Compute cumulative variance ratio
    cumsum = np.cumsum(pca.explained_variance_ratio_)
    d = np.argmax(cumsum >= pca_variance_threshold) + 1

    print(f"Features before PCA: {X_train_vals.shape[1]}")
    print(f"Number of components to reach {pca_variance_threshold:.0%} variance: {d}")

    # 4) Create a PCA object with n_components = d
    pca = PCA(n_components=d)
    X_train_reduced = pca.fit_transform(X_train_scaled)
    X_test_reduced = pca.transform(X_test_scaled)

    # (Optional) Plot the explained variance ratio
    if plot_variance:
        plt.figure(figsize=(6, 4))
        plt.plot(cumsum, linewidth=3)
        plt.axis([0, len(cumsum), 0, 1])
        plt.xlabel("Dimensions")
        plt.ylabel("Explained Variance")
        plt.title("PCA Explained Variance Ratio")
        # Mark lines for threshold and d
        plt.plot([d, d], [0, pca_variance_threshold], "k:")
        plt.plot([0, d], [pca_variance_threshold, pca_variance_threshold], "k:")
        plt.plot(d, pca_variance_threshold, "ko")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    # Convert the results back to DataFrames (optional)
    # for clarity, we keep indices from original data
    X_train_reduced = pd.DataFrame(X_train_reduced, 
                                   index=X_train.index if isinstance(X_train, pd.DataFrame) else None)
    X_test_reduced = pd.DataFrame(X_test_reduced, 
                                  index=X_test.index if isinstance(X_test, pd.DataFrame) else None)

    return X_train_reduced, X_test_reduced