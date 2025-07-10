"""
Description:
Comprehensive plotting and visualization module that generates various charts and plots for machine learning model performance analysis, including cross-validation comparisons, confusion matrices, correlation heatmaps, and interactive agreement visualizations.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date : 2025/07/08
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime

import seaborn as sns

def plot_cv_vs_test_comparison(model_metrics, output_dir="plots"):
    """Plots CV vs Test scores for each model."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Prepare data for plotting
    models = list(model_metrics.keys())
    cv_accuracy = [metrics['cv']['accuracy'] for metrics in model_metrics.values()]
    cv_f1 = [metrics['cv']['f1_weighted'] for metrics in model_metrics.values()]
    test_accuracy = [metrics['test']['accuracy'] for metrics in model_metrics.values()]
    test_f1 = [metrics['test']['f1_weighted'] for metrics in model_metrics.values()]
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Set width of bars
    barWidth = 0.35
    
    # Set position of bar on X axis
    r1 = np.arange(len(models))
    r2 = [x + barWidth for x in r1]
    
    # Make the plot for Accuracy
    bars1 = ax1.bar(r1, cv_accuracy, width=barWidth, label='CV', color='skyblue')
    bars2 = ax1.bar(r2, test_accuracy, width=barWidth, label='Test', color='lightcoral')
    
    # Add labels and title
    ax1.set_xlabel('Models', fontweight='bold')
    ax1.set_ylabel('Accuracy', fontweight='bold')
    ax1.set_title('Accuracy: CV vs Test')
    ax1.set_xticks([r + barWidth/2 for r in range(len(models))])
    ax1.set_xticklabels(models, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add values on bars
    for bar, value in zip(bars1, cv_accuracy):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f'{value:.3f}', ha='center', va='bottom')
    
    for bar, value in zip(bars2, test_accuracy):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f'{value:.3f}', ha='center', va='bottom')
    
    # Make the plot for F1 Score
    bars3 = ax2.bar(r1, cv_f1, width=barWidth, label='CV', color='skyblue')
    bars4 = ax2.bar(r2, test_f1, width=barWidth, label='Test', color='lightcoral')
    
    # Add labels and title
    ax2.set_xlabel('Models', fontweight='bold')
    ax2.set_ylabel('F1 Score (Weighted)', fontweight='bold')
    ax2.set_title('F1 Score: CV vs Test')
    ax2.set_xticks([r + barWidth/2 for r in range(len(models))])
    ax2.set_xticklabels(models, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add values on bars
    for bar, value in zip(bars3, cv_f1):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f'{value:.3f}', ha='center', va='bottom')
    
    for bar, value in zip(bars4, test_f1):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f'{value:.3f}', ha='center', va='bottom')
    
    # Adjust layout and save
    plt.tight_layout()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plt.savefig(f"{output_dir}/cv_test_comparison_{timestamp}.png")
    plt.show()
    
    print(f"CV vs Test comparison plot saved to {output_dir}/cv_test_comparison_{timestamp}.png")


def plot_per_class_cv_test(model_metrics, output_dir="plots"):
    """Plots per-class F1 scores for the best model on test set."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Find the best model based on test F1 score
    best_model = max(model_metrics.keys(), key=lambda x: model_metrics[x]['test']['f1_weighted'])
    
    # Get all class labels
    class_labels = sorted(model_metrics[best_model]['test']['class_f1_scores'].keys())
    
    # Prepare data for all models' test F1 scores per class
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Number of models
    n_models = len(model_metrics)
    barWidth = 0.8 / n_models
    
    # Calculate positions for bars
    positions = []
    for i in range(n_models):
        offset = i - (n_models - 1) / 2
        positions.append(np.arange(len(class_labels)) + offset * barWidth)
    
    # Colors for models
    colors = plt.cm.tab10(np.linspace(0, 1, n_models))
    
    # Plot bars for each model
    for i, (model_name, metrics) in enumerate(model_metrics.items()):
        test_f1_scores = [metrics['test']['class_f1_scores'].get(cl, 0) for cl in class_labels]
        ax.bar(positions[i], test_f1_scores, width=barWidth, label=model_name, color=colors[i])
    
    # Add labels and title
    ax.set_xlabel('Class', fontweight='bold')
    ax.set_ylabel('F1 Score', fontweight='bold')
    ax.set_title('Per-Class F1 Scores on Test Set')
    ax.set_xticks(np.arange(len(class_labels)))
    ax.set_xticklabels(class_labels)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Adjust layout and save
    plt.tight_layout()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plt.savefig(f"{output_dir}/per_class_f1_test_{timestamp}.png")
    plt.show()
    
    print(f"Per-class F1 scores plot saved to {output_dir}/per_class_f1_test_{timestamp}.png")

def plot_metrics_for_filter(
    df,
    filter_dict=None
):
    """
    Plots mean accuracy, mean F1 (weighted), and mean F1 per class
    after filtering the DataFrame by one or more conditions.
    
    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe containing the data.

    filter_dict : dict or None
        A dictionary where keys are column names and values are either a single value 
        or a list of values to filter for. For instance:
            {
                "additional_info.prompting_technique": "naive",
                "additional_info.subset_name": ["contractnli_a", "some_other_subset"]
            }
        If None, no filtering is performed.
    """

    # -------------------------
    # 1) Apply filtering
    # -------------------------
    df_filtered = df.copy()
    
    # If there's no filtering dictionary, we just skip the filtering step
    if filter_dict is not None:
        for col, desired in filter_dict.items():
            # If desired is a list, use .isin(...)
            if isinstance(desired, list):
                df_filtered = df_filtered[df_filtered[col].isin(desired)]
            else:
                # Otherwise, filter by direct equality
                df_filtered = df_filtered[df_filtered[col] == desired]
    
    if df_filtered.empty:
        print("No rows found after applying the given filters. Nothing to plot.")
        return
    
    # -------------------------
    # 2) Group and compute means
    # -------------------------
    grouped = df_filtered.groupby("additional_info.model", as_index=False).agg({
        "result.accuracy": "mean",
        "result.f1_weighted": "mean",
        "result.f1_per_class.contradiction": "mean",
        "result.f1_per_class.entailment": "mean",
        "result.f1_per_class.neutral": "mean"
    })

    models           = grouped["additional_info.model"].values
    accuracy_vals    = grouped["result.accuracy"].values
    f1_weighted_vals = grouped["result.f1_weighted"].values
    f1_contra_vals   = grouped["result.f1_per_class.contradiction"].values
    f1_entail_vals   = grouped["result.f1_per_class.entailment"].values
    f1_neutral_vals  = grouped["result.f1_per_class.neutral"].values

    # =====================================================================
    # A) Plot Accuracy (one bar per model)
    # =====================================================================
    fig, ax = plt.subplots(figsize=(12, 6))
    bar_width = 0.6

    bars_acc = ax.bar(
        x=np.arange(len(models)),
        height=accuracy_vals,
        width=bar_width,
        color='skyblue'
    )

    ax.set_xlabel('Models', fontweight='bold')
    ax.set_ylabel('Accuracy', fontweight='bold')
    ax.set_title('Mean Accuracy by Model (after filtering)')
    ax.set_xticks(np.arange(len(models)))
    ax.set_xticklabels(models, rotation=45, ha='right')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Add data labels
    for bar, val in zip(bars_acc, accuracy_vals):
        ax.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.001,
            f'{val:.3f}',
            ha='center', 
            va='bottom'
        )

    plt.tight_layout()
    plt.show()

    # =====================================================================
    # B) Plot F1 (Weighted) (one bar per model)
    # =====================================================================
    fig, ax = plt.subplots(figsize=(12, 6))
    bars_f1 = ax.bar(
        x=np.arange(len(models)),
        height=f1_weighted_vals,
        width=bar_width,
        color='lightcoral'
    )

    ax.set_xlabel('Models', fontweight='bold')
    ax.set_ylabel('F1 Weighted', fontweight='bold')
    ax.set_title('Mean F1 (Weighted) by Model (after filtering)')
    ax.set_xticks(np.arange(len(models)))
    ax.set_xticklabels(models, rotation=45, ha='right')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    for bar, val in zip(bars_f1, f1_weighted_vals):
        ax.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.001,
            f'{val:.3f}',
            ha='center', 
            va='bottom'
        )

    plt.tight_layout()
    plt.show()

    # =====================================================================
    # C) Plot F1 per class (three bars per model)
    # =====================================================================
    fig, ax = plt.subplots(figsize=(12, 6))
    bar_width = 0.2

    # Positions for the bars
    r1 = np.arange(len(models))
    r2 = r1 + bar_width
    r3 = r2 + bar_width

    bars_contra = ax.bar(r1, f1_contra_vals, width=bar_width, label='Contradiction', color='skyblue')
    bars_entail = ax.bar(r2, f1_entail_vals, width=bar_width, label='Entailment', color='lightcoral')
    bars_neutral = ax.bar(r3, f1_neutral_vals, width=bar_width, label='Neutral', color='palegreen')

    ax.set_xlabel('Models', fontweight='bold')
    ax.set_ylabel('F1 Score', fontweight='bold')
    ax.set_title('Mean F1 per Class by Model (after filtering)')
    ax.set_xticks(r1 + bar_width)
    ax.set_xticklabels(models, rotation=45, ha='right')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.legend()

    # Add data labels
    for bar, val in zip(bars_contra, f1_contra_vals):
        ax.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.001,
            f'{val:.3f}',
            ha='center', 
            va='bottom'
        )

    for bar, val in zip(bars_entail, f1_entail_vals):
        ax.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.001,
            f'{val:.3f}',
            ha='center', 
            va='bottom'
        )

    for bar, val in zip(bars_neutral, f1_neutral_vals):
        ax.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.001,
            f'{val:.3f}',
            ha='center', 
            va='bottom'
        )

    plt.tight_layout()
    plt.show()

# usage examples:
# plot_metrics_for_filter(df, filter_dict={
#     "additional_info.prompting_technique": "naive"
# })
# # filter on "naive" prompting technique AND subset_name = "contractnli_a"
# plot_metrics_for_filter(df, filter_dict={
#     "additional_info.prompting_technique": "naive",
#     "additional_info.subset_name": "contractnli_a"
# })

def plot_CorrelationHeatmap(predictions, name_map):
    """
    Plots a heatmap of the correlation matrix for a given set of model predictions.

    Parameters:
    -----------
    predictions : pandas.DataFrame
        A DataFrame where each column represents predictions from a different model.
        The function computes the correlation between these columns.

    name_map : dict
        A dictionary mapping short model names (column names in `predictions`)
        to their full descriptive names. This mapping is printed for reference.

    Returns:
    --------
    None
        The function displays a heatmap of the correlation matrix and prints 
        the mapping of short names to long names.

    Notes:
    ------
    - Uses Pearson correlation by default (`DataFrame.corr()`).
    - Displays annotations with correlation values rounded to two decimal places.
    - The heatmap is plotted using Seaborn with a fixed figure size (20x20).
    """
    # Compute correlation
    corr_matrix = predictions.corr()

    # Plot heatmap
    plt.figure(figsize=(20, 20))
    sns.heatmap(
        corr_matrix,
        annot=True,   
        square=True,
        linewidths=.5,
        fmt=".2f"        # show only 2 decimal places
    )
    plt.title("Correlation of Model Predictions")
    plt.show()
    # If you need to see which experiment corresponds to which original name:
    print("Mapping from short to long names:")
    for short_name, long_name in name_map.items():
        print(f"{short_name} => {long_name}")

from sklearn.metrics import cohen_kappa_score

def plot_agreement_heatmaps(df_preds):
    """
    Plots heatmaps for two agreement metrics: 
    (1) Simple Agreement (percent agreement) 
    (2) Cohen's Kappa, which adjusts for chance-level agreement.

    Parameters:
    -----------
    df_preds : pandas.DataFrame
        A DataFrame where each column represents predictions from a different model.
        The function computes agreement metrics between all pairs of models.

    Returns:
    --------
    None
        The function displays two heatmaps:
        - Simple Agreement between all model predictions.
        - Cohen's Kappa between all model predictions.

    Notes:
    ------
    - Simple Agreement measures the proportion of identical predictions.
    - Cohen’s Kappa accounts for agreement expected by chance.
    - Values range from:
      - **Simple Agreement:** 0 (no agreement) to 1 (perfect agreement).
      - **Cohen’s Kappa:** -1 (worse than random) to +1 (perfect agreement).
    - A 20x20 figure size is used to ensure readability for larger datasets.
    """
    # Create empty matrices for our metrics
    num_experiments = len(df_preds.columns)
    simple_agreement_matrix = np.zeros((num_experiments, num_experiments))
    cohens_kappa_matrix = np.zeros((num_experiments, num_experiments))

    # Fill the matrices with calculated metrics
    for i, col1 in enumerate(df_preds.columns):
        for j, col2 in enumerate(df_preds.columns):
            # Simple agreement (percent agreement)
            simple_agreement_matrix[i, j] = np.mean(df_preds[col1] == df_preds[col2])
            
            # Cohen's Kappa
            if i != j:  # Kappa is 1 for self-comparison, no need to calculate
                cohens_kappa_matrix[i, j] = cohen_kappa_score(df_preds[col1], df_preds[col2])
            else:
                cohens_kappa_matrix[i, j] = 1.0  # Perfect agreement with self

    # Convert to DataFrames with the same labels as your original data
    simple_agreement_df = pd.DataFrame(
        simple_agreement_matrix, 
        index=df_preds.columns, 
        columns=df_preds.columns
    )

    cohens_kappa_df = pd.DataFrame(
        cohens_kappa_matrix,
        index=df_preds.columns,
        columns=df_preds.columns
    )

    plt.figure(figsize=(20, 20))
    sns.heatmap(
        simple_agreement_df,
        annot=True,
        square=True,
        linewidths=.5,
        fmt=".2f",
        vmin=0,
        vmax=1
    )
    plt.title("Simple Agreement Between Model Predictions")
    plt.show()

    # Cohen's Kappa Heatmap
    plt.figure(figsize=(20, 20))
    sns.heatmap(
        cohens_kappa_df,
        annot=True,
        square=True,
        linewidths=.5,
        fmt=".2f",
        vmin=-1,
        vmax=1
    )
    plt.title("Cohen's Kappa Between Model Predictions")

    plt.tight_layout()
    plt.show()


def _get_filter_string(filter_dict):
    """Helper function to convert filter_dict to a readable string for plot titles"""
    if filter_dict is None or len(filter_dict) == 0:
        return ""
    
    filter_parts = []
    for col, val in filter_dict.items():
        # Get the simplest column name for display (remove additional_info prefix)
        display_col = col.split('.')[-1] if '.' in col else col
        
        if isinstance(val, list):
            if len(val) == 1:
                filter_parts.append(f"{display_col}={val[0]}")
            else:
                val_str = ', '.join(str(v) for v in val)
                filter_parts.append(f"{display_col} in [{val_str}]")
        else:
            filter_parts.append(f"{display_col}={val}")
    
    return "\n(Filter: " + ", ".join(filter_parts) + ")"

def plot_metrics(
    df,
    group_by_column=None,
    filter_dict=None,
    model_filter=None
):
    """
    Plots metrics (accuracy, F1) after filtering the data.
    If group_by_column is provided, metrics are grouped by values of that column.
    If group_by_column is None, metrics are grouped by model (similar to the original function).
    
    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe containing the data.
        
    group_by_column : str or None
        The column whose values will be used to group and compare metrics.
        Example: "additional_info.prompting_technique"
        If None, metrics will be grouped by model (default behavior).
    
    filter_dict : dict or None
        A dictionary where keys are column names and values are either a single value 
        or a list of values to filter for. For instance:
            {
                "additional_info.subset_name": ["contractnli_a", "contractnli_b"]
            }
        If None, no filtering is performed.
        
    model_filter : str, list, or None
        If specified, only data for this model or models will be included.
        Can be a single model name or a list of model names.
        Examples: 
          - "Meta-Llama-3-8B-LOCAL"
          - ["Meta-Llama-3-8B-LOCAL", "Claude-3-Opus"]
    """
    
    # -------------------------
    # 1) Apply filtering (always happens first)
    # -------------------------
    df_filtered = df.copy()
    
    # Apply general filters from filter_dict
    if filter_dict is not None:
        for col, desired in filter_dict.items():
            # If desired is a list, use .isin(...)
            if isinstance(desired, list):
                df_filtered = df_filtered[df_filtered[col].isin(desired)]
            else:
                # Otherwise, filter by direct equality
                df_filtered = df_filtered[df_filtered[col] == desired]
    
    # Filter by specific model(s) if requested
    if model_filter is not None:
        # If model_filter is a list, use .isin()
        if isinstance(model_filter, list):
            df_filtered = df_filtered[df_filtered["additional_info.model"].isin(model_filter)]
        else:
            # For a single model as string
            df_filtered = df_filtered[df_filtered["additional_info.model"] == model_filter]
    
    if df_filtered.empty:
        print("No rows found after applying the given filters. Nothing to plot.")
        return
    
    # Create a human-readable filter string for plot titles
    filter_string = _get_filter_string(filter_dict)
    
    # -------------------------
    # 2) Group and compute means
    # -------------------------
    if group_by_column is None:
        # Original behavior - group only by model
        grouped = df_filtered.groupby("additional_info.model", as_index=False).agg({
            "result.accuracy": "mean",
            "result.f1_weighted": "mean",
            "result.f1_per_class.contradiction": "mean",
            "result.f1_per_class.entailment": "mean",
            "result.f1_per_class.neutral": "mean"
        })
        
        models = grouped["additional_info.model"].values
        accuracy_vals = grouped["result.accuracy"].values
        f1_weighted_vals = grouped["result.f1_weighted"].values
        f1_contra_vals = grouped["result.f1_per_class.contradiction"].values
        f1_entail_vals = grouped["result.f1_per_class.entailment"].values
        f1_neutral_vals = grouped["result.f1_per_class.neutral"].values
        
        # Plot metrics by model (original style)
        _plot_metrics_by_model(models, accuracy_vals, f1_weighted_vals, 
                           f1_contra_vals, f1_entail_vals, f1_neutral_vals, filter_string)
        
    else:
        # New behavior - group by model and the specified column
        # Preserve the order of factor values by getting them in order of first appearance
        factor_order = df_filtered[group_by_column].drop_duplicates().tolist()
        
        # Group by model and the specified factor
        grouped = df_filtered.groupby(["additional_info.model", group_by_column], as_index=False).agg({
            "result.accuracy": "mean",
            "result.f1_weighted": "mean",
            "result.f1_per_class.contradiction": "mean",
            "result.f1_per_class.entailment": "mean",
            "result.f1_per_class.neutral": "mean"
        })
        
        # Use Categorical data type with our custom order to ensure consistent ordering
        grouped[group_by_column] = pd.Categorical(
            grouped[group_by_column], 
            categories=factor_order,
            ordered=True
        )
        
        # Sort by model and then by the ordered factor
        grouped = grouped.sort_values(["additional_info.model", group_by_column])
        
        # Plot metrics by factor values
        _plot_metrics_by_factor(grouped, group_by_column, filter_string)


def _plot_metrics_by_model(models, accuracy_vals, f1_weighted_vals, 
                      f1_contra_vals, f1_entail_vals, f1_neutral_vals, filter_string=""):
    """Plot metrics grouped by model (original style)"""
    
    # =====================================================================
    # A) Plot Accuracy (one bar per model)
    # =====================================================================
    fig, ax = plt.subplots(figsize=(12, 6))
    bar_width = 0.6

    bars_acc = ax.bar(
        x=np.arange(len(models)),
        height=accuracy_vals,
        width=bar_width,
        color='skyblue'
    )

    ax.set_xlabel('Models', fontweight='bold')
    ax.set_ylabel('Accuracy', fontweight='bold')
    ax.set_title(f'Mean Accuracy by Model{filter_string}')
    ax.set_xticks(np.arange(len(models)))
    ax.set_xticklabels(models, rotation=45, ha='right')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Set y-axis limit to 1.0
    ax.set_ylim(0, 1.0)

    # Add data labels
    for bar, val in zip(bars_acc, accuracy_vals):
        ax.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.02,
            f'{val:.3f}',
            ha='center', 
            va='bottom'
        )

    plt.tight_layout()
    plt.show()

    # =====================================================================
    # B) Plot F1 (Weighted) (one bar per model)
    # =====================================================================
    fig, ax = plt.subplots(figsize=(12, 6))
    bars_f1 = ax.bar(
        x=np.arange(len(models)),
        height=f1_weighted_vals,
        width=bar_width,
        color='lightcoral'
    )

    ax.set_xlabel('Models', fontweight='bold')
    ax.set_ylabel('F1 Weighted', fontweight='bold')
    ax.set_title(f'Mean F1 (Weighted) by Model{filter_string}')
    ax.set_xticks(np.arange(len(models)))
    ax.set_xticklabels(models, rotation=45, ha='right')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Set y-axis limit to 1.0
    ax.set_ylim(0, 1.0)

    for bar, val in zip(bars_f1, f1_weighted_vals):
        ax.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.02,
            f'{val:.3f}',
            ha='center', 
            va='bottom'
        )

    plt.tight_layout()
    plt.show()

    # =====================================================================
    # C) Plot F1 per class (three bars per model)
    # =====================================================================
    fig, ax = plt.subplots(figsize=(12, 6))
    bar_width = 0.2

    # Positions for the bars
    r1 = np.arange(len(models))
    r2 = r1 + bar_width
    r3 = r2 + bar_width

    bars_contra = ax.bar(r1, f1_contra_vals, width=bar_width, label='Contradiction', color='skyblue')
    bars_entail = ax.bar(r2, f1_entail_vals, width=bar_width, label='Entailment', color='lightcoral')
    bars_neutral = ax.bar(r3, f1_neutral_vals, width=bar_width, label='Neutral', color='palegreen')

    ax.set_xlabel('Models', fontweight='bold')
    ax.set_ylabel('F1 Score', fontweight='bold')
    ax.set_title(f'Mean F1 per Class by Model{filter_string}')
    ax.set_xticks(r1 + bar_width)
    ax.set_xticklabels(models, rotation=45, ha='right')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.legend()
    
    # Set y-axis limit to 1.0
    ax.set_ylim(0, 1.0)

    # Add data labels
    for bar, val in zip(bars_contra, f1_contra_vals):
        ax.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.02,
            f'{val:.3f}',
            ha='center', 
            va='bottom'
        )

    for bar, val in zip(bars_entail, f1_entail_vals):
        ax.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.02,
            f'{val:.3f}',
            ha='center', 
            va='bottom'
        )

    for bar, val in zip(bars_neutral, f1_neutral_vals):
        ax.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.02,
            f'{val:.3f}',
            ha='center', 
            va='bottom'
        )

    plt.tight_layout()
    plt.show()


def _plot_metrics_by_factor(grouped, group_by_column, filter_string=""):
    """Plot metrics grouped by factor values"""
    
    # Get unique models
    unique_models = grouped["additional_info.model"].unique()
    num_models = len(unique_models)
    
    if num_models > 1:
        # For multiple models, use subplots to organize visually
        fig_height = 5 * num_models
        fig, axes = plt.subplots(num_models, 3, figsize=(18, fig_height))
        plt.subplots_adjust(hspace=0.4)
        
        for i, model in enumerate(unique_models):
            model_data = grouped[grouped["additional_info.model"] == model]
            
            factors = model_data[group_by_column].values
            accuracy_vals = model_data["result.accuracy"].values
            f1_weighted_vals = model_data["result.f1_weighted"].values
            f1_contra_vals = model_data["result.f1_per_class.contradiction"].values
            f1_entail_vals = model_data["result.f1_per_class.entailment"].values
            f1_neutral_vals = model_data["result.f1_per_class.neutral"].values
            
            # Plot accuracy
            _plot_single_metric(axes[i, 0], factors, accuracy_vals, 
                           f"Accuracy by {group_by_column.split('.')[-1]}{filter_string}", 
                           "Accuracy", model)
            
            # Plot F1 weighted
            _plot_single_metric(axes[i, 1], factors, f1_weighted_vals, 
                           f"F1 Weighted by {group_by_column.split('.')[-1]}{filter_string}", 
                           "F1 Weighted", model, color='lightcoral')
            
            # Plot F1 per class
            _plot_f1_per_class(axes[i, 2], factors, f1_contra_vals, f1_entail_vals, 
                          f1_neutral_vals, 
                          f"F1 per Class by {group_by_column.split('.')[-1]}{filter_string}", 
                          model)
        
        plt.tight_layout()
        plt.show()
    
    else:
        # For a single model, create three separate plots
        model = unique_models[0]
        model_data = grouped[grouped["additional_info.model"] == model]
        
        factors = model_data[group_by_column].values
        accuracy_vals = model_data["result.accuracy"].values
        f1_weighted_vals = model_data["result.f1_weighted"].values
        f1_contra_vals = model_data["result.f1_per_class.contradiction"].values
        f1_entail_vals = model_data["result.f1_per_class.entailment"].values
        f1_neutral_vals = model_data["result.f1_per_class.neutral"].values
        
        # =====================================================================
        # A) Plot Accuracy (one bar per factor value)
        # =====================================================================
        fig, ax = plt.subplots(figsize=(12, 6))
        _plot_single_metric(ax, factors, accuracy_vals, 
                       f"Accuracy by {group_by_column.split('.')[-1]} for {model}{filter_string}", 
                       "Accuracy")
        plt.tight_layout()
        plt.show()
        
        # =====================================================================
        # B) Plot F1 Weighted (one bar per factor value)
        # =====================================================================
        fig, ax = plt.subplots(figsize=(12, 6))
        _plot_single_metric(ax, factors, f1_weighted_vals, 
                       f"F1 Weighted by {group_by_column.split('.')[-1]} for {model}{filter_string}", 
                       "F1 Weighted", color='lightcoral')
        plt.tight_layout()
        plt.show()
        
        # =====================================================================
        # C) Plot F1 per Class (grouped bars)
        # =====================================================================
        fig, ax = plt.subplots(figsize=(12, 6))
        _plot_f1_per_class(ax, factors, f1_contra_vals, f1_entail_vals, f1_neutral_vals,
                      f"F1 per Class by {group_by_column.split('.')[-1]} for {model}{filter_string}")
        plt.tight_layout()
        plt.show()


def _plot_single_metric(ax, x_values, y_values, title, y_label, model=None, color='skyblue'):
    """Helper function to plot a single metric as bars"""
    
    bar_width = 0.6
    
    bars = ax.bar(
        x=np.arange(len(x_values)),
        height=y_values,
        width=bar_width,
        color=color
    )
    
    if model:
        ax.set_title(f"{title}\n(Model: {model})")
    else:
        ax.set_title(title)
        
    ax.set_xlabel('Factor Values', fontweight='bold')
    ax.set_ylabel(y_label, fontweight='bold')
    ax.set_xticks(np.arange(len(x_values)))
    ax.set_xticklabels(x_values, rotation=45, ha='right')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Set y-axis limit to 1.0
    ax.set_ylim(0, 1.0)
    
    # Add data labels
    for bar, val in zip(bars, y_values):
        ax.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.02,  # Adjusted to be more visible with fixed y-axis
            f'{val:.3f}',
            ha='center', 
            va='bottom'
        )
    
    return ax


def _plot_f1_per_class(ax, x_values, contra_vals, entail_vals, neutral_vals, title, model=None):
    """Helper function to plot F1 per class as grouped bars"""
    
    bar_width = 0.25
    
    # Positions for the bars
    r1 = np.arange(len(x_values))
    r2 = r1 + bar_width
    r3 = r2 + bar_width
    
    bars_contra = ax.bar(r1, contra_vals, width=bar_width, label='Contradiction', color='skyblue')
    bars_entail = ax.bar(r2, entail_vals, width=bar_width, label='Entailment', color='lightcoral')
    bars_neutral = ax.bar(r3, neutral_vals, width=bar_width, label='Neutral', color='palegreen')
    
    if model:
        ax.set_title(f"{title}\n(Model: {model})")
    else:
        ax.set_title(title)
        
    ax.set_xlabel('Factor Values', fontweight='bold')
    ax.set_ylabel('F1 Score', fontweight='bold')
    ax.set_xticks(r1 + bar_width)
    ax.set_xticklabels(x_values, rotation=45, ha='right')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.legend()
    
    # Set y-axis limit to 1.0
    ax.set_ylim(0, 1.0)
    
    # Add data labels
    for bar, val in zip(bars_contra, contra_vals):
        ax.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.02,  # Adjusted to be more visible with fixed y-axis
            f'{val:.3f}',
            ha='center', 
            va='bottom'
        )
    
    for bar, val in zip(bars_entail, entail_vals):
        ax.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.02,  # Adjusted for visibility
            f'{val:.3f}',
            ha='center', 
            va='bottom'
        )
    
    for bar, val in zip(bars_neutral, neutral_vals):
        ax.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.02,  # Adjusted for visibility
            f'{val:.3f}',
            ha='center', 
            va='bottom'
        )
    
    return ax


# Usage examples:
# 1. Original behavior - group by model after filtering
# plot_metrics(
#     df,
#     filter_dict={"additional_info.prompting_technique": "naive zero-shot"}
# )

# 2. New behavior - group by a specific column
# plot_metrics(
#     df,
#     group_by_column="additional_info.prompting_technique"
# )

# 3. With filtering and grouping
# plot_metrics(
#     df,
#     group_by_column="additional_info.prompting_technique",
#     filter_dict={"additional_info.subset_name": "contractnli_b"}
# )

# 4. For a specific model with filtering
# plot_metrics(
#     df,
#     group_by_column="additional_info.prompting_technique",
#     filter_dict={"additional_info.subset_name": "contractnli_b"},
#     model_filter="Meta-Llama-3-8B-LOCAL"
# )