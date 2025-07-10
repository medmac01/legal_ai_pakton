# Experiments and Evaluation

This directory contains all experimental implementations and evaluation results for the PAKTON framework, corresponding to **Section 4: Experiments and Results** of the paper. The directory is organized into quantitative and qualitative evaluation methodologies.

The frontend of the experiments is deployed at https://pakton.site/evaluation/

## Directory Structure

```
Experiments and Evaluation/                         # Directory for experiments and results 
├── README.md                                       # This file
├── Frontend/                                       # Frontend to display the results of the experiments
├── Qualitative/                                    # Qualitative evaluation methods
│   ├── Human Evaluation/                           # Human-based evaluation - survey and results - Section 4.2 of the paper
│   └── LLM as a judge - GEVAL/                     # G-EVAL automated evaluation - Section 4.3 of the paper
└── Quantitative/                                   # Quantitative evaluation methods
    ├── Classification Performance - ContractNLI/   # ContractNLI dataset evaluation - Section 4.1.1 of the paper
    └── RAG Performance - LegalBenchRAG/            # LegalBenchRAG dataset evaluation - Section 4.1.2 of the paper
```

## Overview

The experiments evaluate PAKTON's performance across multiple dimensions:

### Quantitative Evaluation
- **Classification Performance**: Evaluation on ContractNLI dataset (Section 4.1.1)
- **RAG Performance**: Evaluation on LegalBenchRAG dataset (Section 4.1.2)

### Qualitative Evaluation
- **G-EVAL Framework**: LLM-based evaluation of response quality (Section 4.3)
- **Human Evaluation**: Human expert assessment of generated responses

## Key Experimental Components

### 1. ContractNLI Classification (Section 4.1.1)
Located in `Quantitative/Classification Performance - ContractNLI/`

- **Purpose**: Evaluate PAKTON's performance on natural language inference tasks for contracts
- **Dataset**: ContractNLI - specialized NLI dataset for contract analysis
- **Models Evaluated**: OpenAI, Google, Anthropic, AWS Bedrock, DeepSeek, Qwen, Local models, and PAKTON
- **Results**: Comprehensive performance metrics stored in `results/` directory

### 2. LegalBenchRAG Performance (Section 4.1.2)
Located in `Quantitative/RAG Performance - LegalBenchRAG/`

- **Purpose**: Evaluate retrieval-augmented generation performance on legal benchmarks
- **Dataset**: LegalBenchRAG - legal domain question-answering dataset
- **Focus**: Information retrieval and generation quality in legal contexts

### 3. G-EVAL Qualitative Assessment (Section 4.3)
Located in `Qualitative/LLM as a judge - GEVAL/`

- **Purpose**: Automated qualitative evaluation using LLM judges
- **Framework**: G-EVAL methodology for comprehensive response assessment
- **Criteria**: Multiple evaluation dimensions including accuracy, relevance, and coherence
- **Comparison**: PAKTON vs. GPT-4o with reasoning capabilities

### 4. Human Evaluation
Located in `Qualitative/Human Evaluation/`

- **Purpose**: Human assessment of system outputs
- **Evaluators**: Legal domain experts
- **Metrics**: Human-perceived quality

## Results Summary

The experiments demonstrate PAKTON's effectiveness across multiple evaluation scenarios:

- **Quantitative Performance**: Competitive results on standard legal NLP benchmarks
- **Qualitative Assessment**: High-quality responses as evaluated by both LLM judges and human experts
