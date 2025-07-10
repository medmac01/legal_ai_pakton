import React, { useState, useEffect } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import ReactJson from 'react-json-view';

const ExperimentDetailsView = ({ jsonData }) => {
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [scoresData, setScoresData] = useState(null);
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    const loadCode = async () => {
      try {
        setIsLoading(true);
        
        // Fetch the Python code file
        const response = await fetch('./data/geval.py');
        
        if (!response.ok) {
          throw new Error(`Failed to fetch code: ${response.status}`);
        }
        
        const codeContent = await response.text();
        setCode(codeContent);
        setIsLoading(false);
      } catch (err) {
        console.error('Error loading code:', err);
        setError('Failed to load experiment code file.');
        setIsLoading(false);
      }
    };
    
    loadCode();
  }, []);

  // Load the scores data
  useEffect(() => {
    const loadScores = async () => {
      try {
        const response = await fetch('./data/geval_scores.json');
        
        if (!response.ok) {
          throw new Error(`Failed to fetch scores: ${response.status}`);
        }
        
        const scoresContent = await response.json();
        setScoresData(scoresContent);
      } catch (err) {
        console.error('Error loading scores data:', err);
        // Not setting main error to avoid disrupting the UI
      }
    };
    
    loadScores();
  }, []);

  // Handle download of scores JSON file
  const handleDownloadScores = () => {
    try {
      setIsDownloading(true);
      
      // Create a blob from the scores data
      const fileData = JSON.stringify(scoresData, null, 2);
      const blob = new Blob([fileData], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      
      // Create a temporary anchor element and trigger download
      const a = document.createElement('a');
      a.href = url;
      a.download = 'geval_scores.json';
      document.body.appendChild(a);
      a.click();
      
      // Clean up
      setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        setIsDownloading(false);
      }, 1000);
    } catch (err) {
      console.error('Error downloading scores:', err);
      alert('Failed to download scores data');
      setIsDownloading(false);
    }
  };

  // Get all test cases
  const testCases = jsonData ? Object.keys(jsonData) : [];

  const evaluationCriteria = [
    'Explainability and Reasoning',
    'Justification with Evidence',
    'Contextual and Legal Understanding',
    'Handling Ambiguity',
    'Acknowledgment of Knowledge Gaps',
    'Conciseness and Precision',
    'Coherence and Organization',
    'Relevance and Focus',
    'Completeness'
  ];

  if (isLoading) {
    return <div className="loading">Loading experiment details...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <>
      <h2>G-EVAL Experiment Details</h2>
      
      <div className="experiment-tabs">
        <button 
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab-button ${activeTab === 'code' ? 'active' : ''}`}
          onClick={() => setActiveTab('code')}
        >
          Experiment Code
        </button>
        <button 
          className={`tab-button ${activeTab === 'data' ? 'active' : ''}`}
          onClick={() => setActiveTab('data')}
        >
          Sample JSON Data
        </button>
        <button 
          className={`tab-button ${activeTab === 'results' ? 'active' : ''}`}
          onClick={() => setActiveTab('results')}
        >
          Results
        </button>
      </div>
      
      <div className="experiment-content">
        {activeTab === 'overview' && (
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
        )}
        
        {activeTab === 'code' && (
          <div className="code-container">
            <h3>Experiment Code</h3>
            <SyntaxHighlighter language="python" style={oneDark} customStyle={{ borderRadius: '6px', fontSize: '14px' }}>
                {code}
            </SyntaxHighlighter>
          </div>
        )}
        
        {activeTab === 'data' && (
          <div className="json-container">
            <div className="download-section">
              <h3>Experiment Data</h3>
              <button 
                onClick={handleDownloadScores} 
                className={`download-button ${isDownloading ? 'downloading' : ''}`}
                disabled={isDownloading || !scoresData}
              >
                {isDownloading ? 'Downloading...' : 'Download Full Scores JSON'}
              </button>
            </div>

            <h3>Test Cases</h3>
            
            {testCases.length > 0 ? (
              <div className="all-test-cases">
                {testCases.map(caseId => (
                  <div key={caseId} className="test-case-item">
                    <h4>Test Case {caseId}</h4>
                    <ReactJson
                      src={{ [caseId]: jsonData[caseId] }}
                      name={false}
                      collapsed={1}
                      displayDataTypes={false}
                      enableClipboard={true}
                      style={{ fontSize: "14px" }}
                    />
                  </div>
                ))}
              </div>
            ) : (
              <p>No test cases available.</p>
            )}
          </div>
        )}

        {activeTab === 'results' && (
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
        )}
      </div>
      
      <style>{`
        .experiment-tabs {
          display: flex;
          margin-bottom: 20px;
          border-bottom: 1px solid #e2e8f0;
          flex-wrap: wrap;
        }
        
        .tab-button {
          padding: 10px 20px;
          background: none;
          border: none;
          border-bottom: 3px solid transparent;
          cursor: pointer;
          font-size: 15px;
          font-weight: 500;
          transition: all 0.2s;
        }
        
        .tab-button:hover {
          background-color: #f8fafc;
        }
        
        .tab-button.active {
          border-bottom: 3px solid #3b82f6;
          color: #3b82f6;
          font-weight: 600;
        }
        
        .overview-container, .code-container, .json-container, .results-container {
          background-color: #f8fafc;
          border-radius: 8px;
          padding: 20px;
          overflow: auto;
        }
        
        .criteria-list {
          margin-left: 20px;
          margin-bottom: 20px;
        }
        
        .criteria-list li {
          margin-bottom: 5px;
        }
        
        .code-block, .json-block {
          max-height: 500px;
          overflow: auto;
          background-color: #1e293b;
          color: #e2e8f0;
          padding: 15px;
          border-radius: 6px;
          line-height: 1.5;
          font-family: 'Courier New', monospace;
          white-space: pre-wrap;
          font-size: 14px;
        }

        .results-reference {
          margin-top: 20px;
          padding: 10px;
          background-color: #eef2ff;
          border-left: 4px solid #818cf8;
          border-radius: 4px;
        }
        
        .all-test-cases {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }
        
        .test-case-item {
          background-color: #f1f5f9;
          border-radius: 8px;
          padding: 15px;
          margin-bottom: 10px;
        }
        
        .test-case-item h4 {
          margin-top: 0;
          margin-bottom: 10px;
          color: #1e40af;
        }

        .download-section {
          display: flex;
          justify-content: space-between;
          align-items: center;
          background-color: #e0f2fe;
          padding: 16px 20px;
          border-radius: 8px;
          margin-bottom: 24px;
          border-left: 4px solid #0ea5e9;
        }

        .download-section h3 {
          margin: 0;
          color: #0369a1;
        }

        .download-button {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          padding: 10px 18px;
          background-color: #0284c7;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          transition: all 0.2s ease;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .download-button:hover {
          background-color: #0369a1;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          transform: translateY(-1px);
        }
        
        .download-button:active {
          transform: translateY(1px);
          box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }

        .download-button.downloading {
          background-color: #6b7280;
          cursor: not-allowed;
        }

        .download-button:disabled {
          background-color: #94a3b8;
          cursor: not-allowed;
        }

        .download-icon {
          font-size: 16px;
        }
      `}</style>
    </>
  );
};

export default ExperimentDetailsView;