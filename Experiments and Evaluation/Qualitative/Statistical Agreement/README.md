# Statistical Agreement Analysis

This directory contains the statistical agreement analysis between LLM-based evaluation (G-EVAL) and human expert judgments for the PAKTON framework evaluation. This analysis validates the consistency between automated and human evaluation methods, as presented in Appendix A.3 of the paper.

## Overview

The statistical agreement analysis demonstrates that LLM-based evaluation using G-EVAL framework aligns closely with human expert judgments, providing validation for the automated evaluation methodology. This analysis transforms absolute G-EVAL scores into categorical votes and compares them with human evaluation results to assess distributional similarity.

## Files Description

### `geval_scores.json`
Contains the raw G-EVAL scores for both PAKTON and GPT-4o across all evaluation criteria and test cases:
- **Structure**: Organized by test case, with scores for each system (PAKTON/GPT) across nine evaluation criteria
- **Criteria**: Justification with Evidence, Contextual and Legal Understanding, Handling Ambiguity, Acknowledgment of Knowledge Gaps, Conciseness and Precision, Coherence and Organization, Relevance and Focus, Completeness, Explainability and Reasoning
- **Format**: Numerical scores between 0 and 1 with detailed reasoning for each evaluation

### `human_aggregated_votes.json`
Contains aggregated human evaluation votes across the same criteria:
- **Structure**: Vote counts for each criterion across four categories
- **Categories**: 
  - `PAKTON`: Human evaluators preferred PAKTON's response
  - `GPT`: Human evaluators preferred GPT-4o's response  
  - `Neither`: No clear preference between systems
  - `I am not sure`: Evaluator uncertainty
- **Source**: Aggregated from human expert evaluations conducted via survey

### `statistical_agreement.ipynb`
Jupyter notebook containing the complete statistical analysis:
- **Transformation Process**: Converts G-EVAL absolute scores to categorical votes
- **Threshold Application**: Uses 1% difference threshold for tie determination
- **Distributional Analysis**: Compares vote distributions between LLM and human evaluations
- **Statistical Tests**: Includes cosine similarity, MAE/RMSE calculations, variance tests, and distribution tests

## Methodology

### Transformation Process
1. **Score Conversion**: G-EVAL absolute scores are transformed into categorical votes
2. **Tie Threshold**: If the difference between PAKTON and GPT-4o scores is < 1%, the outcome is classified as "Neither"
3. **Vote Assignment**: Otherwise, the vote goes to the system with the higher score
4. **Normalization**: Both LLM-derived and human votes are converted to percentages

### Statistical Measures
- **Cosine Similarity**: Measures distributional alignment between LLM and human votes
- **Mean Absolute Error (MAE)**: Quantifies percentage point differences
- **Root Mean Square Error (RMSE)**: Provides variance-sensitive error measurement
- **Variance Tests**: F-tests to compare dispersion between methods
- **Distribution Tests**: Kolmogorov-Smirnov and Mann-Whitney U tests for distributional differences

## Key Findings

### Overall Agreement
- **Average Cosine Similarity**: 0.88 across all criteria
- **Average MAE**: 12.6% between LLM and human distributions
- **Statistical Significance**: No significant differences in variance or distributions (all p ≥ 0.05)

### Outlier-Excluded Analysis
After removing the "Contextual and Legal Understanding" criterion (identified as a G-EVAL framework interpretation issue):
- **Improved Cosine Similarity**: 0.9164 average
- **Reduced MAE**: 10.88% average
- **Enhanced RMSE**: 14.06% average

### Strongest Agreement Criteria
1. **Completeness**: Cosine similarity 0.9992, MAE 1.77%
2. **Explainability and Reasoning**: Cosine similarity 0.9915, MAE 4.07%
3. **Relevance and Focus**: Cosine similarity 0.9901, MAE 3.86%
4. **Justification with Evidence**: Cosine similarity 0.9751, MAE 6.69%
5. **Acknowledgment of Knowledge Gaps**: Cosine similarity 0.9769, MAE 7.24%

## Usage

### Running the Analysis
```bash
# Navigate to the directory
cd "Experiments and Evaluation/Qualitative/Statistical Agreement"

# Open the Jupyter notebook
jupyter notebook statistical_agreement.ipynb
```

### Requirements
- Python 3.x
- Jupyter Notebook
- Standard libraries: json, os, collections
- Additional libraries for statistical analysis (if extended): numpy, scipy, pandas

## Implications

The statistical agreement analysis provides crucial validation for the G-EVAL framework as a reliable automated evaluation method:

1. **Methodology Validation**: Demonstrates that LLM-based evaluation can serve as a proxy for human expert judgment
2. **Framework Reliability**: Shows consistent distributional patterns between automated and human assessments  
3. **Quality Assurance**: Provides confidence in the automated evaluation results presented in the main paper
4. **Future Applications**: Supports the use of G-EVAL for large-scale evaluation where human assessment is impractical

## Citation Context

This analysis supports the findings presented in Section 4.3 of the paper, where G-EVAL framework results are used to compare PAKTON and GPT-4o performance. The statistical agreement validates that the automated evaluation methodology produces results consistent with human expert judgment, lending credibility to the reported performance differences between systems.

## Related Directories

- `../LLM as a judge - GEVAL/`: Contains the G-EVAL framework implementation and raw results
- `../Human Evaluation/`: Contains the human evaluation survey data and aggregated results
- `../../Quantitative/`: Contains quantitative evaluation results that complement these qualitative findings
