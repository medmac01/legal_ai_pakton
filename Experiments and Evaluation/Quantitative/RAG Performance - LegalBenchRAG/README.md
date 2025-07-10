# RAG Performance - LegalBenchRAG Experiments

## Overview

This directory contains experimental evaluations of retrieval-augmented generation (RAG) systems on legal domain benchmarks using a modified version of the [LegalBenchRAG](https://github.com/zeroentropy-ai/legalbenchrag) framework. Our experiments focus on comparing different retrieval strategies, particularly the `PAKTON` framework, across multiple legal datasets.

These experiments are discussed in Section 4.1.2, Performance of RAG, and detailed further in Appendix B: Experiments on LegalBenchRAG of the paper.

## Project Structure

```
RAG Performance - LegalBenchRAG/
├── monitor.sh                      # Monitoring script for Dockerized PAKTON
├── legalbenchrag/                  # Modified LegalBenchRAG codebase
└── results/                        # Experimental results organized by retriever type for PAKTON
    ├── flagReranker/               # Results using flag-based reranking (Configuration 1 of the paper)
    │   ├── results_by_type_*.json  # Aggregated results for each dataset of the benchmark
    └── llmReranker/                # Results using LLM-based reranking (Configuration 2 of the paper)
```

## Datasets

The experiments were conducted on the following legal domain datasets:

- **ContractNLI**: A dataset for natural language inference on contracts
- **CUAD**: Contract Understanding Atticus Dataset
- **MAUD**: M&A Understanding Dataset
- **PrivacyQA**: Question answering dataset on privacy policies

## Modifications

[The original LegalBenchRAG codebase](https://github.com/zeroentropy-ai/legalbenchrag) was modified to accommodate the `PAKTON` evaluation.

## Results

Experimental results are organized in the `results` directory:

- **flagReranker**: Results using a flag-based reranking approach (configuration 1)
- **llmReranker**: Results using an LLM-based reranking approach (configuration 2)

Each subdirectory contains:
- JSON files with aggregated results for each benchmark

## Usage

To replicate these experiments:

1. Download the benchmark and corpus dataset:
   ```
   Visit [this link](https://www.dropbox.com/scl/fo/r7xfa5i3hdsbxex1w6amw/AID389Olvtm-ZLTKAPrw6k4?rlkey=5n8zrbk4c08lbit3iiexofmwg&st=0hu354cq&dl=0) to download the benchmarks and corpus data.
   ```

2. Set up your Python environment:
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install pip-tools
   pip-sync && pip install -e .
   ```

4. Configure your API credentials:
   ```bash
   vim ./credentials/credentials.toml
   ```

5. Run the benchmark evaluations using the legalbenchrag/benchmark.py script. When the --baseline flag is specified, the script evaluates the predefined baselines provided by LegalBenchRAG.

6. Before evaluating PAKTON, make sure that the docker-compose.yml is built and running.

## Monitoring Services

The `monitor.sh` script provides health monitoring for Docker containers running related services. It automatically restarts containers if they become unresponsive, ensuring continuous operation during long-running experiments.