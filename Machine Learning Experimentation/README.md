# LLM Output Meta-Learning System

This repository contains a machine learning library designed for analyzing, comparing, and improving the outputs of Large Language Models (LLMs). The framework uses meta-learning techniques to train models that can predict correct outputs based on the predictions of various LLMs. The goal is to see if the outputs of the different LLMs are correlated and how we can combine them in order to increase performance.

## Overview

The system provides tools for:

1. **Analyzing LLM Outputs**: Compare outputs from different LLMs on the same tasks
2. **Meta-Learning**: Train machine learning models that learn from LLM predictions
3. **Visualization**: Generate plots and metrics to analyze model performance
4. **Model Improvement**: Techniques including PCA, oversampling, and undersampling

## Directory Structure

```
MachineLearning/
├── ML_on_LLM_outputs.ipynb        # Main notebook with examples
├── MachineLearning/               # Core library code
│   ├── __init__.py                # Package initialization
│   ├── advancedGridSearch.py      # Extended grid search functionality
│   ├── classifiersConfig.py       # Configuration for different classifiers
│   ├── evaluation.py              # Model evaluation functions
│   ├── gridSearch.py              # Basic grid search implementation
│   ├── logging.py                 # Result logging utilities
│   ├── metaLearning.py            # Main meta-learning pipeline
│   ├── pca.py                     # Principal Component Analysis
│   ├── plotting.py                # Visualization functions
│   ├── preprocessing.py           # Data preparation utilities
│   ├── sampling.py                # Over/undersampling functions
│   └── utils.py                   # Miscellaneous utilities
├── plots/                         # Generated plot output
└── results/                       # Experiment results
    ├── logs/                      # Log files
    ├── models/                    # Saved model files
    └── plots/                     # Experiment-specific plots
```

## Usage

### Installing Dependencies

```bash
cd MachineLearning
pip install -r MachineLearning/requirements.txt
```

### Basic Meta-Learning Pipeline

```python
from MachineLearning.metaLearning import meta_learning

# Basic usage without rebalancing or PCA
overall_best, best_models, model_metrics = meta_learning(
    df_preds,  # DataFrame with model predictions and ground truth
    test_size=0.2,
    use_pca=False,
    do_oversample=False,
    do_undersample=False
)
```

### With Dimensionality Reduction (PCA)

```python
overall_best, best_models, model_metrics = meta_learning(
    df_preds,
    test_size=0.2,
    save_dir="results_pca",
    use_pca=True,
    pca_variance_threshold=0.95
)
```

### With Class Balancing

```python
# With oversampling
overall_best, best_models, model_metrics = meta_learning(
    df_preds,
    test_size=0.2,
    save_dir="results_oversampling",
    use_pca=False,
    do_oversample=True
)

# With undersampling
overall_best, best_models, model_metrics = meta_learning(
    df_preds,
    test_size=0.2,
    save_dir="results_undersampling",
    use_pca=False,
    do_undersample=True
)
```

### Visualization

```python
from MachineLearning.plotting import plot_metrics, plot_CorrelationHeatmap, plot_agreement_heatmaps

# Plot metrics for specific filter conditions
plot_metrics_for_filter(df, filter_dict={
    "additional_info.prompting_technique": "naive zero-shot",
    "additional_info.subset_name": "contractnli_b"
})

# Plot correlation heatmap
plot_CorrelationHeatmap(df_preds, name_map)

# Plot agreement heatmaps
plot_agreement_heatmaps(df_preds)
```

## Performance

The system has been tested with various classifier models:

- Logistic Regression
- Decision Tree Classifier
- Random Forest Classifier
- Gradient Boosting Classifier
- Support Vector Machine (SVC)
- Multi-layer Perceptron (Neural Network)
- Gaussian Naive Bayes
- K-Nearest Neighbors

Results are available in the `results/logs/` directory showing performance metrics including:
- Accuracy
- F1 Score (weighted)
- Per-class F1 scores
- Precision and Recall

## Analysis of LLM Performance

The system has been used to analyze outputs from various LLMs:
- Meta-Llama-3-8B
- ChatGPT-4o
- Claude 3 Opus
- Claude 3.5 Sonnet v2

Performance analysis is available in the main notebook `ML_on_LLM_outputs.ipynb`.