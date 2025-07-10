  // Define criteria tabs with exact column name mapping and instructions
  export const criteria = [
    { 
      id: 'explainability', 
      label: 'Explainability and Reasoning',
      column: 'Which response demonstrates better "Explainability and Reasoning"?',
      instruction: 'Evaluate whether the report clearly and transparently explains not only the final conclusion, but also the reasoning process and supporting evidence in a step-by-step, understandable manner. The explanation should guide the reader through the logic in a way that supports comprehension, avoiding unexplained jumps in logic.'
    },
    { 
      id: 'justification', 
      label: 'Justification with Evidence',
      column: 'Which response demonstrates better "Justification with Evidence"?',
      instruction: 'Determine whether the statements and claims are explicitly justified with relevant, specific, and clearly cited evidence (e.g., direct quotations, clause references). The justification should be traceable, allowing the reader to locate the original source material.'
    },
    { 
      id: 'contextual', 
      label: 'Contextual and Legal Understanding',
      column: 'Which response demonstrates better "Contextual and Legal Understanding"?',
      instruction: 'Assess whether the report demonstrates a deep and accurate understanding of the document, its legal terminology, and the broader context. Consider whether it correctly interprets clauses and captures implied assumptions or legal concerns behind the question.'
    },
    { 
      id: 'ambiguity', 
      label: 'Handling Ambiguity',
      column: 'Which response demonstrates better "Handling Ambiguity"?',
      instruction: 'Determine whether the report identifies and handles ambiguities in the source material appropriately, such as by presenting multiple interpretations or justifying a chosen one clearly.'
    },
    { 
      id: 'knowledge', 
      label: 'Acknowledgment of Knowledge Gaps',
      column: 'Which response demonstrates better "Acknowledgment of Knowledge Gaps"?',
      instruction: 'Evaluate whether the report explicitly acknowledges when available information is insufficient to support a conclusion, avoiding speculation or overconfidence.'
    },
    { 
      id: 'conciseness', 
      label: 'Conciseness and Precision',
      column: 'Which response demonstrates better "Conciseness and Precision"?',
      instruction: 'Assess whether the report communicates clearly and efficiently, avoiding unnecessary repetition or verbosity, while still covering all key points.'
    },
    { 
      id: 'coherence', 
      label: 'Coherence and Organization',
      column: 'Which response demonstrates better "Coherence and Organization"?',
      instruction: 'Check whether the report is logically structured, flows smoothly, and maintains clarity across sections. Transitions between ideas should be natural and helpful.'
    },
    { 
      id: 'relevance', 
      label: 'Relevance and Focus',
      column: 'Which response demonstrates better "Relevance and Focus"?',
      instruction: 'Evaluate whether the report stays on topic and maintains focus on answering the core question, avoiding tangents or irrelevant content.'
    },
    { 
      id: 'completeness', 
      label: 'Completeness',
      column: 'Which response demonstrates better "Completeness"?',
      instruction: 'Assess whether the report addresses all important aspects of the question and offers a contextually broad and holistic answer. It should not omit any major points or perspectives.'
    }
  ];