"""
Description:
Utility functions for managing composable graphs using LlamaIndex. Provides functionality to load and save vector
indices, create hypothesis-based composable graphs, and query them for document retrieval. Supports organizing
documents by hypothesis and label for structured RAG (Retrieval-Augmented Generation) applications.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date  : 2025/07/08
"""

from llama_index.core import VectorStoreIndex, Document, StorageContext, Settings
from llama_index.core.indices.composability import ComposableGraph
from llama_index.core.storage import StorageContext
from llama_index.core.indices.loading import load_index_from_storage

import os
import json
import logging

# Import or create logger
logger = logging.getLogger(__name__)

def load_saved_indices(storage_dir):
    """
    Load saved indices from disk using the hypothesis mapping system.
    This function is the counterpart to create_indices, loading indices that were previously saved.
    
    Args:
        storage_dir: Path to the directory containing saved indices and hypothesis mapping
        
    Returns:
        A tuple of (indices dictionary, hypothesis mapping dictionary)
    """
    indices = {}
    
    # First, load the hypothesis mapping to know which directories to look for
    mapping_path = os.path.join(storage_dir, "hypothesis_mapping.json")
    hypothesis_map = {}
    
    if not os.path.exists(storage_dir):
        logger.warning(f"Storage directory does not exist: {storage_dir}")
        return {}, {}  # Return empty dictionaries instead of None
        
    if os.path.exists(mapping_path):
        try:
            with open(mapping_path, 'r') as f:
                hypothesis_map = json.load(f)
                
            # Create a reverse mapping for easier lookups
            reverse_map = {v: k for k, v in hypothesis_map.items()}
            
            # Load indices for each hypothesis
            for hypothesis_id, hypothesis_text in reverse_map.items():
                indices[hypothesis_id] = {}
                
                # For each hypothesis, check for label directories
                hypothesis_dir = os.path.join(storage_dir, hypothesis_id)
                if os.path.exists(hypothesis_dir):
                    # Get all label directories
                    labels = [d for d in os.listdir(hypothesis_dir) 
                             if os.path.isdir(os.path.join(hypothesis_dir, d))]
                    
                    for label in labels:
                        index_path = os.path.join(hypothesis_dir, label)
                        
                        if os.path.exists(index_path) and os.path.isdir(index_path):
                            # Load the index for this hypothesis and label
                            try:
                                # Use the imported load_index_from_storage function
                                storage_context = StorageContext.from_defaults(persist_dir=index_path)
                                indices[hypothesis_id][label] = load_index_from_storage(storage_context)
                                logger.info(f"Loaded index for hypothesis {hypothesis_id}, label {label}")
                            except Exception as e:
                                logger.error(f"Error loading index for {hypothesis_id}/{label}: {e}")
                        else:
                            logger.warning(f"Index directory not found: {index_path}")
            
            logger.info(f"Loaded {sum(len(labels) for labels in indices.values())} indices for {len(indices)} hypotheses")
            return indices, hypothesis_map
            
        except Exception as e:
            logger.error(f"Error loading hypothesis mapping: {e}")
            # Continue with directory scanning as fallback
            return {}, {}
    
    # If no mapping file exists, use directory scanning
    logger.warning("No hypothesis mapping found, scanning directories...")
    # Implement directory scanning logic here
    return {}, {}

def filter_none_nodes(nodes):
    """
    Filter out nodes with None or empty text.
    
    Args:
        nodes: List of nodes from query response.
        
    Returns:
        List of nodes with valid text content.
    """
    filtered_nodes = []
    for node in nodes:
        # Check if node has text attribute and it has valid content
        if hasattr(node.node, "text") and node.node.text is not None and node.node.text.strip() != "" and node.node.text.strip() != "None":
            filtered_nodes.append(node)
        else:
            print(f"Filtering out node with missing or empty text")
    
    return filtered_nodes

def create_hypothesis_graphs(indices):
    """
    Create a ComposableGraph for each hypothesis from its label indices.
    
    Args:
        indices: Dictionary of label-specific indices per hypothesis.
        
    Returns:
        Dictionary of ComposableGraphs per hypothesis.
    """
    hypothesis_graphs = {}
    
    for hypothesis, label_indices in indices.items():
        if label_indices:
            # We need to have actual index objects in a list
            children_indices = list(label_indices.values())
            # Create summary descriptions for each label index
            index_summaries = [f"Information about hypothesis: '{hypothesis}' with label: '{label}'" 
                              for label in label_indices.keys()]
            
            # Create a new graph with proper parameters
            hypothesis_graph = ComposableGraph.from_indices(
                VectorStoreIndex,  # Root index class
                children_indices,  # Child indices
                index_summaries,   # Summaries matching children_indices order
                # max_top_k=2,       # Select max 2 indices per query
                # child_branch_factor=3,  # Query at most 3 child nodes
                # select_children=True    # Dynamically select relevant children
            )
            
            hypothesis_graphs[hypothesis] = hypothesis_graph
            print(f"Created ComposableGraph for hypothesis: {hypothesis}")

    return hypothesis_graphs

def query_hypothesis_graph(query, hypothesis_graph):
    try:
        # Create a query engine focused on retrieval rather than generation
        retrieval_engine = hypothesis_graph.as_query_engine(
            similarity_top_k=3,       
            max_top_k=3,                
            child_branch_factor=3,    
            select_children=True,    
            response_mode="no_text", 
            verbose=True            
        )
        
        # Execute the query - this will retrieve documents without generating a response
        retrieval_response = retrieval_engine.query(query)
        
        documents_retrieved = []
        # Look for source nodes - these are the retrieved documents
        if hasattr(retrieval_response, "source_nodes") and retrieval_response.source_nodes:
            # Filter out None nodes
            nodes = filter_none_nodes(retrieval_response.source_nodes)
            
            print(f"Retrieved {len(nodes)} valid documents from the graph (filtered from {len(retrieval_response.source_nodes)} total)")

            # Store the test result
            
            for i, node in enumerate(nodes):
                documents_retrieved.append(node.node.text)
        else:
            # No source nodes found
            print(f"  No documents retrieved.")

        return documents_retrieved
        
    except Exception as e:
        print(f"  Error testing hypothesis graph retrieval: {str(e)}")
        return []