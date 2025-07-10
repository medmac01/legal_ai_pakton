# Import the library and datetime module for functionality
import experimentsLibrary  # Import the main library that contains the evaluation and dataset handling functions
from datetime import datetime  # Used for adding timestamps to the result

# Initialize the dataset handler
# This sets up the ContractNLI dataset and provides utility functions for handling it
# pass the argument prompting_technique in order to indicate the prompting technique
# see available options at huggingfaceDatasets.py
dataset_handler = experimentsLibrary.ContractNLIDataset()
print("Dataset loaded")
# Get a function to convert string labels to integer labels
# This function is generated dynamically based on the dataset's label feature
str_to_int_function = dataset_handler.get_str_to_int_function()
int_to_str_function = dataset_handler.get_int_to_str_function()
prompt_generator = dataset_handler.get_prompt_generator()
# Record the start time of execution
start_time = datetime.now()

# select the model. you can pick either one from models.py
# or define a new one following the format conventions displayed 
# in the models.py
modelUsed = experimentsLibrary.models[0]
print("Model loaded")
# Run the test and evaluate function on a subset of the test data
# - `dataset["test"].select(range(10))`: Selects the first 10 samples from the test split
# - `models[0]`: The first model configuration from the library's models module
# - `str_to_int_function`: Function to convert string predictions to integer labels
# - `response_checker`: Optional checker to validate responses from the model
result = experimentsLibrary.testAndEvaluate(
    dataset_handler.dataset["test"],
    modelUsed,
    str_to_int_function,
    int_to_str_function,
    prompt_generator,
    response_checker=dataset_handler.responseChecker
)
print("Test and evaluation completed")
# Save the evaluation results to a file
# - `result`: The output from the testAndEvaluate function
# - Metadata includes a timestamp and the model name
# - Results are appended to `unitTest_results.json` in append mode
experimentsLibrary.save_result_to_file(
    result,
    {"start_timestamp": start_time.strftime("%Y-%m-%d %H:%M:%S"),
    "end_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
    "duration_seconds": (datetime.now() - start_time).total_seconds(),
    "model": modelUsed['name'],
    "API": modelUsed['API'],
    "quantization": modelUsed['quantization_level']},
    "results.json",
    mode="a"
)
print("Results saved to file")