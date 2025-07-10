import asyncio
import json
import os
import requests
import time
from typing import cast, Dict, Tuple
import re
import functools  # For lru_cache decorator

from legalbenchrag.benchmark_types import Document, QueryResponse, RetrievalMethod, RetrievedSnippet

BASE_URL = "http://localhost:5001"  # Change to match your API server
TERMINAL_STATUSES = {"SUCCESS", "FAILURE", "REVOKED", "IGNORED"}

@functools.lru_cache(maxsize=1024)  # Cache up to 1024 recent results
def find_unique_substring_position(original_text, chunk):
    """
    Finds the longest unique substring of `chunk` in `original_text` and returns
    its adjusted position in `original_text`. Falls back to full chunk search if needed.
    Uses lru_cache decorator for automatic caching of results.
    """
    n = len(chunk)

    # Start from longest substrings
    for length in range(n, 0, -1):
        for start in range(n - length + 1):
            substring = chunk[start:start + length]

            first_index = original_text.find(substring)
            if first_index == -1:
                continue

            last_index = original_text.rfind(substring)
            if first_index == last_index:  # Appears only once
                return first_index - start

    # Fallback: check if full chunk exists
    idx = original_text.find(chunk)
    return idx if idx != -1 else -1

class PAKTON(RetrievalMethod):
    def __init__(self):
        self.documents = {}
        # Create temporary directory for document uploads if needed
        os.makedirs("./tmp", exist_ok=True)
        # Keep track of the last document ingested to avoid duplicates
        self.last_ingested_document = None
        # Clear the function cache when creating a new instance
        find_unique_substring_position.cache_clear()
        
    async def ingest_document(self, document: Document, max_retries=3) -> None:
        """Index a document into your API system with retry mechanism."""
        self.documents[document.file_path] = document
        print(f"Indexing document: {document.file_path}")
        # Skip indexing if this is the same document as the last one
        if self.last_ingested_document == document.file_path:
            print(f"Skipping duplicate document: {document.file_path}")
            return
            
        # Create a temp file to upload
        tmp_path = f"./tmp/{os.path.basename(document.file_path)}"
        with open(tmp_path, "w") as f:
            f.write(document.content)
        
        # Upload the file with retry mechanism
        metadata = {"title": os.path.basename(document.file_path)}
        task_id = None
        
        for retry_attempt in range(max_retries):
            try:
                print(f"Uploading document: {document.file_path} (attempt {retry_attempt + 1}/{max_retries})")
                with open(tmp_path, "rb") as f:
                    files = {"file": (os.path.basename(tmp_path), f, "text/plain")}
                    data = {"metadata": json.dumps(metadata)}
                    response = requests.post(
                        f"{BASE_URL}/index/document/", 
                        files=files, 
                        data=data, 
                        timeout=30  # 30-second timeout for the request
                    )
                
                if response.status_code != 200 and response.status_code != 202:
                    print(f"Document upload API returned status code {response.status_code}, retrying...")
                    await asyncio.sleep(2 ** retry_attempt)  # Exponential backoff
                    continue
                    
                task_id = response.json().get("data", {}).get("task_id")
                if not task_id:
                    print(f"No task_id received from document upload API, retrying...")
                    await asyncio.sleep(2 ** retry_attempt)
                    continue
                
                # Poll for task status with the obtained task_id
                result = await self._poll_task_status(task_id)
                
                # Check if polling was successful
                if result.get("error"):
                    print(f"Document indexing task polling failed: {result.get('error')}, retrying upload...")
                    await asyncio.sleep(2 ** retry_attempt)  # Exponential backoff
                    continue
                
                # If we got here, both upload and polling were successful
                break
                
            except (requests.exceptions.RequestException, json.JSONDecodeError, KeyError) as e:
                print(f"Error during document upload (attempt {retry_attempt + 1}/{max_retries}): {str(e)}")
                if retry_attempt < max_retries - 1:
                    wait_time = 2 ** retry_attempt
                    print(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"Max retries reached for document upload: {document.file_path}")
        
        # Clean up temp file
        os.remove(tmp_path)
        
        # Update the last ingested document
        self.last_ingested_document = document.file_path
        print(f"Document indexed: {document.file_path}")

    async def sync_all_documents(self) -> None:
        """Nothing to do here since documents are uploaded one by one."""
        pass

    async def query(self, query: str, max_retries=3):
        """Run a query through your API with retry capability."""
        parts = query.split(";")
        payload = {
            "query": parts[1].strip(), 
            "instructions": parts[0].strip() + "; **USE DOCUMENT SEARCH TOOL ALWAYS DESPITE THE QUERY BEING A GENERAL DEFINITION REQUEST**",
            "agent_config": {"enable_hybrid": True},
            "search_config": {"return_chunks": True}
        }
        
        # The retry mechanism only wraps the API request and polling process
        result = None
        for retry_attempt in range(max_retries):
            try:
                print(f"Querying: {query} (attempt {retry_attempt + 1}/{max_retries})")
                response = requests.post(f"{BASE_URL}/research/", json=payload, timeout=30)
                
                if response.status_code != 200 and response.status_code != 202:
                    print(f"Research API returned status code {response.status_code}, retrying...")
                    await asyncio.sleep(2 ** retry_attempt)  # Exponential backoff
                    continue
                    
                task_id = response.json().get("data", {}).get("task_id")
                if not task_id:
                    print(f"No task_id received from research API, retrying...")
                    await asyncio.sleep(2 ** retry_attempt)
                    continue
                
                # Poll for task status
                result = await self._poll_task_status(task_id)
                
                # Check if polling was successful or if it timed out/failed
                if result.get("error"):
                    print(f"Task polling failed: {result.get('error')}, retrying research request...")
                    await asyncio.sleep(2 ** retry_attempt)
                    continue
                
                # If we got here, we successfully received a result
                break
                
            except (requests.exceptions.RequestException, json.JSONDecodeError, KeyError) as e:
                print(f"Error during research request (attempt {retry_attempt + 1}/{max_retries}): {str(e)}")
                if retry_attempt < max_retries - 1:
                    wait_time = 2 ** retry_attempt
                    print(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"Max retries reached for query: {query}")
        
        # If we exhausted all retries and still don't have a result, return error response
        if result is None or result.get("error"):
            print(f"Failed to get a valid result after {max_retries} attempts")
            return [{"description": "error", "query_response": QueryResponse(retrieved_snippets=[])}]
        
        # Continue with the rest of the function using the obtained result
        # Parse the results into RetrievedSnippets
        response_text = result.get("data", {}).get("task_response", {}).get("data", {}).get("response", "")
        queryResponses = []

        def get_retrieved_snippets(chunks):
            document = self.documents[self.last_ingested_document]
            orig_content = document.content
            retrieved_snippets = []
            for i, chunk_content in enumerate(chunks):
                start_idx = find_unique_substring_position(orig_content, chunk_content)
                print(f"Start index: {start_idx}")
                if start_idx != -1:
                    retrieved_snippets.append(
                        RetrievedSnippet(
                            file_path=self.last_ingested_document,
                            span=(start_idx, start_idx + len(chunk_content)),
                            score=1.0 / (i + 1)  # Simple ranking score - higher for earlier chunks
                        )
                    )
                else:
                    print(f"\n===== ERROR: CHUNK NOT FOUND IN DOCUMENT =====")
                    print(f"Chunk #{i+1} of {len(chunks)}")
                    print(f"Document: {self.last_ingested_document}")
                    print(f"Document length: {len(orig_content)} characters")
                    print(f"Chunk length: {len(chunk_content)} characters")
                    print(f"chunk: {chunk_content}")
                    print(f"Original Text: {orig_content}")
                    print("Possible substrings to search for:")
                    for length in [10, 20, 30, 50]:
                        for start_pos in [0, len(chunk_content)//4, len(chunk_content)//2, len(chunk_content)-length]:
                            if start_pos < len(chunk_content):
                                substring = chunk_content[start_pos:start_pos+length]
                                count = orig_content.count(substring)
                                print(f"  Substring [{start_pos}:{start_pos+length}] (count: {count}): {substring}")
            return retrieved_snippets  # Return the list of retrieved snippets

        # Check if response is in the expected format with "---" delimiters
        if response_text and "---" in response_text:
            chunks_text = response_text.split("---")
            chunks = [chunk.strip() for chunk in chunks_text if chunk.strip() and not chunk.strip().startswith("For the query")]
            queryResponses.append({"description": "llm_filter_top_1", "query_response":QueryResponse(retrieved_snippets=get_retrieved_snippets(chunks[:1]))})
            queryResponses.append({"description": "llm_filter_top_2", "query_response":QueryResponse(retrieved_snippets=get_retrieved_snippets(chunks[:2]))})
            queryResponses.append({"description": "llm_filter_top_4", "query_response":QueryResponse(retrieved_snippets=get_retrieved_snippets(chunks[:4]))})
            queryResponses.append({"description": "llm_filter_top_8", "query_response":QueryResponse(retrieved_snippets=get_retrieved_snippets(chunks[:8]))})
            queryResponses.append({"description": "llm_filter_top_16", "query_response":QueryResponse(retrieved_snippets=get_retrieved_snippets(chunks[:16]))})
            queryResponses.append({"description": "llm_filter_top_32", "query_response":QueryResponse(retrieved_snippets=get_retrieved_snippets(chunks[:32]))})
            queryResponses.append({"description": "llm_filter_top_64", "query_response":QueryResponse(retrieved_snippets=get_retrieved_snippets(chunks[:64]))})
        else:
            # If no "---" delimiters found, return empty snippets
            print(f"No chunk delimiters found in response. Query: {query}")
        
        responseContext = result.get("data", {}).get("task_response", {}).get("data", {}).get("chunks", "")
        
        chunks_content = [chunk.get("page_content") for chunk in responseContext]
        # isolate the original span only and keep unique chunks
        isolated_chunks = []
        for text in chunks_content:
            match = re.search(r"--- ORIGINAL SPAN OF THE DOCUMENT ---\n(.*?)\n------", text, re.DOTALL)
            if match:
                matched_text = match.group(1).strip()
                if matched_text not in isolated_chunks:
                    isolated_chunks.append(matched_text)
        queryResponses.append({"description": "top_1", "query_response":QueryResponse(retrieved_snippets=get_retrieved_snippets(isolated_chunks[:1]))})
        queryResponses.append({"description": "top_2", "query_response":QueryResponse(retrieved_snippets=get_retrieved_snippets(isolated_chunks[:2]))})
        queryResponses.append({"description": "top_4", "query_response":QueryResponse(retrieved_snippets=get_retrieved_snippets(isolated_chunks[:4]))})
        queryResponses.append({"description": "top_8", "query_response":QueryResponse(retrieved_snippets=get_retrieved_snippets(isolated_chunks[:8]))})
        queryResponses.append({"description": "top_16", "query_response":QueryResponse(retrieved_snippets=get_retrieved_snippets(isolated_chunks[:16]))})
        queryResponses.append({"description": "top_32", "query_response":QueryResponse(retrieved_snippets=get_retrieved_snippets(isolated_chunks[:32]))})
        queryResponses.append({"description": "top_64", "query_response":QueryResponse(retrieved_snippets=get_retrieved_snippets(isolated_chunks[:64]))})
        
        return queryResponses

    async def cleanup(self) -> None:
        """Clean up any resources."""
        pass
        
    async def _poll_task_status(self, task_id, max_retries=30):
        """Poll the task status until it reaches a terminal state."""
       
        current_interval = 1
        request_timeout = 10  # Timeout for each request in seconds
        
        for attempt in range(max_retries):
            print(f"Polling task status for task_id: {task_id}, attempt: {attempt}")
            url = f"{BASE_URL}/task_status/{task_id}"
            
            try:
                response = requests.get(url, timeout=request_timeout)
                
                if response.status_code != 200 and response.status_code != 202:
                    print(f"Received non-200, non-202 status code: {response.status_code}")
                    await asyncio.sleep(current_interval)
                    current_interval = min(current_interval * 2, 30)  # Exponential backoff up to 30s
                    continue
                    
                data = response.json()
                status = data.get("data", {}).get("task_status")
                
                if status in TERMINAL_STATUSES:
                    print(f"Task {task_id} reached terminal status: {status}")
                    return data
                
            except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
                print(f"Error during polling of task {task_id}: {str(e)}")
                # Continue with the retry logic even if the request fails
            
            await asyncio.sleep(current_interval)
            current_interval = min(current_interval * 2, 30)  # Exponential backoff up to 30s
            
        print(f"Task {task_id} polling timed out after {max_retries} attempts")
        return {"error": "Task polling timed out"}