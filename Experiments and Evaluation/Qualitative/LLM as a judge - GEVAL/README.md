# LLM as a judge - G-EVAL Evaluation

## Overview

This directory contains the evaluation script of the G-Eval framework for evaluating the outputs of PAKTON and GPT-4o (RAG) in a qualitative manner. The experiments take into account multiple evaluation criteria.

Section 4.3 Evaluation using LLMs and Appendix E - G-EVAL Experiments of the paper provide more technical details.

The frontend for these experiments is available at https://pakton.site/evaluation/geval

## Directory Structure

```
GEVAL_EXPERIMENTS/
├── Geval.ipynb           # Main implementation notebook
├── README.md             # This file
└── results/              # Evaluation results and predictions
    ├── geval_aggregated_evaluation_scores.json  # Aggregated scores
    ├── geval_scores.json                        # Detailed scores
    ├── predictionsGPTreasoning.json             # GPT model outputs
    └── predictionsPAKTON.json                   # PAKTON model outputs
```

## Implementation Details

The G-Eval framework employs GPT-4o as an evaluator to score model outputs across 9 key dimensions:

1. **Explainability and Reasoning** - Clarity and transparency in explaining conclusions with step-by-step reasoning
2. **Justification with Evidence** - Use of specific citations and quotations from source materials
3. **Contextual and Legal Understanding** - Grasp of legal terminology and document context
4. **Handling Ambiguity** - Addressing multiple interpretations appropriately
5. **Acknowledgment of Knowledge Gaps** - Transparency about limitations in available information
6. **Conciseness and Precision** - Clear and efficient communication
7. **Coherence and Organization** - Logical structure and smooth transitions
8. **Relevance and Focus** - Staying on topic and addressing the query directly
9. **Completeness** - Covering all important aspects of the query

## Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key
- Required packages:
  - deepeval
  - tqdm

### Installation

```bash
pip install deepeval tqdm
```

### Usage

1. Open `Geval.ipynb` in Jupyter Notebook or JupyterLab
2. Set your OpenAI API key in the notebook
3. Run all cells to perform evaluation
4. Results will be saved to the `results/` directory

## Evaluation Pipeline

1. **Test Case Preparation**: The notebook creates test cases from PAKTON and GPT-4o outputs for the same inputs
2. **Metric Evaluation**: Each model's output is evaluated using the defined metrics
3. **Score Calculation**: Scores are calculated for each criterion and saved
4. **Data Consolidation**: Multiple evaluation runs are combined into a final dataset

## Results Format

The evaluation results are stored in JSON format:

- `geval_scores.json`: Contains detailed scores for each test case
- `geval_aggregated_evaluation_scores.json`: Contains aggregated scores across all test cases

## References

- DeepEval Documentation: [https://docs.deepeval.com/](https://docs.deepeval.com/)
- G-Eval Paper: [Zheng, L., et al. (2023). G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment](https://arxiv.org/abs/2303.16634)