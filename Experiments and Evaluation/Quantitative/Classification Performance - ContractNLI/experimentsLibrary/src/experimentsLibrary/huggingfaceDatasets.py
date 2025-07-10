"""
Description:
Hugging Face datasets integration module providing abstract dataset interfaces and implementations.
Contains DatasetInterface abstract class and ContractNLIDataset implementation with support for various
prompting techniques, RAG integration, multi-agent frameworks, and comprehensive dataset analysis utilities.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date  : 2025/07/08
"""

#################### HUGGING FACE DATASETS ####################

import os
from collections import Counter
from huggingface_hub import login
from datasets import Dataset, load_dataset, concatenate_datasets
from src.experimentsLibrary.utils import clean
from src.experimentsLibrary.composableGraph_utils import load_saved_indices, create_hypothesis_graphs, query_hypothesis_graph   
import random
import re

from experimentsLibrary.logging_config import get_logger

logger = get_logger(__name__)

import traceback

from src.experimentsLibrary.openai import openaiApiCall

from abc import ABC, abstractmethod

from langchain_core.documents import Document
from experimentsLibrary.utils import format_documents

class DatasetInterface(ABC):
    """
    Abstract base class for datasets, ensuring consistency across dataset implementations.
    """

    @abstractmethod
    def __init__(self):
        """Initialize the dataset."""
        pass

    @abstractmethod
    def describe_dataset(self):
        """Describe the dataset structure, features, and splits."""
        pass

    @abstractmethod
    def analyze_class_distribution(self):
        """Analyze and print class distribution as percentages."""
        pass

    @abstractmethod
    def get_str_to_int_function(self):
        """Return a function for string-to-integer label conversion."""
        pass

    @abstractmethod
    def get_int_to_str_function(self):
        """Return a function for integer-to-string label conversion."""
        pass

    @staticmethod
    @abstractmethod
    def responseChecker(response):
        """
        Check the validity of a response based on dataset-specific rules.

        Args:
            response (str): The response string to check.

        Returns:
            dict: A dictionary with keys 'modifiedResponse' and 'isValid'.
        """
        pass

    @abstractmethod
    def get_prompt_generator(self):
        """
        Return a function to generate prompts for a given data point.

        Returns:
            function: A callable function that takes a data_point as input 
                      and returns systemPrompt (str) and userPrompt (str).
        """
        pass

class ContractNLIDataset(DatasetInterface):
    """
    A class to handle operations on the Contract NLI dataset.

    Attributes:
        dataset (DatasetDict): The loaded Hugging Face dataset with splits.
        label_feature (function): for converting labels from strings to ints and the opposite
    """

    def __init__(self, prompting_technique='naive zero-shot', subset_name="contractnli_b"):
        """
        Initializes the dataset class and logs in to Hugging Face.
        """

        if prompting_technique not in ["naive zero-shot", "optimized zero-shot", "naive few-shot", "naive few-shot isolated spans", "naive_few_shot_isolated_spans_same_hypothesis", "naive_few_shot_isolated_spans_same_hypothesis_chainOfThought", "naive_zero_shot_in_document_rag_naive_chunking", "naive_zero_shot_multi_agent_framework", "naive_few_shot_isolated_spans_same_hypothesis_multi_agent_framework", "naive_zero_shot_lightRAG", "naive_zero_shot_multi_agent_framework_with_predictions", "naive_zero_shot_lightRAG_with_predictions", "naive_zero_shot_with_hypothesis_summary", "hypothesis_composable_graph_rag"]:
            raise ValueError("Invalid prompting technique. Choose from 'naive zero-shot', 'optimized zero-shot', 'naive few-shot', 'naive few-shot isolated spans', 'naive_few_shot_isolated_spans_same_hypothesis', 'naive_few_shot_isolated_spans_same_hypothesis_chainOfThought', 'naive_zero_shot_in_document_rag_naive_chunking', 'naive_zero_shot_multi_agent_framework', 'naive_few_shot_isolated_spans_same_hypothesis_multi_agent_framework', 'naive_zero_shot_lightRAG', 'naive_zero_shot_multi_agent_framework_with_predictions', 'naive_zero_shot_lightRAG_with_predictions', 'naive_zero_shot_with_hypothesis_summary', 'hypothesis_composable_graph_rag'.")

        self.prompting_technique = prompting_technique
        HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
        if not HUGGINGFACE_TOKEN:
            raise EnvironmentError("HUGGINGFACE_TOKEN environment variable is not set.")
        # Login to Hugging Face
        login(token=HUGGINGFACE_TOKEN)

        # Add a cache for chain of thoughts
        self.chain_of_thoughts = {}
        self.indexed_documents = {}
        dataset_name="kiddothe2b/contract-nli"

        # Load the dataset
        print("Loading dataset...")
        self.dataset = load_dataset(dataset_name, subset_name)
        self.isolated_spans_dataset = load_dataset(dataset_name, "contractnli_a")
        # Convert label integers to "entailment", "contradiction", "neutral"
        self.label_feature = self.dataset["train"].features["label"]
        print("Dataset loaded successfully.")

        # Initialize Chroma DB if we're using RAG
        if self.prompting_technique == "naive_zero_shot_in_document_rag_naive_chunking":
            self._init_chroma_db()

        if self.prompting_technique == "hypothesis_composable_graph_rag":
            self._init_hypothesis_graphs()

    def _init_hypothesis_graphs(self):
        from llama_index.core import Settings
        from llama_index.embeddings.openai import OpenAIEmbedding
        import json
        
        def setup_embeddings():
            api_key = os.environ.get("EMBEDDINGS_API_KEY")
            if not api_key:
                logger.warning("EMBEDDINGS_API_KEY not found, using fallback")
                return None
            
            embed_model = OpenAIEmbedding(model="text-embedding-3-large", api_key=api_key)
            return embed_model
        
        embed_model = setup_embeddings()
        
        if embed_model is not None:
            Settings.embed_model = embed_model
        
        # Storage directory where indices are saved
        storage_dir = os.path.join(os.getcwd(), "indices_storage_whole_dataset")
        
        # Load the hypothesis mapping
        # mapping_path = os.path.join(storage_dir, "hypothesis_mapping.json")
        
        # with open(mapping_path, 'r') as f:
        #     self.hypothesis_map = json.load(f)
        
        # # Find matching hypothesis ID
        # hypothesis_id = None
        # for hypothesis_text, hypothesis_id_value in hypothesis_map.items():
        #     if hypothesis_text.strip() == data_point["hypothesis"].strip():
        #         hypothesis_id = hypothesis_id_value
        #         break
        
        # if hypothesis_id is None:
        #     logger.warning(f"No matching hypothesis found for: {data_point['hypothesis']}")
        #     return naive_zero_shot(data_point)
        
        # logger.info(f"Found matching hypothesis ID: {hypothesis_id}")
        
        indices, hypothesis_map = load_saved_indices(storage_dir)
        self.hypotheses_graphs = create_hypothesis_graphs(indices)

    def _init_chroma_db(self):
        """Initialize Chroma vector database with embedding model"""
        try:
            from langchain_openai import OpenAIEmbeddings
            from langchain_chroma import Chroma
            from langchain.text_splitter import RecursiveCharacterTextSplitter

            from chromadb.config import Settings

            # Then in your _init_chroma_db method:
            client_settings = Settings(
                persist_directory="./chroma_db",
            )

            collection_metadata = {
                "hnsw:M": 100,
                "hnsw:construction_ef": 500, 
                "hnsw:search_ef": 1000
            }

            self.db = Chroma(
                collection_name="experimentsLibrary", 
                embedding_function=OpenAIEmbeddings(model="text-embedding-3-large"),
                client_settings=client_settings,
                collection_metadata=collection_metadata
            )

            logger.info("Initialized Chroma DB")
            
            # Initialize text splitter
            self.splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )

        except Exception as e:
            error_msg = f"Error initializing Chroma DB: {e}\n{traceback.format_exc()}"
            raise Exception(error_msg) from e

    def describe_dataset(self):
        """
        Prints detailed information about the dataset.
        """
        print("First row of Train Data:")
        print(self.dataset["train"][0])

        # Description and metadata
        print("Information of dataset: ", self.dataset["train"].info)

        # Dataset features
        print("Dataset Features: ", self.dataset["train"].features)

        # Dataset splits and sizes
        print("Dataset Splits and Sizes:")
        print({split: len(self.dataset[split]) for split in self.dataset.keys()})

        # Columns in the training split
        print("Columns in the Train Split:")
        print(self.dataset["train"].column_names)

        print("Label conversion examples:")
        print(self.label_feature.int2str(self.dataset["train"][0]["label"]))

        print("NEUTRAL TO INTEGER: ", self.label_feature.str2int("NEUTRAL".lower()))
        print("CONTRADICTION TO INTEGER: ", self.label_feature.str2int("CONTRADICTION".lower()))
        print("ENTAILMENT TO INTEGER: ", self.label_feature.str2int("ENTAILMENT".lower()))

    def analyze_class_distribution(self):
        """
        Analyzes and prints the class distribution as percentages for each split in the dataset.
        """
        for split_name, split_data in self.dataset.items():
            print(f"\nAnalyzing split: {split_name}")
            labels = split_data["label"]
            total = len(labels)
            for label, count in Counter(labels).items():
                percentage = (count / total) * 100
                print(f"Class {label}: {percentage:.2f}% ({count}/{total})")

    import re

    @staticmethod
    def responseChecker(response):
        """
        Checks if the response contains one of the words: 
        {"entailment", "contradiction", "neutral"} or their variations.
        
        - If a match is found, it returns a dictionary with the mapped response and True.
        - If no match is found, it returns {"modifiedResponse": response, "isValid": False}.
        - Any text inside <think>...</think> tags is placed inside reasoning tags.
        """
        
        reasoning_text = ""
        if "<reasoning>" not in response:
            match = re.search(r'<think>(.*?)</think>', response, flags=re.DOTALL)
            if match:
                reasoning_text = match.group(1).strip()
                response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        else:
            match = re.search(r'<reasoning>(.*?)</reasoning>', response, flags=re.DOTALL)
            if match:
                reasoning_text = match.group(1).strip()
                response = re.sub(r'<reasoning>.*?</reasoning>', '', response, flags=re.DOTALL)

        # Define target categories and similar words
        target_mapping = {
            "entailment": {"entailment", "entailed", "entailing"},
            "contradiction": {"contradiction", "contradictory", "contradicts", "contradicting", "contradicted"},
            "neutral": {"neutral"}
        }

        # Normalize words in the response and check for matches
        for word in response.split():
            cleaned_word = clean(word)  # Apply any necessary text cleaning
            for category, synonyms in target_mapping.items():
                if cleaned_word.lower() in synonyms:
                    if reasoning_text:
                        return {"modifiedResponse": f"{category} <reasoning>{reasoning_text}</reasoning>", "isValid": True}
                    else:
                        return {"modifiedResponse": f"{category}", "isValid": True}
        
        return {"modifiedResponse": response, "isValid": False}
    
    def get_str_to_int_function(self):
        """
        Returns a function that converts string labels to integer labels.

        Returns:
            function: A callable function for string-to-integer label conversion.
        """
        def str_to_int(label_str):
            return self.label_feature.str2int(label_str.lower())
        
        return str_to_int

    def get_int_to_str_function(self):
        """
        Returns a function that converts integer labels to string labels.

        Returns:
            function: A callable function for integer-to-string label conversion.
        """
        def int_to_str(label_int):
            return self.label_feature.int2str(label_int)
        
        return int_to_str
    
    def get_prompt_generator(self):
        """
        Returns a function to generate systemPrompt and userPrompt for a given data_point.

        Returns:
            function: A callable function that takes a data_point (dict) as an argument 
                      and returns systemPrompt (str) and userPrompt (str).
        """
        def naive_zero_shot(data_point):
            """
            Generates prompts based on the given data_point using naive zero shot prompting technique.

            Args:
                data_point (dict): A dictionary with keys "premise" and "hypothesis".

            Returns:
                tuple: A tuple containing systemPrompt (str) and userPrompt (str).
            """

            ########################### PROMPTS ########################

            reasoning = os.environ.get("REASONING", "false")
            if reasoning != "false":
                systemPrompt_template = """
                You are a helpful lawyer's assistant tasked with determining whether given hypotheses are entailed, 
                contradicted, or neutral with respect to an NDA contract.

                You will be given a contract and a hypothesis.
                Provide the reasoning as a report and any additional information that led to your conclusion inside the <reasoning>...</reasoning> tags.

                ### **Instructions for Your Reasoning:**
                Try the reasoning/report that you will give to address these criteria:
                - The report must clearly explain not only the conclusion but also the reasoning process and the supporting evidence. The user should be able to follow the logic step by step.

                - The report must provide explicit references or quotations from the source document(s) that directly support its claims or conclusions. Citations should be relevant, specific, and appropriately attributed.

                - The conclusion must follow logically from the evidence and analysis provided. There must not be leaps in logic or unsupported inferences. The reasoning path should be valid and sound.

                - The report must demonstrate a clear understanding of the context of the question and the legal terminology used in the source. It accurately interprets legal clauses, definitions, and relationships.

                - The report must identify and appropriately handles ambiguous terms, clauses, or multiple interpretations. It may present alternatives or explain why a particular interpretation is preferred.

                - When the information available is insufficient to reach a definitive conclusion, the report must explicitly acknowledge the gap instead of speculating or fabricating.

                - The report must be succinct, avoiding unnecessary repetition or verbose language, while still being thorough and informative. It must convey the key points with clarity and efficiency.

                - The report must be well-structured, logically organized, and easy to follow. Transitions between points are smooth, and the structure supports readability and comprehension.

                - The report must directly address the user’s question, maintaining a consistent focus throughout. It must avoid off-topic content and aligns closely with the query intent.

                - The report must address all relevant aspects of the query. It must not omit important points that could materially affect the interpretation or conclusion.
                """

                userPrompt_template = """
                Contract: ```
                {CONTRACT}
                ```

                Hypothesis: ```
                {HYPOTHESIS}
                ```

                Give the answer in only one word:
                "ENTAILMENT" if the hypothesis is entailed by the contract.
                "CONTRADICTION" if the hypothesis is contradicted by the contract.
                "NEUTRAL" if the hypothesis is neutral to (not referenced by) the contract.

                Provide the reasoning and any additional information that led to your conclusion inside the <reasoning>...</reasoning> tags.
                """
            else:
                systemPrompt_template = """
                You are a helpful lawyer's assistant tasked with determining whether given hypotheses are entailed, 
                contradicted, or neutral with respect to an NDA contract.

                You will be given a contract and a hypothesis.
                """

                userPrompt_template = """
                Contract: ```
                {CONTRACT}
                ```

                Hypothesis: ```
                {HYPOTHESIS}
                ```

                Give the answer in only one word:
                "ENTAILMENT" if the hypothesis is entailed by the contract.
                "CONTRADICTION" if the hypothesis is contradicted by the contract.
                "NEUTRAL" if the hypothesis is neutral to (not referenced by) the contract.
                """

            ######################################################
            systemPrompt = systemPrompt_template
            userPrompt = userPrompt_template.format(CONTRACT=data_point["premise"], HYPOTHESIS=data_point["hypothesis"])
            return systemPrompt, userPrompt

        def optimized_zero_shot(data_point):
            """
            Generates prompts based on the given data_point using optimized zero shot prompting technique

            Args:
                data_point (dict): A dictionary with keys "premise" and "hypothesis".

            Returns:
                tuple: A tuple containing systemPrompt (str) and userPrompt (str).
            """

            ########################### PROMPTS ########################

            systemPrompt_template = """
            You are an expert legal assistant specializing in Natural Language Inference (NLI) for contract analysis. Your task is to evaluate the logical relationship between a given hypothesis and an NDA contract. This involves determining whether the hypothesis is:

            1. **ENTAILMENT**:
            - The hypothesis is logically true based on the content of the contract.
            - It is explicitly stated or can be directly inferred.
            - Example: 
                - Contract: "The employee must not disclose trade secrets to third parties."
                - Hypothesis: "The employee is prohibited from sharing trade secrets."

            2. **CONTRADICTION**:
            - The hypothesis directly conflicts with the contract's content.
            - Example:
                - Contract: "The employee must disclose trade secrets to authorized personnel."
                - Hypothesis: "The employee is not allowed to disclose trade secrets under any circumstances."

            3. **NEUTRAL**:
            - The hypothesis is unrelated to the contract, or there is insufficient information to conclude its truth or falsehood.
            - Example:
                - Contract: "The employee must not disclose trade secrets to third parties."
                - Hypothesis: "The employee can work remotely."

            ### Additional Rules:
            - Only respond with one word: "ENTAILMENT," "CONTRADICTION," or "NEUTRAL."
            - Do not provide explanations.

            """

            userPrompt_template = """
            Evaluate the following NDA contract and hypothesis based on Natural Language Inference (NLI):
            Contract: ```
            {CONTRACT}
            ```

            Hypothesis: ```
            {HYPOTHESIS}
            ```

            Give the answer in only one word:
            "ENTAILMENT" if the hypothesis is explicitly supported or logically follows from the contract.
            "CONTRADICTION" if the hypothesis directly conflicts with the contract's content.
            "NEUTRAL" if the hypothesis is unrelated to or not inferable from the contract.
            """

            ######################################################
            systemPrompt = systemPrompt_template
            userPrompt = userPrompt_template.format(CONTRACT=data_point["premise"], HYPOTHESIS=data_point["hypothesis"])
            return systemPrompt, userPrompt

        def naive_few_shot(data_point):
            """
            Generates prompts based on the given data_point using naive few shot prompting technique

            Args:
                data_point (dict): A dictionary with keys "premise" and "hypothesis".

            Returns:
                tuple: A tuple containing systemPrompt (str) and userPrompt (str).
            """

            # Combine train and validate datasets
            combined_dataset = concatenate_datasets([self.dataset['train'], self.dataset['validation']])

            # THE BEST THING IS NOT TO FEED THE WHOLE CONTRACT BUT ONLY THE SPANS THAT HOLD THE ANSWER

            # Randomly select three examples
            few_shot_examples = random.sample(list(combined_dataset), 3)
            int_to_str_function = self.get_int_to_str_function()
            # Format the examples
            few_shot_examples_text = "\n".join(
                [
                    f"Example {i + 1}:\nContract: \"{example['premise']}\"\nHypothesis: \"{example['hypothesis']}\"\nAnswer: {int_to_str_function(example['label'])}\n"
                    for i, example in enumerate(few_shot_examples)
                ]
            )

            ########################### PROMPTS ########################

            systemPrompt_template = """
            You are an expert legal assistant specializing in Natural Language Inference (NLI) for contract analysis. Your task is to evaluate the logical relationship between a given hypothesis and an NDA contract. This involves determining whether the hypothesis is:

            1. **ENTAILMENT**:
            - The hypothesis is logically true based on the content of the contract.
            - It is explicitly stated or can be directly inferred.
            - Example: 
                - Contract: "The employee must not disclose trade secrets to third parties."
                - Hypothesis: "The employee is prohibited from sharing trade secrets."

            2. **CONTRADICTION**:
            - The hypothesis directly conflicts with the contract's content.
            - Example:
                - Contract: "The employee must disclose trade secrets to authorized personnel."
                - Hypothesis: "The employee is not allowed to disclose trade secrets under any circumstances."

            3. **NEUTRAL**:
            - The hypothesis is unrelated to the contract, or there is insufficient information to conclude its truth or falsehood.
            - Example:
                - Contract: "The employee must not disclose trade secrets to third parties."
                - Hypothesis: "The employee can work remotely."

            ### Examples: 
            {EXAMPLES_TEXT}

            ### Additional Rules:
            - Only respond with one word: "ENTAILMENT," "CONTRADICTION," or "NEUTRAL."
            - Do not provide explanations.

            """

            userPrompt_template = """
            Evaluate the following NDA contract and hypothesis based on Natural Language Inference (NLI):
            Contract: ```
            {CONTRACT}
            ```

            Hypothesis: ```
            {HYPOTHESIS}
            ```

            Give the answer in only one word:
            "ENTAILMENT" if the hypothesis is explicitly supported or logically follows from the contract.
            "CONTRADICTION" if the hypothesis directly conflicts with the contract's content.
            "NEUTRAL" if the hypothesis is unrelated to or not inferable from the contract.
            """

            ######################################################
            systemPrompt = systemPrompt_template.format(EXAMPLES_TEXT=few_shot_examples_text)
            userPrompt = userPrompt_template.format(CONTRACT=data_point["premise"], HYPOTHESIS=data_point["hypothesis"])
            return systemPrompt, userPrompt
        
        def naive_few_shot_isolated_spans(data_point):
            """
            Generates prompts based on the given data_point using naive few shot (on the isolated evidence spans) prompting technique 

            Args:
                data_point (dict): A dictionary with keys "premise" and "hypothesis".

            Returns:
                tuple: A tuple containing systemPrompt (str) and userPrompt (str).
            """

            # Combine train and validate datasets
            combined_dataset = concatenate_datasets([self.isolated_spans_dataset['train'], self.isolated_spans_dataset['validation']])

            # THE BEST THING IS NOT TO FEED THE WHOLE CONTRACT BUT ONLY THE SPANS THAT HOLD THE ANSWER

            # Randomly select three examples
            few_shot_examples = random.sample(list(combined_dataset), 3)
            int_to_str_function = self.get_int_to_str_function()
            # Format the examples
            few_shot_examples_text = "\n".join(
                [
                    f"Example {i + 1}:\nContract: \"{example['premise']}\"\nHypothesis: \"{example['hypothesis']}\"\nAnswer: {int_to_str_function(example['label'])}\n"
                    for i, example in enumerate(few_shot_examples)
                ]
            )

            ########################### PROMPTS ########################

            systemPrompt_template = """
            You are an expert legal assistant specializing in Natural Language Inference (NLI) for contract analysis. Your task is to evaluate the logical relationship between a given hypothesis and an NDA contract. This involves determining whether the hypothesis is:

            1. **ENTAILMENT**:
            - The hypothesis is logically true based on the content of the contract.
            - It is explicitly stated or can be directly inferred.
            - Example: 
                - Contract: "The employee must not disclose trade secrets to third parties."
                - Hypothesis: "The employee is prohibited from sharing trade secrets."

            2. **CONTRADICTION**:
            - The hypothesis directly conflicts with the contract's content.
            - Example:
                - Contract: "The employee must disclose trade secrets to authorized personnel."
                - Hypothesis: "The employee is not allowed to disclose trade secrets under any circumstances."

            3. **NEUTRAL**:
            - The hypothesis is unrelated to the contract, or there is insufficient information to conclude its truth or falsehood.
            - Example:
                - Contract: "The employee must not disclose trade secrets to third parties."
                - Hypothesis: "The employee can work remotely."

            ### Examples: 
            {EXAMPLES_TEXT}

            ### Additional Rules:
            - Only respond with one word: "ENTAILMENT," "CONTRADICTION," or "NEUTRAL."
            - Do not provide explanations.

            """

            userPrompt_template = """
            Evaluate the following NDA contract and hypothesis based on Natural Language Inference (NLI):
            Contract: ```
            {CONTRACT}
            ```

            Hypothesis: ```
            {HYPOTHESIS}
            ```

            Give the answer in only one word:
            "ENTAILMENT" if the hypothesis is explicitly supported or logically follows from the contract.
            "CONTRADICTION" if the hypothesis directly conflicts with the contract's content.
            "NEUTRAL" if the hypothesis is unrelated to or not inferable from the contract.
            """

            ######################################################
            systemPrompt = systemPrompt_template.format(EXAMPLES_TEXT=few_shot_examples_text)
            userPrompt = userPrompt_template.format(CONTRACT=data_point["premise"], HYPOTHESIS=data_point["hypothesis"])
            print("systemPrompt: ", systemPrompt)
            print("userPrompt: ", userPrompt)
            return systemPrompt, userPrompt

        def naive_few_shot_isolated_spans_same_hypothesis(data_point):
            """
            Generates prompts based on the given data_point using naive few shot (on the isolated evidence spans and the same hypothesis) prompting technique 

            Args:
                data_point (dict): A dictionary with keys "premise" and "hypothesis".

            Returns:
                tuple: A tuple containing systemPrompt (str) and userPrompt (str).
            """

            # Combine train and validate datasets
            combined_dataset_full = concatenate_datasets([self.dataset['train'], self.dataset['validation']])
            combined_dataset = concatenate_datasets([self.isolated_spans_dataset['train'], self.isolated_spans_dataset['validation']])

            combined_dataset = [example for example in combined_dataset if example['hypothesis'] == data_point['hypothesis']]

            # Randomly pick three examples for each label
            labels = [0, 1, 2]  
            few_shot_examples = []
            for label in labels:
                label_examples = [example for example in combined_dataset if example['label'] == label]
                if len(label_examples) < 3:
                    few_shot_examples.extend(label_examples)  # Use all available examples
                else:
                    few_shot_examples.extend(random.sample(label_examples, 3))

            int_to_str_function = self.get_int_to_str_function()
            # Format the examples
            few_shot_examples_text = "\n".join(
                [
                    f"Example {i + 1}:\nSpan: \"{example['premise']}\"\nHypothesis: \"{example['hypothesis']}\"\nAnswer: {int_to_str_function(example['label'])}\n"
                    for i, example in enumerate(few_shot_examples)
                ]
            )

            ########################### PROMPTS ########################

            systemPrompt_template = """
            You are an expert legal assistant specializing in Natural Language Inference (NLI) for contract analysis. Your task is to evaluate the logical relationship between a given hypothesis and an NDA contract. This involves determining whether the hypothesis is:

            1. **ENTAILMENT**:
            - The hypothesis is logically true based on the content of the contract.
            - It is explicitly stated or can be directly inferred.
            - Example: 
                - Contract: "The employee must not disclose trade secrets to third parties."
                - Hypothesis: "The employee is prohibited from sharing trade secrets."

            2. **CONTRADICTION**:
            - The hypothesis directly conflicts with the contract's content.
            - Example:
                - Contract: "The employee must disclose trade secrets to authorized personnel."
                - Hypothesis: "The employee is not allowed to disclose trade secrets under any circumstances."

            3. **NEUTRAL**:
            - The hypothesis is unrelated to the contract, or there is insufficient information to conclude its truth or falsehood.
            - Example:
                - Contract: "The employee must not disclose trade secrets to third parties."
                - Hypothesis: "The employee can work remotely."

            ### Examples: 
            You will be given a contract like the following:
            {EXAMPLE_CONTRACT}

            From this contract you must extract the exact spans that hold the answer to the hypothesis.
            Then you must evaluate the hypothesis based on the extracted spans as follows:
            {EXAMPLES_TEXT}

            ### Additional Rules:
            - Only respond with one word: "ENTAILMENT," "CONTRADICTION," or "NEUTRAL."
            - Do not provide explanations.

            """

            userPrompt_template = """
            Evaluate the following NDA contract and hypothesis based on Natural Language Inference (NLI):
            Contract: ```
            {CONTRACT}
            ```

            Hypothesis: ```
            {HYPOTHESIS}
            ```

            Give the answer in only one word:
            "ENTAILMENT" if the hypothesis is explicitly supported or logically follows from the contract.
            "CONTRADICTION" if the hypothesis directly conflicts with the contract's content.
            "NEUTRAL" if the hypothesis is unrelated to or not inferable from the contract.
            """

            ######################################################
            systemPrompt = systemPrompt_template.format(EXAMPLE_CONTRACT=random.sample(list(combined_dataset_full), 1)[0]["premise"], EXAMPLES_TEXT=few_shot_examples_text)
            userPrompt = userPrompt_template.format(CONTRACT=data_point["premise"], HYPOTHESIS=data_point["hypothesis"])
            print("systemPrompt: ", systemPrompt)
            print("userPrompt: ", userPrompt)
            return systemPrompt, userPrompt

        def naive_few_shot_isolated_spans_same_hypothesis_chainOfThought(data_point):
            """
            Generates prompts based on the given data_point using naive few shot (on the isolated evidence spans and the same hypothesis) and chain of thought prompting technique 

            Args:
                data_point (dict): A dictionary with keys "premise" and "hypothesis".

            Returns:
                tuple: A tuple containing systemPrompt (str) and userPrompt (str).
            """

            # Get hypothesis for caching
            hypothesis = data_point["hypothesis"]
            if hypothesis not in self.chain_of_thoughts:

                # Combine train and validate datasets
                combined_dataset_full = concatenate_datasets([self.dataset['train'], self.dataset['validation']])
                combined_dataset = concatenate_datasets([self.isolated_spans_dataset['train'], self.isolated_spans_dataset['validation']])

                combined_dataset = [example for example in combined_dataset if example['hypothesis'] == data_point['hypothesis']]

                # Randomly pick examples for each label
                labels = [0, 1, 2]  
                few_shot_examples = []
                for label in labels:
                    label_examples = [example for example in combined_dataset if example['label'] == label]
                    if len(label_examples) < 1:
                        few_shot_examples.extend(label_examples)  # Use all available examples
                    else:
                        few_shot_examples.extend(random.sample(label_examples, 1))

                ########################### PROMPTS CHAIN OF THOUGHT ########################

                systemPrompt_template_chot = """
                You are an expert legal assistant specializing in Natural Language Inference (NLI) for contract analysis. Your task is to justify the logical relationship between a given hypothesis and an NDA contract for a given label. The labels for a hypothesis are:

                1. **ENTAILMENT**:
                - The hypothesis is logically true based on the content of the contract.
                - It is explicitly stated or can be directly inferred.
                - Example: 
                    - Contract: "The employee must not disclose trade secrets to third parties."
                    - Hypothesis: "The employee is prohibited from sharing trade secrets."

                2. **CONTRADICTION**:
                - The hypothesis directly conflicts with the contract's content.
                - Example:
                    - Contract: "The employee must disclose trade secrets to authorized personnel."
                    - Hypothesis: "The employee is not allowed to disclose trade secrets under any circumstances."

                3. **NEUTRAL**:
                - The hypothesis is unrelated to the contract, or there is insufficient information to conclude its truth or falsehood.
                - Example:
                    - Contract: "The employee must not disclose trade secrets to third parties."
                    - Hypothesis: "The employee can work remotely."

                You will be given a span, a hypothesis and a label. 
                Your goal is to find a detailed chain of thought that justifies the label for the hypothesis based on the span provided. 
                Provide instructions on how to think in order to conclude to the given label by the span and the hypothesis.
                """

                userPrompt_template_chot = """
                Try to justify how the label is derived for the following span-hypothesis pair based on Natural Language Inference (NLI):
                Span: ```
                {SPAN}
                ```

                Hypothesis: ```
                {HYPOTHESIS}
                ```

                Label: ```
                {LABEL}
                ```

                Provide step-by-step reasoning (Chain of Thought) on how to approach the problem and determine the hypothesis that aligns with the given label.
                """

                ######################################################

                int_to_str_function = self.get_int_to_str_function()

                chain_of_thoughts = []
                for example in few_shot_examples:
                    chain_of_thoughts.append(openaiApiCall({"name": "ChatGPT-4o", "id": "gpt-4o", "args": None, "API": "OPENAI"}, systemPrompt_template_chot, userPrompt_template_chot.format(SPAN=example["premise"], HYPOTHESIS=example["hypothesis"], LABEL=int_to_str_function(example['label']))))

                # Generate formatted examples with integrated chain of thought responses
                few_shot_examples_text = "\n".join(
                    [
                        f"Example {i + 1}:\n"
                        f"Span: \"{example['premise']}\"\n"
                        f"Hypothesis: \"{example['hypothesis']}\"\n"
                        f"Label: \"{int_to_str_function(example['label'])}\"\n"
                        f"Chain of Thought: {chain_of_thoughts[i]}\n"
                        for i, example in enumerate(few_shot_examples)
                    ]
                )

                # Cache the examples and their text for this hypothesis
                self.chain_of_thoughts[hypothesis] = {
                    'few_shot_examples_text': few_shot_examples_text,
                    'example_contract': random.sample(list(combined_dataset_full), 1)[0]["premise"]
                }

            ########################### PROMPTS ########################

            systemPrompt_template = """
            You are an expert legal assistant specializing in Natural Language Inference (NLI) for contract analysis. Your task is to evaluate the logical relationship between a given hypothesis and an NDA contract. This involves determining whether the hypothesis is:

            1. **ENTAILMENT**:
            - The hypothesis is logically true based on the content of the contract.
            - It is explicitly stated or can be directly inferred.
            - Example: 
                - Contract: "The employee must not disclose trade secrets to third parties."
                - Hypothesis: "The employee is prohibited from sharing trade secrets."

            2. **CONTRADICTION**:
            - The hypothesis directly conflicts with the contract's content.
            - Example:
                - Contract: "The employee must disclose trade secrets to authorized personnel."
                - Hypothesis: "The employee is not allowed to disclose trade secrets under any circumstances."

            3. **NEUTRAL**:
            - The hypothesis is unrelated to the contract, or there is insufficient information to conclude its truth or falsehood.
            - Example:
                - Contract: "The employee must not disclose trade secrets to third parties."
                - Hypothesis: "The employee can work remotely."

            ### Examples: 
            You will be given a contract like the following:
            {EXAMPLE_CONTRACT}

            From this contract you must extract the exact spans that hold the answer to the hypothesis.
            Then you must evaluate the hypothesis based on the extracted spans as follows:
            {EXAMPLES_TEXT}

            ### Additional Rules:
            - Only respond with one word: "ENTAILMENT," "CONTRADICTION," or "NEUTRAL."
            - Do not provide explanations.

            """

            userPrompt_template = """
            Evaluate the following NDA contract and hypothesis based on Natural Language Inference (NLI):
            Contract: ```
            {CONTRACT}
            ```

            Hypothesis: ```
            {HYPOTHESIS}
            ```

            Give the answer in only one word:
            "ENTAILMENT" if the hypothesis is explicitly supported or logically follows from the contract.
            "CONTRADICTION" if the hypothesis directly conflicts with the contract's content.
            "NEUTRAL" if the hypothesis is unrelated to or not inferable from the contract.
            """

            ######################################################
            few_shot_examples_text = self.chain_of_thoughts[hypothesis]['few_shot_examples_text']
            example_contract = self.chain_of_thoughts[hypothesis]['example_contract']
            systemPrompt = systemPrompt_template.format(EXAMPLE_CONTRACT=example_contract, EXAMPLES_TEXT=few_shot_examples_text)
            userPrompt = userPrompt_template.format(CONTRACT=data_point["premise"], HYPOTHESIS=data_point["hypothesis"])
            print("systemPrompt: ", systemPrompt)
            print("userPrompt: ", userPrompt)
            return systemPrompt, userPrompt
        
        def naive_zero_shot_in_document_rag_naive_chunking(data_point):
            """
            Generates prompts based on the given data_point using naive zero shot prompting technique with in document rag and naive chunking.

            Args:
                data_point (dict): A dictionary with keys "premise" and "hypothesis".

            Returns:
                tuple: A tuple containing systemPrompt (str) and userPrompt (str).
            """
            ######################## INDEXING ########################
            # PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
            # if not PINECONE_API_KEY:
            #     raise EnvironmentError("PINECONE_API_KEY environment variable is not set.")
            
            # PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
            # if not PINECONE_INDEX_NAME:
            #     raise EnvironmentError("PINECONE_INDEX_NAME environment variable is not set.")
            
            # PINECONE_API_HOST = os.getenv("PINECONE_API_HOST")
            # if not PINECONE_API_HOST:
            #     raise EnvironmentError("PINECONE_API_HOST environment variable is not set.")

            # try:
            #     pc = Pinecone(api_key=PINECONE_API_KEY, base_url=PINECONE_API_HOST)
            #     pc_index = pc.Index(PINECONE_INDEX_NAME)
            #     pc_index.delete(delete_all=True)
            # except Exception as e:
            #     error_msg = f"Error deleting Pinecone index: {e}\n{traceback.format_exc()}"
            #     raise Exception(error_msg) from e
            
            # try:
            #     import hashlib
            #     # Create a stable ID for the document
            #     def generate_id(text):
            #         return hashlib.md5(text.encode()).hexdigest()

            #     # Generate an ID for the new document
            #     document_id = generate_id(data_point["premise"])

            #     # Check if this ID already exists in FAISS
            #     existing_docs = [doc for doc in self.db.docstore._dict.values() if doc.metadata.get("id") == document_id]
            #     if existing_docs:
            #         logger.info("Document already exists. Skipping indexing.")
            #     else:
            #         logger.info("New document detected. Deleting old documents and indexing the new one.")
            #         # FAISS doesn't do partial deletions—rebuild from scratch with only the new doc
            #         docs = [Document(page_content=data_point["premise"], metadata={"id": document_id})]
            #         splitted_docs = self.splitter.split_documents(docs)
            #         logger.info(f"Number of splitted documents: {len(splitted_docs)}")

            #         # Create a fresh FAISS store with only these chunks
            #         self.db = FAISS.from_documents(splitted_docs, self.embeddings)
            #         logger.info("Number of documents in the vector store: %d", len(self.db.docstore._dict))

            #     # Retrieve top-k chunks for the hypothesis
            #     retriever = self.db.as_retriever(search_kwargs={"k": 5})
            #     docs = retriever.get_relevant_documents(data_point["hypothesis"])
            #     logger.info(f"Number of retrieved documents: {len(docs)}")

            #     # Format the retrieved docs into context text
            #     context_text = format_documents(docs)

            # except Exception as e:
            #     error_msg = f"Error in naive_zero_shot_in_document_rag_naive_chunking: {e}\n{traceback.format_exc()}"
            #     raise Exception(error_msg) from e

            try:
                import hashlib
                def generate_id(text):
                    return hashlib.md5(text.encode()).hexdigest()  # Creates a hash ID

                # Generate an ID for the document
                document_id = generate_id(data_point['premise'])
                
                all_docs = self.db._collection.get()
                existing_docs = [doc for doc, meta in zip(all_docs["documents"], all_docs["metadatas"]) if meta.get("id") == document_id]
                if existing_docs:  # If the document already exists, do nothing
                    logger.info("Document already exists. Skipping indexing.")
                else:
                    logger.info("New document detected. Deleting old documents and indexing the new one.")
                    ids = self.db._collection.get()["ids"]
                    if ids:  # Check if there are any documents to delete
                        self.db._collection.delete(ids)
                    
                    docs = [Document(page_content=data_point['premise'], metadata={"id": document_id})]
                    splitted_docs = self.splitter.split_documents(docs)
                    logger.info(f"Number of splitted documents: {len(splitted_docs)}")
                    self.db.add_documents(splitted_docs)
                    num_docs = self.db._collection.count()
                    logger.info("Number of documents in the vector store: %d", num_docs)
                    
                doc_count = self.db._collection.count()  # Get number of indexed documents
                retriever = self.db.as_retriever(search_kwargs={"k": min(5, doc_count)})
                docs = retriever.invoke(data_point["hypothesis"])

                logger.info(f"Number of retrieved documents: {len(docs)}")
                context_text = format_documents(docs)
            except Exception as e:
                error_msg = f"Error in naive_zero_shot_in_document_rag_naive_chunking: {e}\n{traceback.format_exc()}"
                logger.error(error_msg)
                return naive_zero_shot(data_point)

            # vectorstore = PineconeVectorStore.from_documents(
            #     documents=splitted_docs,
            #     embedding=OpenAIEmbeddings(model="text-embedding-3-large"),
            #     index_name=PINECONE_INDEX_NAME
            # )

            #########################################################

            ##################### RETRIEVING ########################
            # vectorstore = PineconeVectorStore(index_name="test", embedding=OpenAIEmbeddings(model="text-embedding-3-large"))
            # retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

            # # wait the indexing to complete
            # while pc_index.describe_index_stats()['total_vector_count'] < 1:
            #     logger.info(f"Index contains {pc_index.describe_index_stats()['total_vector_count']} vectors")
            
            # documents = retriever.invoke(data_point["hypothesis"], k=5)
            # logger.info(f"Number of retrieved documents: {len(documents)}")
            # context_text = format_documents(documents)

            #########################################################

            ########################### PROMPTS ########################

            systemPrompt_template = """
            You are a helpful lawyer's assistant tasked with determining whether given hypotheses are entailed, 
            contradicted, or neutral with respect to an NDA contract.

            You will be given spans from the contract and a hypothesis.
            """

            userPrompt_template = """
            Spans from the contract: ```
            {CONTEXT}
            ```

            Hypothesis: ```
            {HYPOTHESIS}
            ```

            Give the answer in only one word:
            "ENTAILMENT" if the hypothesis is entailed by the contract.
            "CONTRADICTION" if the hypothesis is contradicted by the contract.
            "NEUTRAL" if the hypothesis is neutral to (not referenced by) the contract.
            """

            ######################################################
            systemPrompt = systemPrompt_template
            userPrompt = userPrompt_template.format(CONTEXT=context_text, HYPOTHESIS=data_point["hypothesis"])
            return systemPrompt, userPrompt
        
        def naive_zero_shot_multi_agent_framework(data_point):
            """
            Generates prompts based on the given data_point using naive zero shot prompting technique tailored for the multi agent call.

            Args:
                data_point (dict): A dictionary with keys "premise" and "hypothesis".

            Returns:
                tuple: A tuple containing systemPrompt (str) and userPrompt (str).
            """

            ####################### INDEXING FIRST ########################

            ########################### PROMPTS ########################

            userQuery = "Is the following hypothesis ENTAILMENT, CONTRADICTION, or NEUTRAL according to the content of the contract: <hypothesis>{hypothesis}</hypothesis>?".format(hypothesis=data_point["hypothesis"])
            userInstructions = """
            The legal researcher has access to the specific contract and can help you reach a decision. You can ask him questions regarding the contract. He doesn't know what the hypothesis is.
            Give the answer in only one word:
                "ENTAILMENT" if the hypothesis is explicitly supported or logically follows from the contract.
                "CONTRADICTION" if the hypothesis directly or logically conflicts with the contract's content.
                “NEUTRAL” if there is insufficient information to determine whether it is CONTRADICTION or ENTAILMENT or if the hypothesis is not mentioned in the contract.
                
            """

            userContext = """
            The problem is categorized as a Natural Language Inference (NLI) task for contract analysis. 
            The answer can be one of the following:
                **ENTAILMENT**:
                - The hypothesis is logically true based on the content of the contract.
                - It is **explicitly stated** or can be directly inferred.

                **CONTRADICTION**:
                - The hypothesis **directly** or **logically** conflicts with the contract's content.

                **NEUTRAL**:
                - There is insufficient information to conclude if it is CONTRADICTION or ENTAILMENT.
                - If the hypothesis isn't mentioned in the contract or is unrelated.
            """

            import hashlib
            def generate_id(text):
                return hashlib.md5(text.encode()).hexdigest()  # Creates a hash ID

            # Generate an ID for the document
            document_id = generate_id(data_point['premise'])
            if self.indexed_documents.get(document_id, None) is None:
                userPrompt = data_point["premise"] # document passed as user prompt for indexing
            else:
                userPrompt = "" # document already indexed
            self.indexed_documents[document_id] = data_point["premise"]


            ######################################################
            systemPrompt = {"userQuery": userQuery, "userContext": userContext, "userInstructions": userInstructions} # user query passed as system prompt
            
            return systemPrompt, userPrompt

        def naive_zero_shot_multi_agent_framework_with_predictions(data_point):
            """
            Generates prompts based on the given data_point using zero shot prompting
            with suggestions from previous model predictions stored in temp.json.

            Args:
                data_point (dict): A dictionary with keys "premise" and "hypothesis".

            Returns:
                tuple: A tuple containing systemPrompt (dict) and userPrompt (str).
            """
            import json
            import os
            
            # Load predictions from temp.json
            try:
                with open(os.path.join(os.getcwd(), "temp.json"), "r") as f:
                    predictions_data = json.load(f)
                
                # Get the most recent prediction set
                latest_result = predictions_data[-1]
                predictions = latest_result["result"]["predictions"]
                
                # Convert prediction to string label
                int_to_str_function = self.get_int_to_str_function()
                
                # Get the index of the current data point in the dataset
                # This requires tracking the current index during inference
                if not hasattr(self, 'current_index'):
                    self.current_index = 0
                
                if self.current_index < len(predictions):
                    prediction_idx = self.current_index
                    self.current_index += 1
                else:
                    prediction_idx = 0  # Default to the first prediction if out of range
                
                prediction_int = predictions[prediction_idx]
                prediction_str = int_to_str_function(prediction_int)
                
                # Include the prediction in the prompt
                userQuery = f"Is the following hypothesis ENTAILMENT, CONTRADICTION, or NEUTRAL according to the content of the contract: <hypothesis>{data_point['hypothesis']}</hypothesis>? Another model predicted: {prediction_str}."
                
                userInstructions = """
                The legal researcher has access to the specific contract and can help you reach a decision. You can ask him questions regarding the contract. He doesn't know what the hypothesis is.
                Give the answer in only one word:
                    "ENTAILMENT" if the hypothesis is explicitly supported or logically follows from the contract.
                    "CONTRADICTION" if the hypothesis directly or logically conflicts with the contract's content.
                    "NEUTRAL" if there is insufficient information to determine whether it is CONTRADICTION or ENTAILMENT or if the hypothesis is not mentioned in the contract.
                    
                Take into account the prediction from another model, but form your own independent judgment based on the contract content.
                """
                
                userContext = f"""
                The problem is categorized as a Natural Language Inference (NLI) task for contract analysis. 
                The answer can be one of the following:
                    **ENTAILMENT**:
                    - The hypothesis is logically true based on the content of the contract.
                    - It is **explicitly stated** or can be directly inferred.

                    **CONTRADICTION**:
                    - The hypothesis **directly** or **logically** conflicts with the contract's content.

                    **NEUTRAL**:
                    - There is insufficient information to conclude if it is CONTRADICTION or ENTAILMENT.
                    - If the hypothesis isn't mentioned in the contract or is unrelated.
                
                Another model has predicted this hypothesis to be: {prediction_str}
                Consider this prediction as a suggestion but verify its accuracy independently.
                """
                
            except Exception as e:
                logger.error(f"Error loading predictions from temp.json: {e}")
                # Fall back to original function if predictions can't be loaded
                return naive_zero_shot_multi_agent_framework(data_point)

            import hashlib
            def generate_id(text):
                return hashlib.md5(text.encode()).hexdigest()  # Creates a hash ID

            # Generate an ID for the document
            document_id = generate_id(data_point['premise'])
            if self.indexed_documents.get(document_id, None) is None:
                userPrompt = data_point["premise"]  # document passed as user prompt for indexing
            else:
                userPrompt = ""  # document already indexed
            self.indexed_documents[document_id] = data_point["premise"]

            ######################################################
            systemPrompt = {"userQuery": userQuery, "userContext": userContext, "userInstructions": userInstructions}  # user query passed as system prompt
            
            return systemPrompt, userPrompt

        def naive_few_shot_isolated_spans_same_hypothesis_multi_agent_framework(data_point):
            """
            Generates prompts based on the given data_point using naive few shot (on the isolated evidence spans and the same hypothesis) prompting technique tailored for the multi-agent framework.

            Args:
                data_point (dict): A dictionary with keys "premise" and "hypothesis".

            Returns:
                tuple: A tuple containing systemPrompt (str) and userPrompt (str).
            """

            # Combine train and validate datasets
            combined_dataset = concatenate_datasets([self.isolated_spans_dataset['train'], self.isolated_spans_dataset['validation']])

            # Filter examples with the same hypothesis
            combined_dataset = [example for example in combined_dataset if example['hypothesis'] == data_point['hypothesis']]

            # Randomly pick three examples for each label
            labels = [0, 1, 2]  
            few_shot_examples = []
            for label in labels:
                label_examples = [example for example in combined_dataset if example['label'] == label]
                if len(label_examples) < 3:
                    few_shot_examples.extend(label_examples)  # Use all available examples
                else:
                    few_shot_examples.extend(random.sample(label_examples, 3))

            int_to_str_function = self.get_int_to_str_function()
            # Format the examples
            few_shot_examples_text = "\n".join(
                [
                    f"Example {i + 1}:\nSpan: \"{example['premise']}\"\nHypothesis: \"{example['hypothesis']}\"\nAnswer: {int_to_str_function(example['label'])}\n"
                    for i, example in enumerate(few_shot_examples)
                ]
            )

            ########################### PROMPTS ########################

            userQuery = "Is the following hypothesis ENTAILMENT, CONTRADICTION, or NEUTRAL according to the content of the contract: <hypothesis>{hypothesis}</hypothesis>?".format(hypothesis=data_point["hypothesis"])

            userInstructions = """
            The legal researcher has access to the specific contract and can help you reach a decision. You can ask him questions regarding the contract. He doesn't know what the hypothesis is.
            Give the answer in only one word:
                "ENTAILMENT" if the hypothesis is explicitly supported or logically follows from the contract.
                "CONTRADICTION" if the hypothesis directly or logically conflicts with the contract's content.
                “NEUTRAL” if there is insufficient information to determine whether it is CONTRADICTION or ENTAILMENT or if the hypothesis is not mentioned in the contract.
                
            """

            userContext = """
            The problem is categorized as a Natural Language Inference (NLI) task for contract analysis. 
            The answer can be one of the following:
                **ENTAILMENT**:
                - The hypothesis is logically true based on the content of the contract.
                - It is **explicitly stated** or can be directly inferred.

                **CONTRADICTION**:
                - The hypothesis **directly** or **logically** conflicts with the contract's content.

                **NEUTRAL**:
                - There is insufficient information to conclude if it is CONTRADICTION or ENTAILMENT.
                - If the hypothesis isn't mentioned in the contract or is unrelated.

            Below are examples from various contracts. Analyze the reasoning behind each example by breaking down why each label (ENTAILMENT, CONTRADICTION, or NEUTRAL) is appropriate based on the given spans and hypotheses. 
            Summarize the insights you derive from these examples into a paragraph, and apply similar logic when determining your final answer to the user’s question.
            ### Examples: 
            {EXAMPLES_TEXT}
            """.format(EXAMPLES_TEXT=few_shot_examples_text)

            import hashlib
            def generate_id(text):
                return hashlib.md5(text.encode()).hexdigest()  # Creates a hash ID

            # Generate an ID for the document
            document_id = generate_id(data_point['premise'])
            if self.indexed_documents.get(document_id, None) is None:
                userPrompt = data_point["premise"] # document passed as user prompt for indexing
            else:
                userPrompt = "" # document already indexed
            self.indexed_documents[document_id] = data_point["premise"]


            ######################################################
            systemPrompt = {"userQuery": userQuery, "userContext": userContext, "userInstructions": userInstructions} # user query passed as system prompt
            
            return systemPrompt, userPrompt
        

        def naive_zero_shot_lightRAG(data_point):
            """
            Generates prompts based on the given data_point using naive zero shot prompting technique tailored for the light rag call.

            Args:
                data_point (dict): A dictionary with keys "premise" and "hypothesis".

            Returns:
                tuple: A tuple containing systemPrompt (str) and userPrompt (str).
            """

            ####################### INDEXING FIRST ########################

            ########################### PROMPTS ########################

            userQuery = "Is the following hypothesis ENTAILMENT, CONTRADICTION, or NEUTRAL according to the content of the contract: <hypothesis>{hypothesis}</hypothesis>?".format(hypothesis=data_point["hypothesis"])

            context = """
            The problem is categorized as a Natural Language Inference (NLI) task for contract analysis. 
            The answer can be one of the following:
                **ENTAILMENT**:
                - The hypothesis is logically true based on the content of the contract.
                - It is **explicitly stated** or can be directly inferred.

                **CONTRADICTION**:
                - The hypothesis **directly** or **logically** conflicts with the contract's content.

                **NEUTRAL**:
                - There is insufficient information to conclude if it is CONTRADICTION or ENTAILMENT.
                - If the hypothesis isn't mentioned in the contract or is unrelated.
            """

            import hashlib
            def generate_id(text):
                return hashlib.md5(text.encode()).hexdigest()  # Creates a hash ID

            # Generate an ID for the document
            document_id = generate_id(data_point['premise'])
            if self.indexed_documents.get(document_id, None) is None:
                userPrompt = data_point["premise"] # document passed as user prompt for indexing
            else:
                userPrompt = "" # document already indexed
            self.indexed_documents[document_id] = data_point["premise"]


            ######################################################
            systemPrompt = f"{userQuery} \n {context}"
            
            return systemPrompt, userPrompt

        def naive_zero_shot_lightRAG_with_predictions(data_point):
            """
            Combines lightRAG with predictions from temp.json file.
            Generates prompts based on the given data_point using naive zero shot prompting technique
            with suggestions from previous model predictions for the lightRAG approach.

            Args:
                data_point (dict): A dictionary with keys "premise" and "hypothesis".

            Returns:
                tuple: A tuple containing systemPrompt (str) and userPrompt (str).
            """
            import json
            import os
            
            # Load predictions from temp.json
            try:
                with open(os.path.join(os.getcwd(), "temp.json"), "r") as f:
                    predictions_data = json.load(f)
                
                # Get the most recent prediction set
                latest_result = predictions_data[-1]
                predictions = latest_result["result"]["predictions"]
                
                # Convert prediction to string label
                int_to_str_function = self.get_int_to_str_function()
                
                # Get the index of the current data point in the dataset
                # This requires tracking the current index during inference
                if not hasattr(self, 'current_index'):
                    self.current_index = 0
                
                if self.current_index < len(predictions):
                    prediction_idx = self.current_index
                    self.current_index += 1
                else:
                    prediction_idx = 0  # Default to the first prediction if out of range
                
                prediction_int = predictions[prediction_idx]
                prediction_str = int_to_str_function(prediction_int).upper()
                
                # Include the prediction in the prompt for lightRAG
                # userQuery = f"Is the following hypothesis ENTAILMENT, CONTRADICTION, or NEUTRAL according to the content of the contract: <hypothesis>{data_point['hypothesis']}</hypothesis>? Another model predicted: {prediction_str}."

                userQuery = f"Is the following hypothesis {prediction_str} according to the content of the contract: <hypothesis>{data_point['hypothesis']}</hypothesis>?"

                context = f"""
                The problem is categorized as a Natural Language Inference (NLI) task for contract analysis. 
                The answer can be one of the following:
                    **ENTAILMENT**:
                    - The hypothesis is logically true based on the content of the contract.
                    - It is **explicitly stated** or can be directly inferred.

                    **CONTRADICTION**:
                    - The hypothesis **directly** or **logically** conflicts with the contract's content.

                    **NEUTRAL**:
                    - There is insufficient information to conclude if it is CONTRADICTION or ENTAILMENT.
                    - If the hypothesis isn't mentioned in the contract or is unrelated.
                    
                If the hypothesis is not {prediction_str}, give what it could be in one word 'ENTAILMENT', 'CONTRADICTION', or 'NEUTRAL'.
                """
                
            except Exception as e:
                logger.error(f"Error loading predictions from temp.json: {e}")
                # Fall back to original lightRAG function if predictions can't be loaded
                return naive_zero_shot_lightRAG(data_point)

            import hashlib
            def generate_id(text):
                return hashlib.md5(text.encode()).hexdigest()  # Creates a hash ID

            # Generate an ID for the document
            document_id = generate_id(data_point['premise'])
            if self.indexed_documents.get(document_id, None) is None:
                userPrompt = data_point["premise"] # document passed as user prompt for indexing
            else:
                userPrompt = "" # document already indexed
            self.indexed_documents[document_id] = data_point["premise"]

            ######################################################
            systemPrompt = f"{userQuery} \n {context}"
            
            return systemPrompt, userPrompt

        def naive_zero_shot_with_hypothesis_summary(data_point):
            """
            Generates prompts based on the given data_point using naive zero shot prompting technique
            with corresponding hypothesis summary as reasoning.

            Args:
                data_point (dict): A dictionary with keys "premise" and "hypothesis".

            Returns:
                tuple: A tuple containing systemPrompt (str) and userPrompt (str).
            """
            import os
            import json

            # Load the hypothesis mapping to get the hypothesis ID
            hypothesis_mapping_path = os.path.join(os.getcwd(), "indices_storage_whole_dataset", "hypothesis_mapping.json")
            try:
                with open(hypothesis_mapping_path, 'r') as f:
                    hypothesis_mapping = json.load(f)
                
                # Find hypothesis ID for the current data point's hypothesis
                hypothesis_id = None
                for hypothesis_text, hypothesis_id_value in hypothesis_mapping.items():
                    if hypothesis_text.strip() == data_point["hypothesis"].strip():
                        hypothesis_id = hypothesis_id_value
                        break
                
                if hypothesis_id is None:
                    logger.warning(f"Hypothesis not found in mapping: {data_point['hypothesis']}")
                    # Fall back to regular naive zero-shot if no mapping found
                    return naive_zero_shot(data_point)
                
                # Load the corresponding hypothesis summary
                summary_path = os.path.join(os.getcwd(), "indices_storage_whole_dataset", f"{hypothesis_id}_summary.md")
                if not os.path.exists(summary_path):
                    logger.warning(f"Summary file not found: {summary_path}")
                    return naive_zero_shot(data_point)
                
                with open(summary_path, 'r') as f:
                    hypothesis_summary = f.read()
                
                # Create prompts with hypothesis summary as reasoning
                systemPrompt = """
                You are a helpful lawyer's assistant tasked with determining whether given hypotheses are entailed, 
                contradicted, or neutral with respect to an NDA contract.

                You will be given a contract and a hypothesis.
                You will also be given a summary of guidelines for this specific hypothesis that you should use in your reasoning.
                """

                userPrompt = f"""
                Contract: ```
                {data_point["premise"]}
                ```

                Hypothesis: ```
                {data_point["hypothesis"]}
                ```

                Guidelines for this hypothesis: ```
                {hypothesis_summary}
                ```
                Based on these guidelines and the content of the contract, determine whether the hypothesis is ENTAILMENT, CONTRADICTION, or NEUTRAL.

                Give the answer in only one word:
                "ENTAILMENT" if the hypothesis is entailed by the contract.
                "CONTRADICTION" if the hypothesis is contradicted by the contract.
                "NEUTRAL" if the hypothesis is neutral to (not referenced by) the contract.
                """

                return systemPrompt, userPrompt
                
            except Exception as e:
                logger.error(f"Error loading hypothesis summary: {e}")
                # Fall back to regular naive zero-shot if error occurs
                return naive_zero_shot(data_point)

        def hypothesis_composable_graph_rag(data_point):
            """
            Generates prompts based on the given data_point using hypothesis graphs from indices_storage_whole_dataset.
            This technique:
            1. Loads indices from disk
            2. Creates hypothesis graphs
            3. Queries the appropriate hypothesis graph for the current hypothesis
            4. Uses retrieved examples to enhance the prompt

            Args:
                data_point (dict): A dictionary with keys "premise" and "hypothesis".

            Returns:
                tuple: A tuple containing systemPrompt (str) and userPrompt (str).
            """
            import os
            import json
            import logging
            
            # Configure logging for this function
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger("hypothesis_composable_graph_rag")
            
            try:
            
                # Create the query string (renamed from query_hypothesis_graph to avoid confusion)
                query_string = f"Is the following hypothesis ENTAILMENT, CONTRADICTION, or NEUTRAL according to the content of the contract: <hypothesis>{data_point['hypothesis']}</hypothesis>?\nThe contract is: {data_point['premise']}"

                # Get the documents from the hypothesis graph by calling the query_hypothesis_graph function
                retrieved_documents = query_hypothesis_graph(query_string, self.hypotheses_graphs[data_point["hypothesis"]])
                
                # Format the retrieved documents into example text
                few_shot_examples_text = ""
                if retrieved_documents:
                    few_shot_examples_text = "\n".join([
                        f"--------\nExample {i+1}:\n{doc}\n--------\n"
                        for i, doc in enumerate(retrieved_documents)
                    ])
                else:
                    logger.warning(f"No documents retrieved for hypothesis: {data_point['hypothesis']}")
                    # Fall back to naive zero-shot if no documents retrieved
                    return naive_zero_shot(data_point)
                
                # Create the prompt with the retrieved examples
                systemPrompt_template = """
                You are an expert legal assistant specializing in Natural Language Inference (NLI) for contract analysis. Your task is to evaluate the logical relationship between a given hypothesis and an NDA contract. This involves determining whether the hypothesis is:

                1. **ENTAILMENT**:
                - The hypothesis is logically true based on the content of the contract.
                - It is explicitly stated or can be directly inferred.

                2. **CONTRADICTION**:
                - The hypothesis directly conflicts with the contract's content.

                3. **NEUTRAL**:
                - The hypothesis is unrelated to the contract, or there is insufficient information to conclude its truth or falsehood.

                The hypothesis you need to evaluate is: 
                Hypothesis: ```
                {HYPOTHESIS}
                ```

                Here are examples of how this specific hypothesis has been evaluated on other contracts and the corresponding reasoning:
                {EXAMPLES_TEXT}

                Use these examples as a guide, but focus on the specific content of the current contract when making your evaluation.
                """

                userPrompt_template = """
                Contract: ```
                {CONTRACT}
                ```

                Hypothesis: ```
                {HYPOTHESIS}
                ```

                Give the answer in only one word:
                "ENTAILMENT" if the hypothesis is explicitly supported or logically follows from the contract.
                "CONTRADICTION" if the hypothesis directly conflicts with the contract's content.
                "NEUTRAL" if the hypothesis is unrelated to or not inferable from the contract.
                """

                systemPrompt = systemPrompt_template.format(
                    HYPOTHESIS=data_point["hypothesis"],
                    EXAMPLES_TEXT=few_shot_examples_text if few_shot_examples_text else "No examples available for this specific hypothesis."
                )
                
                userPrompt = userPrompt_template.format(
                    CONTRACT=data_point["premise"],
                    HYPOTHESIS=data_point["hypothesis"]
                )
                
                return systemPrompt, userPrompt
                
            except Exception as e:
                logger.error(f"Error in hypothesis_composable_graph_rag: {e}")
                # Fall back to naive zero-shot if any errors occur
                return naive_zero_shot(data_point)

        if self.prompting_technique == 'naive zero-shot':
            return naive_zero_shot
        if self.prompting_technique == 'optimized zero-shot':
            return optimized_zero_shot
        if self.prompting_technique == 'naive few-shot':
            return naive_few_shot
        if self.prompting_technique == 'naive few-shot isolated spans':
            return naive_few_shot_isolated_spans
        if self.prompting_technique == 'naive_few_shot_isolated_spans_same_hypothesis':
            return naive_few_shot_isolated_spans_same_hypothesis
        if self.prompting_technique == 'naive_few_shot_isolated_spans_same_hypothesis_chainOfThought':
            return naive_few_shot_isolated_spans_same_hypothesis_chainOfThought
        if self.prompting_technique == 'naive_zero_shot_in_document_rag_naive_chunking':
            return naive_zero_shot_in_document_rag_naive_chunking
        if self.prompting_technique == 'naive_zero_shot_multi_agent_framework':
            return naive_zero_shot_multi_agent_framework
        if self.prompting_technique == 'naive_zero_shot_multi_agent_framework_with_predictions':
            return naive_zero_shot_multi_agent_framework_with_predictions
        if self.prompting_technique == 'naive_few_shot_isolated_spans_same_hypothesis_multi_agent_framework':
            return naive_few_shot_isolated_spans_same_hypothesis_multi_agent_framework
        if self.prompting_technique == 'naive_zero_shot_lightRAG':
            return naive_zero_shot_lightRAG
        if self.prompting_technique == 'naive_zero_shot_lightRAG_with_predictions':
            return naive_zero_shot_lightRAG_with_predictions
        if self.prompting_technique == 'naive_zero_shot_with_hypothesis_summary':
            return naive_zero_shot_with_hypothesis_summary
        if self.prompting_technique == 'hypothesis_composable_graph_rag':
            return hypothesis_composable_graph_rag

# Example usage:

# Instantiate the class
# dataset_handler = ContractNLIDataset()

# Describe the dataset
# dataset_handler.describe_dataset()

# Analyze class distribution
# dataset_handler.analyze_class_distribution()