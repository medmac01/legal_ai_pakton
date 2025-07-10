# ContractNLI Experiments Library

## Overview

This repository contains a library for evaluating the performance of various Large Language Models (LLMs) on the ContractNLI dataset using different prompting techniques. ContractNLI is a natural language inference dataset specifically designed for contract analysis tasks.

## Project Goals

The primary objectives of this project are:

1. Evaluate the performance of various LLM providers (OpenAI, Google, Anthropic, AWS Bedrock, etc.) on contract understanding tasks
2. Compare different prompting techniques to identify optimal approaches for contract analysis
3. Provide a standardized framework for reproducible experiments in legal NLP
4. Generate insights on model capabilities for natural language inference on contractual documents

## Project Structure

```
Classification Performance - ContractNLI/
├── results/                            # Results obtained using the experimentsLibrary, detailed json with details and outputs
├── experimentsLibrary/                 # Main experiment library
│   ├── exampleScript.py                # Example usage of the library
│   ├── experimentsScript.py            # Main script for running experiments
│   ├── README.md                       # This documentation
│   ├── requirements.txt                # Python dependencies
│   ├── setup.py                        # Package installation configuration

│   ├── src/                            # Source code for the library
│   │   └── experimentsLibrary/         # Core module implementation
│   │      ├── models.py                # Definitions of models (LLMs) used
│   │      └── huggingfaceDatasets.py   # Definitions of datasets and prompting techniques used
│   └── tests/                          # Unit tests for library components
```

## Supported Models and APIs

The framework supports evaluation of models from the following providers:
- OpenAI (GPT models)
- Google (Gemini models)
- Anthropic (Claude models)
- AWS Bedrock (various foundation models)
- HuggingFace (open-source models)
- Local models (Llama, DeepSeek Distill, etc.)

## Prompting Techniques

The following prompting strategies are implemented and evaluated amongst others:
- Naive zero-shot prompting
- Optimized zero-shot prompting
- Naive few-shot prompting
- Few-shot with isolated spans
- Few-shot with isolated spans and same hypothesis
- Chain-of-thought reasoning with few-shot examples
- PAKTON

## Setup Instructions

### Prerequisites
- Python 3.8+

### Installation

1. Clone this directory
2. Create and activate a virtual environment (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the library in development mode
   ```bash
   pip install -e .
   ```
4. Configure your API credentials:
   ```bash
   cp .env.example .env
   # Edit .env to add your API keys for various providers
   ```
   
If evaluating with the MUTLIAGENT_FRAMEWORK_API make sure that PAKTON's docker-compose.yml is built and running.

## Running Experiments

### Basic Usage

The `experimentsScript.py` file demonstrates how to run experiments:

```python
import experimentsLibrary
from datetime import datetime

# Configure your experiment
prompting_technique = "optimized zero-shot"  
model_subset = [experimentsLibrary.models[0]]  # Select models to evaluate
subset_name = "contractnli_b"  # Dataset subset to use

# Initialize dataset with desired prompting technique
dataset_handler = experimentsLibrary.ContractNLIDataset(
    prompting_technique=prompting_technique, 
    subset_name=subset_name
)

# Run evaluation
for model in model_subset:
    result = experimentsLibrary.testAndEvaluate(
        dataset_handler.dataset["test"],
        model,
        dataset_handler.get_str_to_int_function(),
        dataset_handler.get_int_to_str_function(),
        dataset_handler.get_prompt_generator(),
        response_checker=dataset_handler.responseChecker
    )
    
    # Save results
    experimentsLibrary.save_result_to_file(
        result,
        {
            "model": model['name'],
            "API": model['API'],
            "prompting_technique": prompting_technique,
            "subset_name": subset_name
        },
        "results.json"
    )
```

### Running Tests

1. Test all APIs and models:
   ```bash
   python -m unittest discover -s tests -p "test_*.py"
   ```

2. Test a specific component:
   ```bash
   python -m unittest tests/test_bedrock.py
   # or
   python -m unittest tests.test_bedrock
   ```

### GPU Configuration

To specify which GPUs to use:
```bash
export CUDA_VISIBLE_DEVICES=0,1,2,3
```

### Running in Background

To run experiments in the background:
```bash
nohup python experimentsScript.py > output.log 2>&1 &
```

## Results and Analysis

Experiment results are saved in JSON format and include:
- Accuracy metrics
- Confusion matrices
- Per-example predictions
- Execution metadata (timestamps, duration)

## Known Issues and Limitations

- Ensure numpy version is 1.26 and not newer due to compatibility issues with certain models. See [this issue](https://github.com/meta-llama/llama/issues/380#issuecomment-2609891368).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this framework in your research, please cite:
```
@article{Raptopoulos2025PAKTONAM,
  title={PAKTON: A Multi-Agent Framework for Question Answering in Long Legal Agreements},
  author={Petros Raptopoulos and Giorgos Filandrianos and Maria Lymperaiou and G. Stamou},
  journal={ArXiv},
  year={2025},
  volume={abs/2506.00608},
  url={https://api.semanticscholar.org/CorpusID:279074875}
}
```