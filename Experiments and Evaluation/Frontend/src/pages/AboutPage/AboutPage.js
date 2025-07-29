import React from 'react';
import { useNavigate } from 'react-router-dom';

import './AboutPage.css';

const AboutPakton = () => {
  const navigate = useNavigate();
  
  // Add evaluation criteria for G-EVAL section
  const evaluationCriteria = [
    "Explainability and Reasoning",
    "Justification with Evidence",
    "Handling Ambiguity",
    "Acknowledgment of Knowledge Gaps",
    "Contextual and Legal Understanding",
    "Completeness",
    "Conciseness and Precision",
    "Relevance and Focus",
    "Coherence and Structure"
  ];
  
  return (
    <div className="about-pakton">
      <div className="hero-section">
        <div className="top-button-container">
            <button onClick={() => navigate('/')} className="back-button">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
            </svg>
            Back to Home
            </button>
        </div>
        <h1>PAKTON Framework</h1>
        <p className="subtitle">
          A Multi-Agent Solution for Contract Document Analysis
        </p>
      </div>

      <div className="details-container">
        <div className="details-card">
          <div className="card-header">
            <h2>What is PAKTON?</h2>
          </div>
          <div className="card-body">
            <p>
              PAKTON is a multi-agent framework designed to analyze contract documents and provide explainable, legally grounded answers to user queries. The name comes from the ancient Greek word for agreement or contract, related to the Latin "pactum," as in the phrase "pacta sunt servanda" — agreements must be kept.
            </p>
            
            <h3>The Problem We're Solving</h3>
            <p>
              Reviewing contract documents is a time-consuming process that often requires expert legal knowledge, making it inaccessible to the general public. Research shows that organizations lose an average of 9.2% of their annual revenue due to contract mismanagement, with that figure rising to 15% for larger enterprises. A typical Fortune 1000 company manages between 20,000 and 40,000 active contracts at any given time, and even simple agreements can take over a week to approve.
            </p>
            
            <p>
              Contract documents exhibit several peculiarities that require specialized handling:
            </p>
            <ul className="challenges-list">
              <li>Complex legal terminology requiring domain-specific language understanding</li>
              <li>Overlapping or contradictory clauses that need robust retrieval and conflict resolution</li>
              <li>Exceptions and references to different parts of the document</li>
              <li>Ambiguous phrasing and multiple interpretations requiring careful contextual analysis</li>
              <li>Legal differences across jurisdictions requiring consultation with external legal databases</li>
            </ul>
            
            <p>
              PAKTON addresses these challenges through teamwork among agents and effective use of external knowledge, grounding its responses in the contract and relevant external sources while offering justifications for its conclusions.
            </p>
          </div>
        </div>

        <div className="details-card">
          <div className="card-header">
            <h2>❓ But, Why PAKTON?</h2>
          </div>
          <div className="card-body">
            <h3>Proven Performance</h3>
            <ul className="performance-list">
              <li><strong>Superior Generation Quality:</strong> Outperforms baseline methods on the ContractNLI dataset</li>
              <li><strong>State-of-the-Art Retrieval:</strong> RAG component (Researcher) leads performance on LegalBenchRAG benchmark</li>
              <li><strong>Human-Preferred:</strong> Chosen by human evaluators over ChatGPT for contract analysis—especially for <strong>Explainability</strong> and <strong>Completeness</strong></li>
              <li><strong>LLM Validation:</strong> GEVAL evaluations show consistent preference for PAKTON over GPT-4o</li>
            </ul>

            <h3>Robust, Open, and Adaptable</h3>
            <ul className="adaptability-list">
              <li><strong>Privacy-First:</strong> Fully open-source with on-premise deployment capabilities</li>
              <li><strong>Robust:</strong> According to our robustness analysis, it bridges performance gaps between small and large LLMs, enabling smaller open-source models to rival larger proprietary ones</li>
              <li><strong>Plug-and-Play:</strong> Modular architecture for seamless extension and custom workflow integration</li>
              <li><strong>Transparent Design:</strong> Explainable outputs that contrast with typical black-box AI models</li>
            </ul>
          </div>
        </div>

        <div className="details-card">
          <div className="card-header">
            <h2>Framework Architecture</h2>
          </div>
          <div className="card-body">
            <p>
              The PAKTON framework consists of three specialized agents that collaborate with one another. Each agent plays a distinct role in the reasoning and information retrieval process, contributing to a more accurate, explainable, and well-supported response.
            </p>
            
            <div className="architecture-image-container">
              <img 
                src={`${process.env.PUBLIC_URL}/PAKTON_architecture.png`}
                alt="PAKTON Framework Architecture showing the three agents: Archivist, Interrogator, and Researcher with their interactions and components" 
                className="architecture-image"
              />
              <p className="architecture-caption">PAKTON Architecture Diagram</p>
            </div>
            
            <div className="agent-cards">
              <div className="agent-card">
                <h3>The Archivist</h3>
                <p>
                  Responsible for gathering and organizing relevant information from the user. The Archivist collects the user's query, any accompanying instructions, and contextual background. This information is then structured and passed to the Interrogator agent.
                </p>
                <h4>Key Capabilities:</h4>
                <ul>
                  <li>Information extraction from user queries</li>
                  <li>Document parsing (text, DOCX, PDF via OCR)</li>
                  <li>Graph representation of contract structure</li>
                  <li>Creation of contextual embeddings for retrieval</li>
                </ul>
              </div>
              
              <div className="agent-card">
                <h3>The Researcher</h3>
                <p>
                  Responsible for retrieving relevant information to support the Interrogator in answering the user's query. The Researcher is equipped with multiple retrieval methods and autonomously selects the most suitable approach based on the query.
                </p>
                <h4>Retrieval Tools:</h4>
                <ul>
                  <li>Web search</li>
                  <li>Wikipedia search</li>
                  <li>In-document and cross-document search (hybrid retrieval)</li>
                  <li>SQL-based retrieval for structured data</li>
                  <li>External legal database integration</li>
                </ul>
              </div>
              
              <div className="agent-card">
                <h3>The Interrogator</h3>
                <p>
                  Coordinates the multi-step reasoning process required to answer user queries with confidence and accuracy. The Interrogator takes the user's query and initiates an iterative questioning of the Researcher agent to refine and deepen the system's understanding.
                </p>
                <h4>Process:</h4>
                <ul>
                  <li>Decomposing the original query into targeted questions</li>
                  <li>Generating preliminary reports and identifying knowledge gaps</li>
                  <li>Formulating follow-up questions to address uncertainties</li>
                  <li>Incrementally refining the final response</li>
                  <li>Validating the structure and quality of the final report</li>
                </ul>
              </div>
            </div>
            
            <h3>Advanced Technical Features</h3>
            
            <div className="feature-cards">
              <div className="feature-card">
                <h4>Graph Representation & Contextual Embeddings</h4>
                <p>
                  PAKTON transforms parsed contract content into a graph that captures the hierarchical organization of the document. This structure allows for more efficient and meaningful text chunking and embedding, with three types of chunks generated:
                </p>
                <ul>
                  <li><strong>Node-level chunks:</strong> Individual sections for precise matching</li>
                  <li><strong>Ancestor-aware chunks:</strong> Sections with their parent context</li>
                  <li><strong>Descendant-aware chunks:</strong> Sections with their nested content</li>
                </ul>
              </div>
              
              <div className="feature-card">
                <h4>Two-Step Retrieval Process</h4>
                <p>
                  To ensure both high recall and precision, the Researcher employs a two-step retrieval and reranking process:
                </p>
                <ul>
                  <li>Initial high-recall retrievers collect potentially relevant passages</li>
                  <li>Cross-encoder model reranks results by jointly encoding query and passage</li>
                  <li>Normalized relevance scores determine final passage selection</li>
                </ul>
              </div>
              
              <div className="feature-card">
                <h4>Structured Legal Report Output</h4>
                <p>
                  The final output is presented as a comprehensive legal report including:
                </p>
                <ul>
                  <li>Title and concise topic summary</li>
                  <li>Legal reasoning and key findings</li>
                  <li>Preliminary answer and direction for further research</li>
                  <li>Identified knowledge gaps</li>
                  <li>List of supporting sources with citations</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div className="details-card">
          <div className="card-header">
            <h2>Key Advantages</h2>
          </div>
          <div className="card-body">
            <div className="advantages-grid">
              <div className="advantage-item">
                <h4>Explainability and Reasoning</h4>
                <p>
                  Unlike end-to-end black-box models, PAKTON emphasizes transparency, progressive refinement, and grounded justifications. It clearly explains the reasoning process in a step-by-step, understandable manner.
                </p>
              </div>
              
              <div className="advantage-item">
                <h4>Justification with Evidence</h4>
                <p>
                  PAKTON grounds its responses in the contract and relevant external sources, offering explicit justifications for its conclusions with citations to both contract clauses and external sources.
                </p>
              </div>
              
              <div className="advantage-item">
                <h4>Handling Ambiguity</h4>
                <p>
                  In the legal domain, answers are rarely binary, ambiguity is common, and interpretation frequently involves subjective judgment. PAKTON identifies and handles ambiguities appropriately by presenting multiple interpretations or justifying a chosen one clearly.
                </p>
              </div>
              
              <div className="advantage-item">
                <h4>Acknowledgment of Knowledge Gaps</h4>
                <p>
                  When the available information is insufficient to reach a confident decision, PAKTON explicitly acknowledges knowledge gaps, promoting informed uncertainty rather than unsupported answers.
                </p>
              </div>
              
              <div className="advantage-item">
                <h4>Contextual and Legal Understanding</h4>
                <p>
                  The system demonstrates deep understanding of legal terminology and the broader context of contracts, correctly interpreting clauses and capturing implied assumptions or legal concerns.
                </p>
              </div>
              
              <div className="advantage-item">
                <h4>Completeness</h4>
                <p>
                  PAKTON addresses all important aspects of a query and offers contextually broad and holistic answers, considering questions from multiple angles and offering comprehensive perspectives.
                </p>
              </div>
            </div>
            
            <div className="info-box">
              <div className="info-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="16" x2="12" y2="12"></line>
                  <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
              </div>
              <div className="info-content">
                <p>
                  Experiments across multiple contract analysis tasks show that our framework outperforms general-purpose models not only in accuracy, but also in explainability and reasoning, both of which are critical for decision-making in the presence of legal uncertainty.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* New Experiments Card */}
        <div className="details-card">
          <div className="card-header">
            <h2>Experimental Evaluation</h2>
          </div>
          <div className="card-body">
            <p>
              PAKTON is designed as a general-purpose framework for contract analysis rather than specializing in specific subtasks. We evaluate its performance across multiple representative contract analysis subtasks to assess its overall quality and versatility.
            </p>
            
            <h3>Generalization vs. Specialization</h3>
            <p>
              Unlike existing approaches that are fine-tuned specifically for individual subtasks, PAKTON is not fine-tuned on any particular task. As a result, while it may not consistently outperform specialized models on their respective subtasks, it demonstrates strong generalization across all tasks.
            </p>
            
            <div className="experiment-highlights">
              <div className="highlight-item">
                <h4>Performance</h4>
                <p>
                  PAKTON outperforms general-purpose baselines and achieves competitive performance compared to task-specific fine-tuned systems, highlighting its versatility and robustness across diverse contract-related tasks.
                </p>
              </div>
              
              <div className="highlight-item">
                <h4>Real-world Application</h4>
                <p>
                  In practice, contract analysis problems rarely align perfectly with predefined subtasks. Fine-tuned models often fail to generalize beyond their narrow training scope, while PAKTON's general framework maintains strong performance across diverse settings.
                </p>
              </div>
              
              <div className="highlight-item">
                <h4>Adaptability</h4>
                <p>
                  As a general framework not tied to any specific subtask, PAKTON can be more readily adapted to a variety of contract-related tasks while maintaining consistent performance levels across different use cases.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* ContractNLI Card */}
        <div className="details-card">
          <div className="card-header">
            <h2>ContractNLI Experiments</h2>
          </div>
          <div className="card-body">
            <div className="overview-container">
              <h3>Natural Language Inference in Legal Contracts</h3>
              <p>
                We evaluated PAKTON on the ContractNLI dataset to assess its performance in natural language inference tasks 
                within legal contract documents. The task involves determining whether a given statement is entailed by, 
                contradicted by, or neutral with respect to a contract document.
              </p>
              
              <h3>Key Findings</h3>
              <ul className="criteria-list">
                <li><strong>Superior Performance:</strong> PAKTON consistently outperforms baseline methods across all models, including domain-specific fine-tuned models like Saul and matches or surpasses proprietary models like GPT-4o</li>
                <li><strong>Model Robustness:</strong> Achieves remarkably low performance variation (CV of 12.6%) across different LLMs compared to baseline approaches (CV &gt;25%)</li>
                <li><strong>Performance Stability:</strong> Reduces the gap between different LLMs while maintaining high accuracy, with only 3.8 percentage points difference between models (compared to 22.83% in baseline)</li>
                <li><strong>Open-Source Advantage:</strong> Demonstrates that open-source models with PAKTON can match or exceed the performance of proprietary models, enabling secure processing of sensitive legal information</li>
                <li><strong>Statistical Validation:</strong> Confirmed robustness through rigorous statistical analysis, including ANOVA (F-statistic = 3.05, p=0.12) and regression analysis (slope = 0.44)</li>
              </ul>
            </div>
          </div>
        </div>

        {/* LegalBenchRAG Card */}
        <div className="details-card">
          <div className="card-header">
            <h2>LegalBenchRAG Experiments</h2>
          </div>
          <div className="card-body">
            <div className="overview-container">
              <h3>Retrieval Performance Evaluation</h3>
              <p>
                LegalBenchRAG is a comprehensive benchmark designed to evaluate retrieval-augmented generation systems in the legal domain. 
                We assessed PAKTON's retrieval capabilities across four legal domains: NDAs, M&A agreements, commercial contracts, 
                and consumer-facing privacy policies, focusing on the performance of our Archivist (indexing) and Researcher (retrieval) modules.
              </p>
              
              <h3>Key Findings</h3>
              <ul className="criteria-list">
                <li><strong>Superior Recall Performance:</strong> PAKTON achieves over 5× improvement in Recall@1 (26.77% vs. 4.94%) compared to the strongest baseline</li>
                <li><strong>Enhanced Precision:</strong> More than 3× improvement in Precision@1 (22.34% vs. 6.41%) over baseline methods</li>
                <li><strong>Consistent Performance:</strong> Demonstrates superior performance across all legal document types in the benchmark</li>
                <li><strong>Scalable Retrieval:</strong> Maintains high performance across different k values, showing robust retrieval at various thresholds</li>
                <li><strong>Architecture Effectiveness:</strong> The combination of structural parsing, hybrid retrieval (BM25 + dense embeddings), and sophisticated reranking proves highly effective for legal text retrieval</li>
              </ul>
              
              <div className="info-box">
                <div className="info-content">
                  <p>
                    These results validate PAKTON's retrieval architecture and demonstrate that our multi-agent approach 
                    significantly outperforms traditional retrieval methods in legal document analysis, achieving both 
                    higher precision and recall across multiple legal domains.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* New G-EVAL Card */}
        <div className="details-card">
          <div className="card-header">
            <h2>G-EVAL Assessment</h2>
          </div>
          <div className="card-body">
            <div className="overview-container">
              <h3>Evaluation Design</h3>
              <p>
                G-EVAL has emerged as a widely adopted evaluation framework grounded in the LLM-as-a-Judge paradigm, 
                which leverages large language models to assess the quality of natural language generation (NLG) 
                outputs across multiple dimensions. In this work, we used the publicly available G-EVAL implementation and defined nine evaluation criteria:
              </p>
              <ul className="criteria-list">
                {evaluationCriteria.map((criterion, index) => (
                  <li key={index}>{criterion}</li>
                ))}
              </ul>
              <p>
                The evaluation was conducted on 102 samples randomly drawn from the ContractNLI dataset. 
                Both PAKTON and GPT-4o were evaluated on identical inputs, and the framework produced criterion-specific 
                scores for each response, enabling a more nuanced analysis of model behavior beyond accuracy, particularly 
                in terms of response quality, explainability, and reasoning.
              </p>

              <h3>Configuration</h3>
              <p>
                As part of our evaluation design, we ensured fair model comparison settings. For ChatGPT, we implemented 
                an embedding-based (RAG) pipeline. For PAKTON, we limited tool usage to strictly in-document retrieval 
                (disabling access to external tools like web search), and capped the number of interrogation turns at five. 
                GPT-4o served as the underlying model for both systems to eliminate base model performance discrepancies 
                and isolate differences due to architecture and orchestration.
              </p>
              <p>
                We set the temperature to 0 to ensure deterministic responses, facilitating reproducibility.
              </p>
            </div>
            
            <div className="results-container">
              <h3>Results</h3>
              <p>
                Aggregating the results across all samples and criteria, PAKTON outperforms GPT-4o in the majority of 
                dimensions. Notably, it achieves higher scores in Explainability and Reasoning, Justification with Evidence, 
                Completeness, and Handling Ambiguity. These results align with PAKTON's design goals, which emphasize 
                detailed, well-supported responses that explicitly reason about legal content.
              </p>
              <p>
                For criteria like Conciseness and Precision and Relevance and Focus, both models exhibit comparable 
                performance. This outcome is expected, as these dimensions are often conflicted with completeness, 
                where PAKTON significantly outperforms GPT-4o, highlighting a trade-off between brevity and depth.
              </p>
              <p>
                The only criterion in which PAKTON underperforms relative to GPT-4o is Contextual and Legal Understanding. 
                While this initially appeared counterintuitive, closer inspection of the rationale generated by G-EVAL 
                revealed that PAKTON's responses often explicitly acknowledge knowledge gaps when uncertain. Although 
                this behavior is desirable from a transparency standpoint, the framework interpreted these acknowledgments 
                as evidence of limited understanding, thus assigning lower scores.
              </p>
            </div>
          </div>
        </div>

        <div className="details-card">
          <div className="card-header">
            <h2>Human Evaluation Results</h2>
          </div>
          <div className="card-body">
            <p>
              To evaluate the practical effectiveness of PAKTON, we conducted a human evaluation centered around a real-world legal use case, comparing PAKTON's performance against ChatGPT when answering questions about the EU AI Act.
            </p>
            
            <h3>Key Findings</h3>
            <p>
              Based on the survey results, PAKTON was preferred over ChatGPT in the majority of evaluation criteria. This trend was consistent across all the legal questions presented to participants.
            </p>
            
            <div className="findings-details">
              <h4>Strongest Advantages</h4>
              <p>
                The biggest difference was seen in the "Completeness" criterion. PAKTON tended to give more well-rounded answers, considering the question from multiple angles and offering a broader perspective. It also performed better in "Explainability and Reasoning," which is especially important for users without legal training, as it explained its logic more clearly and step-by-step.
              </p>
              
              <h4>Trade-offs Observed</h4>
              <p>
                As expected, PAKTON was preferred for completeness, while ChatGPT was chosen more often for conciseness. A similar pattern appeared in the "Relevance and Focus" criterion, where both models received similar scores, likely due to the balance between including more perspectives and staying tightly focused.
              </p>
              
              <p>
                Overall, these results align with PAKTON's design, which aims to give detailed, report-like responses. In this context, the trade-off between completeness and brevity seems acceptable and expected.
              </p>
            </div>
          </div>
        </div>

        <div className="details-card">
          <div className="card-header">
            <h2>Limitations & Future Directions</h2>
          </div>
          <div className="card-body">
            <h3>Current Limitations</h3>
            
            <div className="limitations-grid">
              <div className="limitation-item">
                <h4>Language Scope</h4>
                <p>
                  The system has been tested only on English-language contracts. Additional adaptation and evaluation would be necessary for multilingual or cross-lingual applications.
                </p>
              </div>
              
              <div className="limitation-item">
                <h4>Contract & Jurisdiction Coverage</h4>
                <p>
                  PAKTON has been evaluated on a subset of contract types and does not currently cover the full diversity of legal documents or different legal jurisdictions.
                </p>
              </div>
              
              <div className="limitation-item">
                <h4>Latency & Cost</h4>
                <p>
                  The system prioritizes multi-step reasoning over speed, resulting in longer response times compared to general-purpose language models, particularly due to the iterative communication between agents.
                </p>
              </div>
              
              <div className="limitation-item">
                <h4>Explainability vs. Efficiency</h4>
                <p>
                  The emphasis on explainability can sometimes result in longer or less concise responses, occasionally sacrificing brevity for clarity and justification.
                </p>
              </div>
            </div>
            
            <div className="ethics-note">
              <h3>Ethical Considerations</h3>
              <p>
                PAKTON is developed to aid in contract analysis and increase access to legal information, but it does not serve as a substitute for qualified legal advice. There is a risk that users, particularly non-experts, may over-rely on its outputs without proper legal verification. 
              </p>
              <p>
                <strong>PAKTON should be viewed as an assistive tool, not a definitive authority on legal interpretation.</strong>
              </p>
            </div>
          </div>
        </div>

        <div className="details-card">
          <div className="card-header">
            <h2>Try PAKTON</h2>
          </div>
          <div className="card-body">
            <div className="try-pakton-container">
              <p>
                PAKTON aims to help democratize contract understanding by providing explainable, user-friendly outputs that can assist individuals without legal backgrounds. We're working to offer free access to a publicly deployed version of the system, to the extent that it remains practically and financially feasible.
              </p>
              
              <div className="button-container">
              <button
                className="demo-button"
                onClick={() => window.open("https://pakton.site/", "_blank")}
                >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                >
                    <polyline points="9 18 15 12 9 6"></polyline>
                </svg>
                Try the Demo
                </button>
                
                <button className="github-button" onClick={() => window.open('https://github.com/petrosrapto/PAKTON', '_blank')}>
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
                  </svg>
                  View on GitHub
                </button>
                
                <button 
                  className="paper-button"
                  onClick={() => window.open("https://arxiv.org/abs/2506.00608", "_blank")}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M7 3h10a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2zm0 2v14h10V5H7zm2 2h6v1H9V7zm0 2h6v1H9V9zm0 2h6v1H9v-1zm0 2h4v1H9v-1z"/>
                  </svg>
                  Read the Paper
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="details-card">
          <div className="card-body">
            <div className="author-container">
              <div className="author-profile">
                <div className="author-details">
                  <div className="name-title-group">
                    <h3>Raptopoulos Petros</h3>
                    <p className="author-title">AI Software Engineer</p>
                  </div>
                  <p className="author-email">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                      <polyline points="22,6 12,13 2,6"></polyline>
                    </svg>
                    petrosrapto@gmail.com
                  </p>
                </div>
                
                <div className="author-links">
                  <a 
                    href="https://www.linkedin.com/in/petrosrapto/" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="social-link linkedin-link"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
                      <rect x="2" y="9" width="4" height="12"></rect>
                      <circle cx="4" cy="4" r="2"></circle>
                    </svg>
                    LinkedIn Profile
                  </a>
                  
                  <a 
                    href="https://github.com/petrosrapto" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="social-link github-link"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
                    </svg>
                    GitHub Profile
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="footer">
        <p>© 2025 PAKTON - A Multi-Agent Framework for Contract Document Analysis</p>
      </div>
    </div>
  );
};

export default AboutPakton;