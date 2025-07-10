import React from 'react';
import './ExperimentDetails.css';

import { useParams, useNavigate } from 'react-router-dom';

const ExperimentDetails = () => {
  const navigate = useNavigate();
  return (
    <div className="experiment-details">
      <div className="hero-section">
        <div className="top-button-container">
            <button onClick={() => navigate('/human-evaluation')} className="back-button">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
            </svg>
            Back to Dashboard
            </button>
        </div>
        <h1>Experiment Setup & Details</h1>
        <p className="subtitle">
          Technical information about the human evaluation experiment
        </p>
      </div>

      <div className="details-container">
        <div className="details-card">
          <div className="card-header">
            <h2>Experiment Background</h2>
          </div>
          <div className="card-body">
            <p>
              To evaluate the practical effectiveness of PAKTON, we conducted a human evaluation centered around a real-world legal use case. The evaluation was designed to compare PAKTON's performance against ChatGPT when answering questions about EU legislation.
            </p>
            
            <h3>Origin of the Evaluation</h3>
            <p>
              We first participated in the <a href="https://archimedesai.gr/en/events/388-athens-legal-ai-hackathon-2025-1" target="_blank" className="citation-link">Athens Legal AI Hackathon 2025</a>, where we adapted PAKTON to answer user questions about the <a href="https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202401689" target="_blank" className="citation-link">EU AI Act</a>. 
            </p>
            
            <p>
              Following the hackathon, we received encouraging qualitative feedback on PAKTON's output, motivating us to conduct a more structured and comparative evaluation against a widely-used baseline.
            </p>

          </div>
        </div>

        <div className="details-card">
          <div className="card-header">
            <h2>Evaluation Methodology</h2>
          </div>
          <div className="card-body">
            <h3>Survey Platform</h3>
            <p>
              We deployed a survey on <span className="platform-name">Prolific</span>, an online research platform widely used in academic studies. Prolific ensures participant anonymity and does not allow researchers to interfere with or influence responses, maintaining the integrity of the evaluation.
            </p>
            
            <h3>Participant Selection</h3>
            <p>
              We intentionally did not restrict participation to legal professionals. Our goal was to understand how well PAKTON's responses are received by the general public, especially in comparison to a widely used baseline like ChatGPT.
            </p>
            
            <p>
              The only eligibility requirements were:
            </p>
            <ul className="requirements-list">
              <li>Fluency in English</li>
              <li>Completion of at least compulsory education (e.g., high school level)</li>
            </ul>
            
            <p className="eligibility-note">
              These minimal requirements ensured participants had basic reading comprehension and critical reasoning skills necessary for the evaluation task.
            </p>

            <h3>Evaluation Design</h3>
            <p>
              Each participant was presented with paired outputs (PAKTON vs. ChatGPT) for the same legal query. Participants were asked to evaluate which response better satisfied each of nine specific criteria.
            </p>
            
            <h3>Response Format</h3>
            <p>
              For each criterion, participants were required to:
            </p>
            <ul className="response-format-list">
              <li>Vote for the response (either PAKTON or ChatGPT) that better aligned with the criterion</li>
              <li>Provide a brief justification, articulating the rationale behind their choice</li>
              <li>Select "None" or "Not Sure" options for cases where they felt unable to confidently choose</li>
            </ul>
            
            <p className="methodology-note">
              This requirement for written justifications and the inclusion of neutral options helped reduce noise and encouraged careful evaluation.
            </p>
          </div>
        </div>

        <div className="details-card">
          <div className="card-header">
            <h2>Evaluation Criteria</h2>
          </div>
          <div className="card-body">
            <p className="criteria-intro">
              Participants evaluated the responses based on nine distinct criteria, each designed to assess different aspects of AI-generated legal explanations:
            </p>
            
            <div className="criteria-grid">
              <div className="criterion-item">
                <h4>Explainability and Reasoning</h4>
                <p>Whether the answer clearly explained the reasoning process and supported inferences in a step-by-step, understandable manner.</p>
              </div>
              
              <div className="criterion-item">
                <h4>Justification with Evidence</h4>
                <p>Use of relevant citations and evidence to support claims made in the response.</p>
              </div>
              
              <div className="criterion-item">
                <h4>Contextual and Legal Understanding</h4>
                <p>Demonstrated comprehension of legal terminology and the broader context of the EU AI Act.</p>
              </div>
              
              <div className="criterion-item">
                <h4>Handling Ambiguity</h4>
                <p>Appropriate treatment of unclear aspects and recognition of different possible interpretations.</p>
              </div>
              
              <div className="criterion-item">
                <h4>Acknowledgment of Knowledge Gaps</h4>
                <p>Honest recognition of limitations or uncertainties in the response.</p>
              </div>
              
              <div className="criterion-item">
                <h4>Conciseness and Precision</h4>
                <p>Efficient delivery of information without unnecessary or redundant content.</p>
              </div>
              
              <div className="criterion-item">
                <h4>Coherence and Organization</h4>
                <p>Logical structure and flow of information throughout the response.</p>
              </div>
              
              <div className="criterion-item">
                <h4>Relevance and Focus</h4>
                <p>Direct addressing of the question without tangential or unrelated information.</p>
              </div>
              
              <div className="criterion-item">
                <h4>Completeness</h4>
                <p>Comprehensive coverage of all relevant aspects of the question.</p>
              </div>
            </div>
            
            <div className="criteria-note">
              <p>
                For each criterion, detailed instructions were provided to guide participants' judgment. Some criteria were intentionally competing (e.g., "Completeness" vs. "Conciseness") to test whether participants made thoughtful decisions.
              </p>
            </div>
          </div>
        </div>

        <div className="details-card">
          <div className="card-header">
            <h2>Technical Setup</h2>
          </div>
          <div className="card-body">
            <h3>Model Configurations</h3>
            
            <div className="model-config pakton">
              <h4>PAKTON</h4>
              <ul>
                <li><strong>Adaptation:</strong> Adapted specifically to answer questions about the EU AI Act restricting tool usage to only in document search (excluding web search etc.)</li>
                <li><strong>Depth:</strong> Set interrogation max turns to 5</li>
                <li><strong>Base Model:</strong> The base model used for PAKTON was gpt-4o in order to have a fair comparison</li>
              </ul>
            </div>
            
            <div className="model-config chatgpt">
              <h4>ChatGPT</h4>
              <ul>
                <li><strong>Document Integration:</strong> EU AI Act document uploaded via file-upload interface</li>
                <li>
                    <strong>Processing Method:</strong> ChatGPT Enterprise uses Retrieval-Augmented Generation (RAG) techniques to process the uploaded file 
                    <a 
                        href="https://help.openai.com/en/articles/10029836-optimizing-file-uploads-in-chatgpt-enterprise" 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={{ marginLeft: '4px' }}
                    >
                        according to this.
                    </a> 
                </li>
              </ul>
            </div>
            
            <p className="setup-note">
              This configuration enabled a fairer comparison between the two systems, as both had access to the same source document (EU AI Act) when generating responses.
            </p>
          </div>
        </div>

        <div className="details-card">
          <div className="card-header">
            <h2>Key Findings</h2>
          </div>
          <div className="card-body">
            <div className="findings-summary">
              <p>
                Based on the survey results, PAKTON was preferred over ChatGPT in the majority of evaluation criteria. This trend was consistent across all the legal questions presented to participants.
              </p>
            </div>
            
            <div className="findings-details">
              <h3>Strongest Advantages</h3>
              <div className="finding-item">
                <h4>Completeness</h4>
                <p>
                  The most significant difference was seen in the "Completeness" criterion. PAKTON tended to give more well-rounded answers, considering questions from multiple angles and offering a broader perspective.
                </p>
              </div>
              
              <div className="finding-item">
                <h4>Explainability and Reasoning</h4>
                <p>
                  PAKTON performed notably better in explaining its logic clearly and in a step-by-step manner, which is especially important for users without legal training.
                </p>
              </div>
              
              <h3>Trade-offs Observed</h3>
              <div className="finding-item">
                <h4>Completeness vs. Conciseness</h4>
                <p>
                  We included competing criteria to test participant attention. As expected, PAKTON was preferred for completeness, while ChatGPT was chosen more often for conciseness and precision. It's challenging for a response to excel in both dimensions simultaneously.
                </p>
              </div>
              
              <div className="finding-item">
                <h4>Balance in Relevance</h4>
                <p>
                  Both models received similar scores for "Relevance and Focus," likely reflecting the balance between including more perspectives (completeness) and staying tightly focused (conciseness).
                </p>
              </div>
            </div>
            
            <div className="conclusion">
              <p>
                Overall, these results align with PAKTON's design philosophy, which aims to provide detailed, report-like responses that thoroughly address complex legal questions. In this context, the trade-off between completeness and brevity seems acceptable and expected.
              </p>
              <p>
                The findings suggest that PAKTON's multi-agent approach offers advantages in explaining complex legal concepts to non-expert users, even when compared to a strong commercial baseline.
              </p>
            </div>
            
            <div className="button-container">
              <button onClick={() => navigate('/human-evaluation')} className="back-button">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="19" y1="12" x2="5" y2="12"></line>
                  <polyline points="12 19 5 12 12 5"></polyline>
                </svg>
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExperimentDetails;