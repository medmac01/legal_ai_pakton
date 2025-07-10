import asyncio
import json
import os
from collections.abc import Coroutine
from typing import Any

from pydantic import BaseModel, computed_field, model_validator
from typing_extensions import Self
from tqdm import tqdm

from legalbenchrag.benchmark_types import (
    Document,
    QAGroundTruth,
    RetrievalMethod,
    RetrievedSnippet,
    QueryResponse
)

class QAResult(BaseModel):
    qa_gt: QAGroundTruth
    retrieved_snippets: list[RetrievedSnippet]

    @computed_field  # type: ignore[misc]
    @property
    def precision(self) -> float:
        total_retrieved_len = 0
        relevant_retrieved_len = 0
        for snippet in self.retrieved_snippets:
            total_retrieved_len += snippet.span[1] - snippet.span[0]
            # It's guaranteed that gt_snippets don't overlap
            for gt_snippet in self.qa_gt.snippets:
                if snippet.file_path == gt_snippet.file_path:
                    common_min = max(snippet.span[0], gt_snippet.span[0])
                    common_max = min(snippet.span[1], gt_snippet.span[1])
                    if common_max > common_min:
                        relevant_retrieved_len += common_max - common_min
        if total_retrieved_len == 0:
            return 0
        return relevant_retrieved_len / total_retrieved_len

    @computed_field  # type: ignore[misc]
    @property
    def recall(self) -> float:
        total_relevant_len = 0
        relevant_retrieved_len = 0
        for gt_snippet in self.qa_gt.snippets:
            total_relevant_len += gt_snippet.span[1] - gt_snippet.span[0]
            # It's guaranteed that gt_snippets don't overlap
            for snippet in self.retrieved_snippets:
                if snippet.file_path == gt_snippet.file_path:
                    common_min = max(snippet.span[0], gt_snippet.span[0])
                    common_max = min(snippet.span[1], gt_snippet.span[1])
                    if common_max > common_min:
                        relevant_retrieved_len += common_max - common_min
        if total_relevant_len == 0:
            return 0
        return relevant_retrieved_len / total_relevant_len


def avg(arr: list[float]) -> float:
    if len(arr) == 0:
        return float("nan")
    return sum(arr) / len(arr)


class BenchmarkResult(BaseModel):
    qa_result_list: list[QAResult]
    weights: list[float]

    def get_avg_recall_and_precision(
        self, tag_filter: str | None = None
    ) -> tuple[float, float]:
        indices = [
            i
            for i, qa_result in enumerate(self.qa_result_list)
            if (tag_filter is None or tag_filter in qa_result.qa_gt.tags)
        ]
        filtered_qa_results = [self.qa_result_list[i] for i in indices]
        filtered_weights = [self.weights[i] for i in indices]
        avg_weight = avg(filtered_weights)
        return (
            avg(
                [
                    qa_result.recall * weight / avg_weight
                    for qa_result, weight in zip(filtered_qa_results, filtered_weights)
                ]
            ),
            avg(
                [
                    qa_result.precision * weight / avg_weight
                    for qa_result, weight in zip(filtered_qa_results, filtered_weights)
                ]
            ),
        )

    @computed_field  # type: ignore[misc]
    @property
    def avg_precision(self) -> float:
        return self.get_avg_recall_and_precision()[1]

    @computed_field  # type: ignore[misc]
    @property
    def avg_recall(self) -> float:
        return self.get_avg_recall_and_precision()[0]

    @model_validator(mode="after")
    def validate_lengths(self) -> Self:
        if len(self.qa_result_list) != len(self.weights):
            raise ValueError("length of qa_result_list and weights do not match!")
        return self


async def run_benchmark(
    qa_gt_list: list[QAGroundTruth],
    corpus: list[Document],
    retrieval_method: RetrievalMethod,
    *,
    weights: list[float] | None = None,
) -> BenchmarkResult:
    # Process the documents
    for document in corpus:
        # Filter qa_gt_list to only include those for this document
        grouped_qa_gt_list = [
            qa_gt for qa_gt in qa_gt_list
            if qa_gt.snippets[0].file_path == document.file_path
        ]

        # If no qa_gt remains, skip to the next document
        if not grouped_qa_gt_list:
            print(f"Skipping {document.file_path} as all queries are already processed.")
            continue
        await retrieval_method.ingest_document(document)
    await retrieval_method.sync_all_documents()

    # Run the benchmark
    async def run_query(qa_gt: QAGroundTruth) -> QAResult:
        query_response = await retrieval_method.query(qa_gt.query)
        return QAResult(
            qa_gt=qa_gt, retrieved_snippets=query_response.retrieved_snippets
        )

    tasks: list[Coroutine[Any, Any, QAResult]] = [
        run_query(qa_gt) for qa_gt in qa_gt_list
    ]
    results = await asyncio.gather(*tasks)

    await retrieval_method.cleanup()

    return BenchmarkResult(
        qa_result_list=results,
        weights=weights if weights is not None else [1.0] * len(results),
    )

async def run_benchmark_sequentially(
    qa_gt_list: list[QAGroundTruth],
    corpus: list[Document],
    retrieval_method: RetrievalMethod,
    *,
    weights: list[float] | None = None,
) -> dict[str, BenchmarkResult]:
    # Process the documents and query sequentially
    print("Length of corpus:", len(corpus))
    print("Length of qa_gt_list:", len(qa_gt_list))

    # Check if results_by_type.json exists and load it if it does
    if os.path.exists("results_by_type.json"):
        with open("results_by_type.json", "r") as json_file:
            loaded_data = json.load(json_file)
            results_by_type = {
                key: [QAResult.model_validate(item) for item in value]
                for key, value in loaded_data.items()
            }
    else:
        results_by_type: dict[str, list[QAResult]] = {}

    # Helper function to check if a qa_gt exists in all descriptions in results_by_type
    def qa_gt_exists_in_all_results(qa_gt: QAGroundTruth) -> bool:
        # Iterate through all descriptions in results_by_type
        found = False
        for description, result_list in results_by_type.items():
            # Check if qa_gt exists in this description's results
            found_in_description = any(
                result.qa_gt.query == qa_gt.query and 
                result.qa_gt.snippets[0].file_path == qa_gt.snippets[0].file_path
                for result in result_list
            )
            # If not found in this description, return False
            if not found_in_description:
                return False
            else:
                found = True
        # If found in all descriptions, return True
        return found

    # Calculate total queries already processed
    total_queries_to_process = len(qa_gt_list)
    queries_already_processed = 0
    if results_by_type:
        first_description = next(iter(results_by_type.keys()))
        queries_already_processed = len(results_by_type[first_description])
    
    # Create a global progress bar for total queries
    progress_bar = tqdm(
        total=total_queries_to_process,
        initial=queries_already_processed,
        desc="Processing queries",
        unit="query"
    )
    
    # Process each document without tqdm
    for document in corpus:
        # Filter qa_gt_list to only include those for this document
        grouped_qa_gt_list = [
            qa_gt for qa_gt in qa_gt_list
            if qa_gt.snippets[0].file_path == document.file_path
        ]

        # Filter out qa_gt items that already exist in results_by_type
        grouped_qa_gt_list = [
            qa_gt for qa_gt in grouped_qa_gt_list
            if not qa_gt_exists_in_all_results(qa_gt)
        ]

        # If no qa_gt remains, skip to the next document
        if not grouped_qa_gt_list:
            print(f"Skipping {document.file_path} as all queries are already processed.")
            continue

        # Print all queries in the grouped_qa_gt_list
        print(f"\nQueries to process for {document.file_path}:")
        for i, qa_gt in enumerate(grouped_qa_gt_list, 1):
            print(f"  {i}. {qa_gt.query}")
        print(f"Total: {len(grouped_qa_gt_list)} queries\n")

        print(f"Processing {len(grouped_qa_gt_list)} queries for {document.file_path}")
        await retrieval_method.ingest_document(document)
        
        # Process each query for this document (without tqdm since we have a global progress bar)
        for qa_gt in grouped_qa_gt_list:

            query_responses = await retrieval_method.query(qa_gt.query)
            
            # Process multiple responses from PAKTON
            for response_item in query_responses:
                description = response_item.get("description", "unknown")
                query_response = response_item.get("query_response")
                
                if description not in results_by_type:
                    results_by_type[description] = []
                
                # Check if the QAResult already exists in results_by_type[description]
                existing_result_index = next((i for i, result in enumerate(results_by_type[description]) if result.qa_gt.query == qa_gt.query and result.qa_gt.snippets[0].file_path == qa_gt.snippets[0].file_path), None)

                new_result = QAResult(
                    qa_gt=qa_gt, retrieved_snippets=query_response.retrieved_snippets
                )

                if existing_result_index is not None:
                    # Override the first existing result
                    results_by_type[description][existing_result_index] = new_result
                    
                    # Remove any other duplicates that might exist
                    results_by_type[description] = [
                        result for i, result in enumerate(results_by_type[description]) 
                        if i == existing_result_index or 
                        not (result.qa_gt.query == qa_gt.query and 
                             result.qa_gt.snippets[0].file_path == qa_gt.snippets[0].file_path)
                    ]
                else:
                    # Append the new result if no match was found
                    results_by_type[description].append(new_result)
            
            # Save results_by_type to JSON after processing each document
            with open("results_by_type.json", "w") as json_file:
                json.dump({key: [result.dict() for result in value] for key, value in results_by_type.items()}, json_file, indent=4)
            # Update the global progress bar after each query is processed
            progress_bar.update(1)

    # Close the progress bar when done
    progress_bar.close()
    await retrieval_method.cleanup()

    # Create benchmark results for each response type
    benchmark_results: dict[str, BenchmarkResult] = {}
    
    for response_type, result_list in results_by_type.items():
        # Always create weights that match the length of the result list for this response type
        response_weights = [1.0] * len(result_list)
        
        # If weights were provided and happen to match the length of this response type's results,
        # use them instead
        if weights is not None and len(weights) == len(result_list):
            response_weights = weights
        
        benchmark_results[response_type] = BenchmarkResult(
            qa_result_list=result_list,
            weights=response_weights,
        )
    
    return benchmark_results
