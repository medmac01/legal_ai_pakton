import os

# Set the GPUs to be visible to your script
# os.environ["CUDA_VISIBLE_DEVICES"] = "0,1,2,3"
# The PYTORCH_CUDA_ALLOC_CONF environment variable is used to control PyTorch's CUDA memory allocator's behavior. 
# Setting it to expandable_segments:True can help address memory fragmentation issues and improve memory allocation 
# efficiency when working with large models or complex workloads on GPUs.
# os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# Import the library and datetime module for functionality
import experimentsLibrary  # Import the main library that contains the evaluation and dataset handling functions
from datetime import datetime  # Used for adding timestamps to the result

# List of prompting techniques to iterate through
# These techniques are defined in the experimentsLibrary.huggingfaceDatasets module
# You can see details there about each technique and how they are implemented
prompting_techniques = ["naive zero-shot", "optimized zero-shot", "naive few-shot", "naive few-shot isolated spans", "naive_few_shot_isolated_spans_same_hypothesis", "naive_few_shot_isolated_spans_same_hypothesis_chainOfThought", "naive_zero_shot_in_document_rag_naive_chunking", "naive_zero_shot_multi_agent_framework", "naive_few_shot_isolated_spans_same_hypothesis_multi_agent_framework", "naive_zero_shot_lightRAG", "naive_zero_shot_multi_agent_framework_with_predictions", "naive_zero_shot_lightRAG_with_predictions", "naive_zero_shot_with_hypothesis_summary", "hypothesis_composable_graph_rag"]

# Define the subset name for the evaluation
# contractnli_a is the subset with the isolated spans of the contract (not the whole premise)
# contractnli_b is the subset with the original ContractNLI dataset (the whole contracts)
subset_name = "contractnli_b"

# Define the results file where evaluation results will be saved
resultsFile = "resultsGOOGLE.json"

ITERRATIONS = 3  # Number of iterations for the same experiment 

# Define a subset of models to test
# The default models are defined in the experimentsLibrary.models module
# You can see the available models there and their configurations
modelsSubset = [experimentsLibrary.models[0]]

# Loop through each prompting technique
for prompting_technique in prompting_techniques:
    print(f"Starting evaluations with prompting technique: '{prompting_technique}'")

    # Initialize the dataset handler
    # pass the argument prompting_technique in order to indicate the prompting technique
    # see available options at huggingfaceDatasets.py
    dataset_handler = experimentsLibrary.ContractNLIDataset(prompting_technique=prompting_technique, subset_name=subset_name)
    print("Dataset loaded")

    # Get a function to convert string labels to integer labels
    str_to_int_function = dataset_handler.get_str_to_int_function()
    int_to_str_function = dataset_handler.get_int_to_str_function()
    prompt_generator = dataset_handler.get_prompt_generator()

    # Loop through each model in the subset
    for model_idx, model in enumerate(modelsSubset):
        for attempt in range(1, ITERRATIONS+1): 

            try:
                # Print the current model and attempt
                print(f"Testing model '{model['name']}' (Attempt {attempt}/3)")

                # Record the start time for this attempt
                start_time = datetime.now()

                # Run the test and evaluate function on a subset of the test data
                result = experimentsLibrary.testAndEvaluate(
                    dataset_handler.dataset["test"],
                    model,
                    str_to_int_function,
                    int_to_str_function,
                    prompt_generator,
                    response_checker=dataset_handler.responseChecker
                )
                print(f"Test and evaluation completed for model '{model['name']}' (Attempt {attempt})")

                # Save the evaluation results to a file
                experimentsLibrary.save_result_to_file(
                    result,
                    {
                        "start_timestamp": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "end_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "duration_seconds": (datetime.now() - start_time).total_seconds(),
                        "model": model['name'],
                        "API": model['API'],
                        "quantization": model.get('quantization_level', 'no quantization'),
                        "prompting_technique": dataset_handler.prompting_technique,
                        "try": attempt,  # Add the attempt number,
                        "subset_name": subset_name
                    },
                    resultsFile,
                    mode="a"
                )
                print(f"Results saved to file for model '{model['name']}' (Attempt {attempt})")

            except Exception as e:
                # Log the error for the current model and attempt
                print(f"Error occurred while testing model '{model['name']}' with prompting technique '{prompting_technique}' (Attempt {attempt}): {e}")
                # Optionally, you could save the error information to a log file
                with open("error_log.txt", "a") as error_log:
                    error_log.write(
                        f"Error for model '{model['name']}' (API: {model['API']}, Attempt {attempt}, Prompting Technique: {prompting_technique}): {e}\n"
                    )

print("All models and attempts have been tested.")
