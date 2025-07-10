# Human Evaluation of PAKTON vs. ChatGPT (4o) + (RAG)

## Overview

This directory contains the data and results from a comprehensive human evaluation study comparing two AI systems:
- **PAKTON**: A specialized legal AI system developed for analyzing legal documents
- **ChatGPT (4o)**: OpenAI's GPT-4o model (Enterprise, RAG)

The evaluation focuses specifically on each system's ability to analyze and explain aspects of the EU AI Act and related regulatory frameworks. Human evaluators were presented with responses from both systems and asked to compare them across multiple dimensions of quality.

These experiments are addressed at Section 4.2 Qualitative Results of the paper and details can be found at Appendix D Human Evaluation.

The frontend for these experiments is available at https://pakton.site/evaluation/human-evaluation

### Evaluation Criteria

Evaluators rated system responses across nine dimensions of quality:

1. **Explainability and Reasoning**: How well the system explains its logic and reasoning process
2. **Justification with Evidence**: How effectively the system supports claims with evidence from source documents
3. **Contextual and Legal Understanding**: How accurately the system interprets legal concepts and demonstrates contextual awareness
4. **Handling Ambiguity**: How well the system acknowledges and addresses ambiguous aspects of the question or source materials
5. **Acknowledgment of Knowledge Gaps**: Whether the system appropriately recognizes limitations in available information
6. **Conciseness and Precision**: How efficiently and precisely the system communicates information
7. **Coherence and Organization**: How logically structured and easy to follow the response is
8. **Relevance and Focus**: How well the response stays on topic and addresses the core question
9. **Completeness**: Whether the response covers all important aspects of the question

## Evaluation Questions

The evaluation covered six key areas related to the EU AI Act:

1. **Scope**: Understanding the scope and applicability of the EU AI Act
2. **Risk Articles**: Identifying and explaining articles governing high-risk AI systems
3. **Obligations**: Explaining provider obligations for general-purpose AI models
4. **Emotions**: Analyzing regulation of emotion recognition systems
5. **Complaints**: Understanding the right to lodge complaints under the EU AI Act
6. **AI Definition**: Explaining the legal definition of AI systems in the regulatory context

Each area was evaluated with the same nine quality dimensions, resulting in a comprehensive assessment matrix.

## Data Files

This directory contains:

- `Human Evaluation/`: Raw evaluation data collected from participants
  - `ScopeQuestion.csv`: Evaluations of scope-related responses
  - `RiskArticlesQuestion.csv`: Evaluations of high-risk AI article responses
  - `ObligationsQuestion.csv`: Evaluations of obligation-related responses
  - `EmotionsQuestion.csv`: Evaluations of emotion recognition regulation responses
  - `ComplaintsQuestion.csv`: Evaluations of complaint mechanism responses
  - `AIdefinitionQuestion.csv`: Evaluations of AI definition responses
  - `human_aggregated_votes.json`: Aggregated results across all evaluations