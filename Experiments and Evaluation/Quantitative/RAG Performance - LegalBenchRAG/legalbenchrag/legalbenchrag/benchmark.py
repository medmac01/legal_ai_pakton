import asyncio
import datetime as dt
import os
import random
import argparse

import pandas as pd

from legalbenchrag.benchmark_types import Benchmark, Document, QAGroundTruth
from legalbenchrag.methods.baseline import BaselineRetrievalMethod
from legalbenchrag.methods.retrieval_strategies import RETRIEVAL_STRATEGIES
from legalbenchrag.methods.pakton import PAKTON
from legalbenchrag.run_benchmark import run_benchmark, run_benchmark_sequentially

# Function to calculate F1 score
def calculate_f1(precision: float, recall: float) -> float:
    """Calculate F1 score from precision and recall."""
    if precision + recall == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)

benchmark_name_to_weight: dict[str, float] = {
    "privacy_qa": 0.25,
    "contractnli": 0.25,
    "maud": 0.25,
    "cuad": 0.25,
}

# This takes a random sample of the benchmark, to speed up query processing.
# p-values can be calculated, to statistically predict the theoretical performance on the "full test"
# MAX_TESTS_PER_BENCHMARK = 194
MAX_TESTS_PER_BENCHMARK = 194
# This sorts the tests by document,
# so that the MAX_TESTS_PER_BENCHMARK tests are over the fewest number of documents,
# This speeds up ingestion processing, but
# p-values cannot be calculated, because this settings drastically reduces the search space size.
SORT_BY_DOCUMENT = False

async def main() -> None:
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run LegalBenchRAG benchmarks')
    parser.add_argument('--baseline', action='store_true', 
                        help='Run baseline retrieval strategies (if not specified, only PAKTON will run)')
    args = parser.parse_args()

    all_tests: list[QAGroundTruth] = []
    weights: list[float] = []
    document_file_paths_set: set[str] = set()
    used_document_file_paths_set: set[str] = set()
    for benchmark_name, weight in benchmark_name_to_weight.items():
        with open(f"./data/benchmarks/{benchmark_name}.json") as f:
            benchmark = Benchmark.model_validate_json(f.read())
            tests = benchmark.tests
            document_file_paths_set |= {
                snippet.file_path for test in tests for snippet in test.snippets
            }
            # Cap queries for a given benchmark
            if len(tests) > MAX_TESTS_PER_BENCHMARK:
                if SORT_BY_DOCUMENT:
                    # Use random based on file path seed, rather than the file path itself, to prevent bias.
                    tests = sorted(
                        tests,
                        key=lambda test: (
                            random.seed(test.snippets[0].file_path),
                            random.random(),
                        )[1],
                    )
                else:
                    # Keep seed consistent, for better caching / testing.
                    random.seed(benchmark_name)
                    random.shuffle(tests)
                tests = tests[:MAX_TESTS_PER_BENCHMARK]
            used_document_file_paths_set |= {
                snippet.file_path for test in tests for snippet in test.snippets
            }
            for test in tests:
                test.tags = [benchmark_name]
            all_tests.extend(tests)
            weights.extend([weight / len(tests)] * len(tests))
    benchmark = Benchmark(
        tests=all_tests,
    )

    # Create corpus (sorted for consistent processing)
    corpus: list[Document] = []
    for document_file_path in sorted(
        document_file_paths_set
        if not SORT_BY_DOCUMENT
        else used_document_file_paths_set
    ):
        with open(f"./data/corpus/{document_file_path}") as f:
            corpus.append(
                Document(
                    file_path=document_file_path,
                    content=f.read(),
                )
            )

    # Create a save location for this run
    run_name = dt.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    benchmark_path = f"./benchmark_results/{run_name}"
    os.makedirs(benchmark_path, exist_ok=True)

    rows: list[dict[str, str | None | int | float]] = []
    
    # Run baseline retrieval strategies benchmarks (only if --baseline flag is set)
    if args.baseline:
        print("\n--- Running Baseline Benchmarks ---")
        for i, retrieval_strategy in enumerate(RETRIEVAL_STRATEGIES):
            retrieval_method = BaselineRetrievalMethod(
                retrieval_strategy=retrieval_strategy,
            )
            print(f"Num Documents: {len(corpus)}")
            print(
                f"Num Corpus Characters: {sum(len(document.content) for document in corpus)}"
            )
            print(f"Num Queries: {len(benchmark.tests)}")

            benchmark_result = await run_benchmark(
                benchmark.tests,
                corpus,
                retrieval_method,
                weights=weights,
            )

            # Save the results
            with open(f"{benchmark_path}/{i}_results.json", "w") as f:
                f.write(benchmark_result.model_dump_json(indent=4))

            row: dict[str, str | None | int | float] = {
                "i": i,
                "method": "baseline",
                "chunk_strategy_name": retrieval_strategy.chunking_strategy.strategy_name,
                "chunk_size": retrieval_strategy.chunking_strategy.chunk_size,
                "top_k": retrieval_strategy.embedding_topk,
                "rerank_model": retrieval_strategy.rerank_model.company
                if retrieval_strategy.rerank_model is not None
                else None,
                "top_k_rerank": retrieval_strategy.rerank_topk,
                "token_limit": retrieval_strategy.token_limit,
            }
            row["recall"] = benchmark_result.avg_recall
            row["precision"] = benchmark_result.avg_precision
            row["f1"] = calculate_f1(benchmark_result.avg_precision, benchmark_result.avg_recall)
            for benchmark_name in benchmark_name_to_weight:
                avg_recall, avg_precision = benchmark_result.get_avg_recall_and_precision(
                    benchmark_name
                )
                row[f"{benchmark_name}|recall"] = avg_recall
                row[f"{benchmark_name}|precision"] = avg_precision
                row[f"{benchmark_name}|f1"] = calculate_f1(avg_precision, avg_recall)
                print(f"{benchmark_name} Avg Recall: {100*avg_recall:.2f}%")
                print(f"{benchmark_name} Avg Precision: {100*avg_precision:.2f}%")
                print(f"{benchmark_name} Avg F1: {100*calculate_f1(avg_precision, avg_recall):.2f}%")
            print(f"Avg Recall: {100*benchmark_result.avg_recall:.2f}%")
            print(f"Avg Precision: {100*benchmark_result.avg_precision:.2f}%")
            print(f"Avg F1: {100*calculate_f1(benchmark_result.avg_precision, benchmark_result.avg_recall):.2f}%")
            rows.append(row)
        
    else:

        # Run PAKTON benchmark (always run this)
        print("\n--- Running PAKTON Benchmark ---")
        pakton_method = PAKTON()
        benchmark_results = await run_benchmark_sequentially(
            benchmark.tests,
            corpus,
            pakton_method,
            weights=weights,
        )
        
        # Save the PAKTON results
        with open(f"{benchmark_path}/pakton_results.json", "w") as f:
            # Convert dictionary of BenchmarkResult objects to a serializable dictionary
            serializable_results = {
                key: value.model_dump() for key, value in benchmark_results.items()
            }
            import json
            json.dump(serializable_results, f, indent=4)
        
        # Add PAKTON results to the rows list for each response type
        for response_type, benchmark_result in benchmark_results.items():
            pakton_index = len(RETRIEVAL_STRATEGIES) if args.baseline else 0
            pakton_row: dict[str, str | None | int | float] = {
                "i": pakton_index,
                "method": f"pakton_{response_type}",
                "response_type": response_type,
                "chunk_strategy_name": "structural parsing",
                "top_k": "100",
                "rerank_model": "yes",
                "top_k_rerank": "top_10 with relevance filtering "
            }
            pakton_row["recall"] = benchmark_result.avg_recall
            pakton_row["precision"] = benchmark_result.avg_precision
            pakton_row["f1"] = calculate_f1(benchmark_result.avg_precision, benchmark_result.avg_recall)
            
            print(f"\n--- PAKTON {response_type} Results ---")
            for benchmark_name in benchmark_name_to_weight:
                avg_recall, avg_precision = benchmark_result.get_avg_recall_and_precision(
                    benchmark_name
                )
                pakton_row[f"{benchmark_name}|recall"] = avg_recall
                pakton_row[f"{benchmark_name}|precision"] = avg_precision
                pakton_row[f"{benchmark_name}|f1"] = calculate_f1(avg_precision, avg_recall)
                print(f"{benchmark_name} Avg Recall: {100*avg_recall:.2f}%")
                print(f"{benchmark_name} Avg Precision: {100*avg_precision:.2f}%")
                print(f"{benchmark_name} Avg F1: {100*calculate_f1(avg_precision, avg_recall):.2f}%")
            print(f"Avg Recall: {100*benchmark_result.avg_recall:.2f}%")
            print(f"Avg Precision: {100*benchmark_result.avg_precision:.2f}%")
            print(f"Avg F1: {100*calculate_f1(benchmark_result.avg_precision, benchmark_result.avg_recall):.2f}%")
            rows.append(pakton_row)
    
    # Create and save the DataFrame with all results
    df = pd.DataFrame(rows)
    df.to_csv(f"{benchmark_path}/results.csv", index=False)

    print(f'All Benchmark runs saved to: "{benchmark_path}"')


if __name__ == "__main__":
    asyncio.run(main())
