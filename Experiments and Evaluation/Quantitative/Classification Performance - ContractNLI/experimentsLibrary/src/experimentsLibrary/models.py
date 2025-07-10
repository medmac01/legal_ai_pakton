"""
Description:
Model configuration and API caller mapping module. Contains comprehensive model definitions for various language
models across different APIs (Bedrock, OpenAI, Google, Anthropic, Local, WatsonX) with their specific parameters,
prompt formats, and response extractors. Provides centralized model management and API routing functionality.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date  : 2025/07/08
"""

####################### MODELS #######################

# The `models` list contains configurations for different language models.
# Each model is represented as a dictionary with specific fields that define
# how to interact with the model's API.

# Fields:
# "name": A user-friendly name for the model for easy identification.
# "id": The unique identifier for the model
# - search for it in bedrock docs (when calling the bedrockAPI).
# - search for it in openai docs (when calling the openaiAPI).
# - search for it in huggingface docs (when calling the localAPI).
# "quantization_level": The level of the quantization applied. "no quantization", "normal", "aggressive"
# "prompt_format": A template for structuring input prompts to the model.
# - Use placeholders {SYSTEM_PROMPT} and {USER_PROMPT}, which are replaced
#   with actual instructions at runtime.
# - Ensure this format aligns with the model's expected input structure.
# "response_extractor": A lambda function that defines how to extract the
# model's generated output from the API response. The exact structure of
# the response depends on the model and must be handled accordingly.
# "args": Additional arguments passed to the bedrockAPI call
# "API": write "BEDROCK" for using bedrock api and "OPENAI" for using openAI openai api
# for local execution write 'LOCAL' to the 'API', 
models = [
    {"name": "Llama-3.1-8b", "id": "meta.llama3-1-8b-instruct-v1:0", "prompt_format":
     """
    <|begin_of_text|><|start_header_id|>system<|end_header_id|>

    {SYSTEM_PROMPT}<|eot_id|><|start_header_id|>user<|end_header_id|>

    {USER_PROMPT}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """,
    "response_extractor": lambda model_response: model_response["generation"],
    "args": {"max_gen_len": 700, "temperature": 0.5, "top_p": 1.0, },
    "API": "BEDROCK"},
    {"name": "Mistral-Instruct-7b", "id": "mistral.mistral-7b-instruct-v0:2", "prompt_format":
     """ <s>[INST] {SYSTEM_PROMPT}\n{USER_PROMPT} [/INST] """,
     "response_extractor": lambda model_response: model_response["outputs"][0]["text"],
     "args": {"max_tokens": 700, "temperature": 0.5, "top_p": 1.0, },
     "API": "BEDROCK"},
    {"name": "Mixtral-Instruct-8x7B", "id": "mistral.mixtral-8x7b-instruct-v0:1", "prompt_format":
     """ <s>[INST] {SYSTEM_PROMPT}\n{USER_PROMPT} [/INST] """,
     "response_extractor": lambda model_response: model_response["outputs"][0]["text"],
     "args": {"max_tokens": 700, "temperature": 0.5, "top_p": 1.0, },
     "API": "BEDROCK"},
     {"name": "Llama-3.1-70b", "id": "meta.llama3-1-70b-instruct-v1:0", "prompt_format":
     """
    <|begin_of_text|><|start_header_id|>system<|end_header_id|>

    {SYSTEM_PROMPT}<|eot_id|><|start_header_id|>user<|end_header_id|>

    {USER_PROMPT}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """,
    "response_extractor": lambda model_response: model_response["generation"],
    "args": {"max_gen_len": 700, "temperature": 0.5, "top_p": 1.0, },
    "API": "BEDROCK"},
    {"name": "ChatGPT-4o", "id": "gpt-4o", "args": None, "API": "OPENAI"},
    {"name": "Meta-Llama-3-8B-LOCAL", 
    "id": "meta-llama/Meta-Llama-3-8B-Instruct", 
    "quantization_level": "no quantization",
    "prompt_format": ["system", "user", "eos_token_needed"], # if the model (eg mistral) doesnt have system prompt dont include it
    "args": {
        "max_new_tokens": 700,
        "temperature": 0.3,
        "top_p": 1.0
        # "repetition_penalty": 1.15
    },
    "API": "LOCAL"},
    {"name": "Mistral-7B-Instruct-LOCAL", 
    "id": "mistralai/Mistral-7B-Instruct-v0.2", 
    "quantization_level": "no quantization",
    "prompt_format": ["user"], 
    "args": {
        "max_new_tokens": 700,
        "temperature": 0.3,
        "top_p": 1.0
    },
    "API": "LOCAL"},
    {"name": "Meta-Llama-3-70B-Instruct-LOCAL", 
    "id": "meta-llama/Meta-Llama-3-70B-Instruct", 
    "quantization_level": "no quantization",
    "prompt_format": ["system", "user", "eos_token_needed"], 
    "args": {
        "max_new_tokens": 700,
        "temperature": 0.3,
        "top_p": 1.0
    },
    "API": "LOCAL"},
    {"name": "Mixtral-8x7B-LOCAL", 
    "id": "mistralai/Mixtral-8x7B-v0.1", 
    "quantization_level": "normal",
    "prompt_format": ["user"], 
    "args": {
        "max_new_tokens": 700,
        "temperature": 0.3,
        "top_p": 1.0
    },
    "API": "LOCAL"},  
    {"name": "Mixtral-8x7B-Instruct-LOCAL", 
    "id": "mistralai/Mixtral-8x7B-Instruct-v0.1", 
    "quantization_level": "normal",
    "prompt_format": ["user"], 
    "args": {
        "max_new_tokens": 700,
        "temperature": 0.2,
        "top_p": 1.0
    },
    "API": "LOCAL"}, 
    {"name": "Equall/Saul-7B-Instruct-LOCAL", 
    "id": "Equall/Saul-7B-Instruct-v1", 
    "quantization_level": "no quantization",
    "prompt_format": ["user"], 
    "args": {
        "max_new_tokens": 700,
        "temperature": 0.3,
        "top_p": 1.0
    },
    "API": "LOCAL"},  
    {"name": "SaulLM-54B-Instruct-LOCAL", 
    "id": "Equall/SaulLM-54B-Instruct", 
    "quantization_level": "lowest",
    "prompt_format": ["user"], 
    "args": {
        "max_new_tokens": 700,
        "temperature": 0.3,
        "top_p": 1.0
    },
    "API": "LOCAL"},  
    {"name": "SaulLM-141B-Instruct-LOCAL", 
    "id": "Equall/SaulLM-141B-Instruct", 
    "quantization_level": "no quantization",
    "prompt_format": ["user"], 
    "args": {
        "max_new_tokens": 700,
        "temperature": 0.3,
        "top_p": 1.0
    },
    "API": "LOCAL"},  
    {
        "name": "DeepSeek-R1-Distill-Llama-70B-LOCAL",
        "id": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
        "quantization_level": "normal",
        "prompt_format": ["system", "user", "eos_token_needed"],
        "args": {"max_new_tokens": 700, "temperature": 0.3, "top_p": 1.0},
        "API": "LOCAL",
    },
    {
        "name": "Claude 3 Opus",
        "id": "anthropic.claude-3-opus-20240229-v1:0",
        "messages_format": lambda user_prompt: [
            {"role": "user", "content": user_prompt}
        ],
        "response_extractor": lambda model_response: ''.join(
            block['text'] for block in model_response.get('content', []) if block.get('type') == 'text'
        ),
        "args": {"max_tokens": 700, "temperature": 0.5, "top_p": 1.0},
        "API": "BEDROCK"
    },
    {
        "name": "Claude 3.5 Sonnet v2",
        "id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "messages_format": lambda user_prompt: [
            {"role": "user", "content": user_prompt}
        ],
        "response_extractor": lambda model_response: ''.join(
            block['text'] for block in model_response.get('content', []) if block.get('type') == 'text'
        ),
        "args": {"max_tokens": 700, "temperature": 0.5, "top_p": 1.0},
        "API": "BEDROCK"
    },
    {
        "name": "Multi Agent Framework version 1",
        "id": "Multi Agent Framework version 1",
        "API": "MUTLI_AGENT_FRAMEWORK"
    },
    {
        "name": "WatsonX Llama-3-3-70B",
        "id": "meta-llama/llama-3-3-70b-instruct",
        "project_id": "8e60491c-6efe-40a5-8544-0f06a13e9405",  # This is from the notebook example
        "args": {"max_tokens": 700, "temperature": 0.5, "top_p": 1.0},
        "API": "WATSONX"
    },
    {
        "name": "LightRAG",
        "id": "LightRAG",
        "API": "LIGHT_RAG"
    },
    {"name": "DeepSeek-V3", "id": "deepseek-chat", "args": {"temperature": 0.3}, "API": "OPENAI"}, # 0.3 temperature seems to be too low for deepseek
    {"name": "DeepSeek-R1", "id": "deepseek-reasoner", "args": {"temperature": 1.3}, "API": "OPENAI"},
    {
        "name": "Claude 3.7 Sonnet",
        "id": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        "messages_format": lambda user_prompt: [
            {"role": "user", "content": user_prompt}
        ],
        "response_extractor": lambda model_response: ''.join(
            block['text'] for block in model_response.get('content', []) if block.get('type') == 'text'
        ),
        "args": {"max_tokens": 700, "temperature": 0.5, "top_p": 1.0},
        "API": "BEDROCK"
    },
    {"name": "Claude 3.7", "id": "claude-3-7-sonnet-20250219", "args": {"max_tokens": 20000, "temperature": 0.0}, "API": "ANTHROPIC"},
    {"name": "Llama-3.3-70b", "id": "us.meta.llama3-3-70b-instruct-v1:0", "prompt_format":
     """
    <|begin_of_text|><|start_header_id|>system<|end_header_id|>

    {SYSTEM_PROMPT}<|eot_id|><|start_header_id|>user<|end_header_id|>

    {USER_PROMPT}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """,
    "response_extractor": lambda model_response: model_response["generation"],
    "args": {"max_gen_len": 700, "temperature": 0.5, "top_p": 1.0, },
    "API": "BEDROCK"},
    {"name": "Qwen 2.5 72B Instruct", "id": "qwen2.5-72b-instruct", "args": {"temperature": 0.3}, "API": "OPENAI"}, 
    {"name": "Gemma 3 27B", "id": "gemma-3-27b-it", "args": {"temperature": 0.3}, "API": "GOOGLE"},
]

##############################################################

################## API CALL FUNCTIONS ########################

from src.experimentsLibrary.bedrock import bedrockApiCall
from src.experimentsLibrary.openai import openaiApiCall
from src.experimentsLibrary.local import localApiCall
from src.experimentsLibrary.multiAgentFramework import multiAgentApiCall
from src.experimentsLibrary.anthropic import anthropicApiCall
from src.experimentsLibrary.google import googleApiCall
from src.experimentsLibrary.lightRAG import lightRAGCall
from src.experimentsLibrary.watsonx import watsonxApiCall

# Define a mapping of API names to their respective functions
api_callers = {
    'BEDROCK': bedrockApiCall,
    'OPENAI': openaiApiCall,
    'LOCAL': localApiCall,
    'MUTLI_AGENT_FRAMEWORK': multiAgentApiCall,
    'LIGHT_RAG': lightRAGCall,
    'WATSONX': watsonxApiCall,
    'ANTHROPIC': anthropicApiCall,
    'GOOGLE': googleApiCall,
}