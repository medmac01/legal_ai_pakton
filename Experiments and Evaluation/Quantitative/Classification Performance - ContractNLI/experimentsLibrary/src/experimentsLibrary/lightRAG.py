"""
Description:
LightRAG integration module for knowledge graph-based retrieval augmented generation. Provides functions
for document indexing, pipeline status monitoring, and query processing against a LightRAG service. Supports
document upload, hybrid search modes, and comprehensive error handling with retry logic.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date  : 2025/07/08
"""

from src.experimentsLibrary.logging_config import get_logger
import time
import os
import json
import requests
import tempfile
from tenacity import (retry, stop_after_attempt, wait_exponential, retry_if_exception_type)
from src.experimentsLibrary.exceptions import InvalidOutputException

# Get a logger for this module
logging = get_logger(__name__)

# Define the base URL of the LightRAG service
BASE_URL = "http://localhost:9621"

def poll_pipeline_status(max_polling_time=120, polling_interval=2):
    """
    Poll the pipeline status until processing is complete or timeout is reached.
    
    Args:
        max_polling_time (int): Maximum polling time in seconds (default: 120)
        polling_interval (int): Time between status checks in seconds (default: 2)
        
    Returns:
        dict: The final pipeline status or None if timeout is reached
    """
    pipeline_status_url = f"{BASE_URL}/documents/pipeline_status"
    start_time = time.time()
    
    logging.info("Polling pipeline status...")
    
    while time.time() - start_time < max_polling_time:
        try:
            # Get the current pipeline status
            status_response = requests.get(pipeline_status_url)
            status_response.raise_for_status()
            status_data = status_response.json()
            
            # Check if pipeline is busy
            if status_data.get('busy', False):
                logging.info(f"Pipeline busy: {status_data.get('job_name', 'Unknown job')} - {status_data.get('latest_message', '')}")
                logging.info(f"Progress: Batch {status_data.get('cur_batch', 0)}/{status_data.get('batchs', 0)}")
            else:
                logging.info("Pipeline processing completed!")
                return status_data
                
            # Wait before checking again
            time.sleep(polling_interval)
        except requests.exceptions.RequestException as e:
            logging.error(f"Error polling pipeline status: {e}")
            return None
    
    logging.warning(f"Max polling time ({max_polling_time} seconds) exceeded.")
    return None

def query_lightrag(query, mode="local", top_k=10, response_type="Single Paragraph", max_token=4000):
    """
    Send a query to the LightRAG server.
    
    Args:
        query (str): The query text
        mode (str): Retrieval mode - "local", "global", or "mix" (default: "local")
        top_k (int): Number of documents to retrieve (default: 10)
        response_type (str): Format of the response - "Single Paragraph" or "Multiple Paragraphs"
        max_token (int): Maximum tokens for context (default: 4000)
        
    Returns:
        dict: The response from the LightRAG server
    """
    api_url = f"{BASE_URL}/query"
    
    payload = {
        "query": query,
        "mode": mode,
        "only_need_context": False,
        "only_need_prompt": False,
        "response_type": response_type,
        "top_k": top_k,
        "max_token_for_text_unit": max_token,
        "max_token_for_global_context": max_token,
        "max_token_for_local_context": max_token,
        "history_turns": 0
    }
    
    try:
        logging.info(f"Sending query to LightRAG: {query[:100]}...")
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error querying LightRAG: {e}")
        raise

def upload_document(file_path):
    """
    Upload a document to the LightRAG server.
    
    Args:
        file_path (str): Path to the document file
        
    Returns:
        dict: The response from the upload endpoint
    """
    upload_url = f"{BASE_URL}/documents/upload"
    
    # Prepare the file for upload
    with open(file_path, "rb") as file_content:
        files = {"file": (os.path.basename(file_path), file_content, "text/plain")}
        
        try:
            logging.info(f"Uploading document: {os.path.basename(file_path)}")
            upload_response = requests.post(upload_url, files=files)
            upload_response.raise_for_status()
            
            try:
                return upload_response.json()
            except json.JSONDecodeError:
                return {"text": upload_response.text}
        except requests.exceptions.RequestException as e:
            logging.error(f"Error uploading document: {e}")
            raise

def delete_documents(document_ids=None):
    """
    Delete documents from the LightRAG server.
    
    Args:
        document_ids (list, optional): List of document IDs to delete. 
                                       If None, attempts to delete all documents.
                                       
    Returns:
        dict: The response from the delete endpoint
    """
    delete_docs_url = f"{BASE_URL}/documents"
    
    payload = {}
    if document_ids:
        payload["document_ids"] = document_ids
    
    try:
        logging.info(f"Deleting documents: {document_ids if document_ids else 'ALL'}")
        delete_response = requests.delete(delete_docs_url, json=payload if document_ids else None)
        delete_response.raise_for_status()
        
        try:
            return delete_response.json()
        except json.JSONDecodeError:
            return {"text": delete_response.text}
    except requests.exceptions.RequestException as e:
        logging.error(f"Error deleting documents: {e}")
        raise

def get_documents_status():
    """
    Get the status of all documents in the LightRAG server.
    
    Returns:
        dict: The response with document statuses
    """
    docs_url = f"{BASE_URL}/documents"
    
    try:
        logging.info("Fetching document statuses")
        docs_response = requests.get(docs_url)
        docs_response.raise_for_status()
        return docs_response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching document statuses: {e}")
        raise

@retry(
    stop=stop_after_attempt(5), 
    wait=wait_exponential(multiplier=10, min=1, max=600),
    retry=retry_if_exception_type((InvalidOutputException, Exception)),
)
def lightrag_api_call(model, system_prompt, user_prompt, response_checker=None):
    """
    Main function to interact with the LightRAG API.
    
    Args:
        model: Not used by LightRAG, included for compatibility with multiAgentApiCall
        system_prompt (dict): Contains userQuery, userContext, and userInstructions
        user_prompt (str): Document text to index before querying
        response_checker (callable, optional): Function to validate and potentially modify the response
        
    Returns:
        tuple: (response_text, (0, 0)) - Same format as multiAgentApiCall for compatibility
    """
    try:
        # Initialize file_path for the finally clause
        file_path = None
        
        # If user_prompt is not empty, delete all documents then index the new document
        if user_prompt != "":
            logging.info("Starting indexing...")
            
            # First, delete all existing documents
            logging.info("Deleting all existing documents before indexing...")
            delete_result = delete_documents()
            time.sleep(2)  # Wait for a moment to ensure deletion is processed
            logging.info(f"Delete result: {delete_result}")
            
            # Create a temporary file with the document text
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp_file:
                file_path = tmp_file.name
                tmp_file.write(user_prompt)
            
            # Upload the document
            upload_response = upload_document(file_path)
            logging.info("Document uploaded successfully")
            time.sleep(2)
            
            # Poll until processing is complete
            pipeline_status = poll_pipeline_status()
            if not pipeline_status:
                raise Exception("Document processing timed out or failed")
                
            # Check the document status
            docs_status = get_documents_status()
            logging.info(f"Document processing completed with status: {docs_status}")
        
        # Send the query
        response = query_lightrag(system_prompt, mode="mix", response_type="Single Paragraph")
        
        # Extract the response text
        response_text = response.get('response', 'No response found')
        logging.info(f"Response from LightRAG: {response_text}")
        reasoning = response_text
        # Validate the response if a checker function is provided
        if response_checker:
            temp = response_checker(response_text)
            response_text, is_valid = temp["modifiedResponse"], temp["isValid"]
            if not is_valid:
                raise InvalidOutputException(f"Invalid response: {response_text}")
        
        logging.info(f"Response returned from light rag api call: {response_text}")
        response_text = f"{response_text} <reasoning>{reasoning}</reasoning>"
        return response_text, (0, 0)
    
    except InvalidOutputException as e:
        logging.error(f"Invalid Response: {e}")
        raise
    except Exception as e:
        logging.error(f"An error occurred while interacting with LightRAG: {e}")
        raise
    finally:
        # Clean up temporary files
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

# Create an alias for the lightrag_api_call function to match the name imported in models.py
lightRAGCall = lightrag_api_call