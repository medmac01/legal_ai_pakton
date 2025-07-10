# Classification Performance - ContractNLI

This directory contains the experimental setup and results for evaluating Large Language Models (LLMs) on the ContractNLI dataset, as described in **Section 4.1.1 Performance on a classification dataset** of the PAKTON paper.

## Overview

The ContractNLI dataset is a specialized natural language inference dataset designed for contract analysis tasks. Our experiments evaluate the performance of various LLM providers using different prompting techniques, including the novel PAKTON multi-agent framework.

**Dataset Reference:** [ContractNLI: A Dataset for Document-level Natural Language Inference for Contracts](https://aclanthology.org/2021.findings-emnlp.164/)

## Prerequisites

Before running the experiments, ensure you have:

1. **PAKTON Framework Setup**: The PAKTON framework must be properly configured and running. Refer to:
   - Section 4.1.1 of the paper for configuration details
   - Appendix C - Experiments on ContractNLI for specific setup instructions

2. **API Access**: Valid API keys for the LLM providers you wish to evaluate (OpenAI, Google, Anthropic, AWS Bedrock, etc.)

## Project Structure

```
Classification Performance - ContractNLI/
├── results/                            # Experimental results and outputs
├── experimentsLibrary/                 # Core experiment library
└── README.md                          # This documentation
```

## Results Format

Each experiment generates detailed JSON results containing:
- **Accuracy Metrics**: Overall performance scores
- **Confusion Matrices**: Classification breakdown
- **Per-Example Predictions**: Individual model responses
- **Execution Metadata**: Timestamps, duration, and configuration details

## Key Findings

The experiments demonstrate the effectiveness of the PAKTON multi-agent framework compared to traditional prompting approaches on contract understanding tasks. Detailed results and analysis are available in the paper's Section 4.1.1.

## Citation

If you use this experimental setup or results in your research, please cite:

```bibtex
@article{Raptopoulos2025PAKTONAM,
  title={PAKTON: A Multi-Agent Framework for Question Answering in Long Legal Agreements},
  author={Petros Raptopoulos and Giorgos Filandrianos and Maria Lymperaiou and G. Stamou},
  journal={ArXiv},
  year={2025},
  volume={abs/2506.00608},
  url={https://api.semanticscholar.org/CorpusID:279074875}
}
```

## Support

For questions or issues related to the experiments, please refer to the main PAKTON documentation or contact the authors.