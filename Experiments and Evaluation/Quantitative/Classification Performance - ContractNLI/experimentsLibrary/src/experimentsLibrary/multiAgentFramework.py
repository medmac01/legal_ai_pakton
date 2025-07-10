"""
Description:
Multi-agent framework (PAKTON) integration module.
Provides functions for task polling, document processing through a FastAPI service.
Supports asynchronous task execution, status monitoring, and result aggregation with comprehensive error handling.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date  : 2025/07/08
"""

from src.experimentsLibrary.logging_config import get_logger
import time 

from src.experimentsLibrary.exceptions import InvalidOutputException

from docx import Document
import tempfile

# Get a logger for this module
logging = get_logger(__name__)

import re
import requests
import time

# Define the base URL of your FastAPI service
BASE_URL = "http://localhost:5001"  # Change if running on a different port

# Terminal statuses for Celery tasks
TERMINAL_STATUSES = {"SUCCESS", "FAILURE", "REVOKED", "IGNORED"}

def poll_task_status(task_id, initial_interval=20, max_retries=50, backoff_factor=1):
    """
    Polls the task status until it reaches a terminal state, using exponential backoff.

    Args:
        task_id (str): The ID of the Celery task.
        initial_interval (int): Initial time in seconds to wait before the first retry.
        max_retries (int): Maximum number of status checks before giving up.
        backoff_factor (int or float): Factor by which the interval is multiplied each retry.

    Returns:
        dict: The final response from the task status check or an error message.
    """
    current_interval = initial_interval
    url = f"{BASE_URL}/task_status/{task_id}"
    print(f"################### POLLING FOR TASK: {task_id} #####################")

    for attempt in range(max_retries):
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Endpoint returned error while checking task status: {response.text}")
            return None

        data = response.json()
        status = data.get("data", {}).get("task_status")

        print(f"Attempt {attempt + 1}/{max_retries}: Task {task_id} status -> {status}")

        # Check if the task has reached a terminal state
        if status in TERMINAL_STATUSES:
            print(f"Final Task Status: {status}, Endpoint's data: {data}")
            return data
        
        # If not in terminal state, wait and then retry
        time.sleep(current_interval)
        # Multiply the interval by the backoff factor to get exponential growth
        current_interval *= backoff_factor

    # If we exit the loop, we've exhausted max_retries
    print(f"Task {task_id} polling exceeded max retries.")
    return {"error": "Task polling timed out"}

def interrogation(userQuery, userContext, userInstructions):
    """
    Call the /interrogation/ endpoint
    
    Returns:
        - task_id (str): The ID of the Celery task.
    """
    print("################# Request to /interrogation/ endpoint ####################")
    url = f"{BASE_URL}/interrogation/"
    payload = {"userQuery": userQuery, "userContext": userContext, "userInstructions": userInstructions}
    response = requests.post(url, json=payload)
    print(f"Endpoint's Response: {response.json()}")
    return response.json().get("data", {}).get("task_id")

from tenacity import (retry, stop_after_attempt, wait_exponential, retry_if_exception_type)

@retry(
    stop=stop_after_attempt(5), 
    wait=wait_exponential(multiplier=10, min=1, max=600),
    retry=retry_if_exception_type((InvalidOutputException, Exception)), 
)
def multiAgentApiCall(model, system_prompt, user_prompt, response_checker=None): 
    # query passed as system_prompt 
    # contract passed as user_prompt
    try:
        # if user_prompt is empty, then only interrogation is done
        if user_prompt != "":
            logging.info("Starting indexing...")
            # create docx from user_prompt and pass it to index_document

            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp_file:
                file_path = tmp_file.name
                tmp_file.write(user_prompt)

            # with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
            #     docx_path = tmp_file.name

            # logging.info(f"Docx file created at: {docx_path}")
            # doc = Document()
            # doc.add_paragraph(user_prompt)
            # doc.save(docx_path)


            # import shutil
            # debug_copy_path = os.path.join(os.getcwd(), "debug_docx.docx")
            # shutil.copy(docx_path, debug_copy_path)
            # logging.info(f"Copied docx file to: {debug_copy_path}")
            task_id = index_document(file_path)
            logging.info("Request for indexing sent to Multi Agent Framework successfully.")
            response = poll_task_status(task_id)

            task_status = response.get("data", {}).get("task_status")
            task_response = response.get("data", {}).get("task_response")
            if task_status != "SUCCESS" or task_response.get("status") != "SUCCESS":  
                raise Exception(f"Not successful task status: {task_status}")

        userQuery = system_prompt.get("userQuery", "No user query found")
        userContext = system_prompt.get("userContext", "No user context found")
        userInstructions = system_prompt.get("userInstructions", "No user instructions found")
        task_id = interrogation(userQuery=userQuery, userContext=userContext, userInstructions=userInstructions)
        logging.info("Request for interrogation sent to Multi Agent Framework successfully.")
        response = poll_task_status(task_id)
        task_status = response.get("data", {}).get("task_status")
        task_response = response.get("data", {}).get("task_response")
        
        if task_status != "SUCCESS" or task_response.get("status") != "SUCCESS":  
            raise Exception(f"Not successful task status: {task_status}")

        response_text = task_response.get("data", {}).get("conclusion", "No conclusion provided")

        # Validate the response if a checker function is provided
        if response_checker:
            temp = response_checker(response_text)
            response_text, is_valid = temp["modifiedResponse"], temp["isValid"]
            if not is_valid:
                raise InvalidOutputException(f"Invalid response: {response_text}")
            
        response_text = f"{response_text} <reasoning>{task_response.get('data', {}).get('report', 'No report provided')}</reasoning>"
        return response_text, (0, 0)
    
    except InvalidOutputException as e:
        logging.error(f"Invalid Response: {e}")
        raise  
    except Exception as e:
        logging.error(f"An error occurred while sending the request to Mutli Agent Framework: {e}")
        raise
    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

MIME_TYPES = {
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.pdf': 'application/pdf'
}

import os
import json

def index_document(file_path: str):
    """
    Call the /index/document/ endpoint
    
    Args:
        file_path (str): Path to the file to be indexed
    
    Returns:
        str: The ID of the Celery task
    """
    print("################# Request to /index/document/ endpoint ####################")
    url = f"{BASE_URL}/index/document/"
    
    # Get file extension and corresponding MIME type
    file_extension = os.path.splitext(file_path)[1].lower()
    mime_type = MIME_TYPES.get(file_extension, 'application/octet-stream')
    
    metadata = {"title": "Test Document","author": "Test Author"}

    # Open and send the file
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, mime_type)}
        data = {"metadata": json.dumps(metadata)}
        response = requests.post(url, files=files, data=data)

    print(f"Endpoint's Response: {response.json()}")
    return response.json().get("data", {}).get("task_id")