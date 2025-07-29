import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line,
  ScatterChart, Scatter, ZAxis
} from 'recharts';

import './LegalBenchRAGPage.css';

const LegalBenchRAGPage = () => {
  const [flagRerankerData, setFlagRerankerData] = useState(null);
  const [llmRerankerData, setLlmRerankerData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedDataset, setSelectedDataset] = useState('ALL');
  const [selectedConfig, setSelectedConfig] = useState('flagReranker');

  // Sample data from the paper for visualization
  const performanceData = [
    { dataset: 'PrivacyQA', paktonRecall1: 17.00, paktonRecall2: 26.39, paktonRecall4: 39.99, paktonRecall8: 62.73 },
    { dataset: 'ContractNLI', paktonRecall1: 67.67, paktonRecall2: 83.35, paktonRecall4: 90.87, paktonRecall8: 95.16 },
    { dataset: 'MAUD', paktonRecall1: 17.06, paktonRecall2: 19.94, paktonRecall4: 30.57, paktonRecall8: 49.94 },
    { dataset: 'CUAD', paktonRecall1: 4.38, paktonRecall2: 16.11, paktonRecall4: 34.09, paktonRecall8: 53.00 },
    { dataset: 'ALL', paktonRecall1: 26.53, paktonRecall2: 36.45, paktonRecall4: 48.88, paktonRecall8: 65.21 }
  ];

  const precisionData = [
    { dataset: 'PrivacyQA', paktonPrecision1: 18.64, paktonPrecision2: 17.66, paktonPrecision4: 14.13, paktonPrecision8: 10.39 },
    { dataset: 'ContractNLI', paktonPrecision1: 42.21, paktonPrecision2: 36.86, paktonPrecision4: 19.81, paktonPrecision8: 10.58 },
    { dataset: 'MAUD', paktonPrecision1: 17.77, paktonPrecision2: 11.35, paktonPrecision4: 9.41, paktonPrecision8: 8.32 },
    { dataset: 'CUAD', paktonPrecision1: 2.61, paktonPrecision2: 5.10, paktonPrecision4: 5.72, paktonPrecision8: 4.18 },
    { dataset: 'ALL', paktonPrecision1: 20.31, paktonPrecision2: 17.74, paktonPrecision4: 12.27, paktonPrecision8: 8.37 }
  ];

  const compareData = [
    { k: 1, pakton: 26.53, baseline: 4.94 },
    { k: 2, pakton: 36.45, baseline: 8.22 },
    { k: 4, pakton: 48.88, baseline: 14.15 },
    { k: 8, pakton: 65.21, baseline: 22.78 }
  ];

  useEffect(() => {
    const loadData = async () => {
      try {
        setIsLoading(true);
        
        // Load data from JSON files
        const flagRerankerResponse = await fetch('./legalbenchrag/results/flagReranker/results_by_type_contractNLI.json');
        const llmRerankerResponse = await fetch('./legalbenchrag/results/llmReranker/results_by_type_contractNLI.json');
        
        if (flagRerankerResponse.ok) {
          const flagData = await flagRerankerResponse.json();
          setFlagRerankerData(flagData);
        }
        
        if (llmRerankerResponse.ok) {
          const llmData = await llmRerankerResponse.json();
          setLlmRerankerData(llmData);
        }
        
        setIsLoading(false);
      } catch (err) {
        console.error('Error loading data:', err);
        setError('Failed to load some data files. Some features may not be available.');
        setIsLoading(false);
      }
    };
    
    loadData();
  }, []);

  const handleDownload = (filename, configType) => {
    const url = `./legalbenchrag/results/${configType}/${filename}`;
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };



  const renderOverview = () => (
    <div className="overview-section">
      <div className="intro-text">
        <h2>Overview</h2>
        <p>
          This section presents the results of experiments conducted using the LegalBench-RAG benchmark 
          to evaluate PAKTON's retrieval capabilities. The experiments assess the performance of PAKTON's 
          Archivist and Researcher modules across four legal domains: NDAs, M&A agreements, commercial 
          contracts, and consumer-facing privacy policies.
        </p>
        
        <div className="references-section">
          <p>
            <strong>LegalBench-RAG GitHub Repository:</strong>{' '}
            <a 
              href="https://github.com/zeroentropy-ai/legalbenchrag" 
              target="_blank" 
              rel="noopener noreferrer"
              className="external-link"
            >
              https://github.com/zeroentropy-ai/legalbenchrag
            </a>
          </p>
          <p>
            <strong>Research Paper:</strong>{' '}
            <a 
              href="https://arxiv.org/abs/2408.10343" 
              target="_blank" 
              rel="noopener noreferrer"
              className="external-link"
            >
              LegalBench-RAG: A Benchmark for Retrieval-Augmented Generation in Legal Domain (arXiv:2408.10343)
            </a>
          </p>
          <p className="note">
            The original LegalBenchRAG codebase was modified to accommodate the PAKTON evaluation.
          </p>
        </div>
        
        <div className="comparison-results">
          <div className="image-container">
            <img src="./legalbenchrag/ComparisonResults.png" alt="Comparison Results" />
            <p className="image-caption">
              Precision and Recall @ k ∈ &#123;1, 2, 4, 8, 16, 32, 64&#125; for four retrieval pipelines on five legal-text datasets.
            </p>
          </div>
        </div>
        
        <div className="key-findings">
          <h3>Key Findings</h3>
          <ul>
            <li>PAKTON achieves significantly higher recall rates compared to baseline methods</li>
            <li>PAKTON demonstrates superior performance compared to baseline models, achieving a significantly larger area under the precision-recall curve (AUPRC), which indicates both higher precision and better recall across varying thresholds (k).”</li>
            <li>Aggregated results across all benchmark datasets show that PAKTON achieves over a 5× improvement in Recall@1 (26.77% vs. 4.94%) and more than a 3× improvement in Precision@1 (22.34% vs. 6.41%) compared to the strongest baseline.</li>
          </ul>
        </div>
      </div>
    </div>
  );

  const renderImages = () => (
    <div className="images-section">
      <h2>Experimental Results Visualizations</h2>
      <p>The following images show precision, recall performance comparisons between the different retrieval methods.</p>
      <p>PAKTON’s retrieval performance (purple line) is clearly superior to the baseline retrieval methods.</p>
      <div className="images-grid">
        <div className="image-container">
          <h3>Precision @ k across all datasets</h3>
          <img src="./legalbenchrag/precisionRetrieval.jpg" alt="Precision @ k across all datasets" />
          <p>This chart shows how precision varies across different k values for all datasets in the benchmark for different retrieval methods (see colors in the legend at Recall chart).</p>
        </div>
        
        <div className="image-container">
          <h3>Recall @ k across all datasets</h3>
          <img src="./legalbenchrag/recallRetrieval.jpg" alt="Recall @ k across all datasets" />
          <p>This chart demonstrates the recall performance across different k values for all datasets and for different retrieval methods (see legend's colors).</p>
        </div>
        
        <div className="image-container">
          <h3>Precision-Recall Trade-off</h3>
          <img src="./legalbenchrag/precision_recall.jpg" alt="Precision-Recall across all datasets" />
          <p>This visualization shows the trade-off between precision and recall across all datasets.</p>
        </div>
      </div>
    </div>
  );

  const renderResults = () => (
    <div className="results-section">
      <div className="results-header">
        <div className="results-title">
          <h2>Experiment Results</h2>
          <p>Download the complete experimental results for detailed analysis.</p>
        </div>
        <a 
          href="./legalbenchrag/results.zip" 
          download="legalbenchrag_results.zip"
          className="download-all-btn"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="download-icon">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7,10 12,15 17,10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          Download All Results
        </a>
      </div>
      
      <div className="configuration-results">
        <div className="config-images-grid">
          <div className="image-container">
            <h4>Configuration 1: Flag Reranker</h4>
            <img src="./legalbenchrag/Configuration1.png" alt="Configuration 1 Performance Results" />
            <p className="image-caption">
              Performance comparison on different datasets for Precision and Recall at various k values for PAKTON's Researcher and Archivist under configuration 1.
            </p>
          </div>
          
          <div className="image-container">
            <h4>Configuration 2: LLM Reranker</h4>
            <img src="./legalbenchrag/Configuration2.png" alt="Configuration 2 Performance Results" />
            <p className="image-caption">
              Performance comparison across different datasets in terms of Precision and Recall at various k values, using PAKTON's Researcher and Archivist under Configuration 2.
            </p>
          </div>
        </div>
      </div>
      
      <div className="section">
          <h3>Key Insights</h3>
          <p>
            Across all datasets, PAKTON consistently and significantly outperforms alternatives at every evaluated k.
            For instance, on the ContractNLI dataset, PAKTON achieves a Recall@1 of 53.14%, nearly 5 times higher than 
            the strongest baseline (11.32%), a trend that holds across all k values. Similar improvements are observed in 
            other datasets: on PrivacyQA, MAUD, and CUAD, PAKTON surpasses the best Recall@1 scores by margins often exceeding 20%. 
            Aggregate results reinforce this pattern, with PAKTON achieving more than five-fold increase in Recall@1 (26.77% vs. 4.94%).
            These improvements are especially critical in the legal domain, where high recall is essential. Failing to retrieve 
            relevants spans can result in flawed reasoning or unsupported conclusions, particularly when legal documents 
            contain conflicting clauses, exceptions, or interdependent provisions that must be interpreted in context.
          </p>
      </div>

      <div className="download-section">
        <div className="download-grid">
          <div className="config-section">
            <h4>Configuration 1: Flag Reranker</h4>
            <p>Results using a flag-based reranking approach</p>
            <p className="download-note">
              <em>Click the corresponding button below to download results for each dataset:</em>
            </p>
            <div className="download-buttons">
              <button onClick={() => handleDownload('results_by_type_contractNLI.json', 'flagReranker')}>
                ContractNLI Results
              </button>
              <button onClick={() => handleDownload('results_by_type_cuad.json', 'flagReranker')}>
                CUAD Results
              </button>
              <button onClick={() => handleDownload('results_by_type_maud.json', 'flagReranker')}>
                MAUD Results
              </button>
              <button onClick={() => handleDownload('results_by_type_privacyQA.json', 'flagReranker')}>
                PrivacyQA Results
              </button>
            </div>
          </div>
          
          <div className="config-section">
            <h4>Configuration 2: LLM Reranker</h4>
            <p>Results using an LLM-based reranking approach</p>
            <p className="download-note">
              <em>Click the corresponding button below to download results for each dataset:</em>
            </p>
            <div className="download-buttons">
              <button onClick={() => handleDownload('results_by_type_contractNLI.json', 'llmReranker')}>
                ContractNLI Results
              </button>
              <button onClick={() => handleDownload('results_by_type_cuad.json', 'llmReranker')}>
                CUAD Results
              </button>
              <button onClick={() => handleDownload('results_by_type_maud.json', 'llmReranker')}>
                MAUD Results
              </button>
              <button onClick={() => handleDownload('results_by_type_privacyQA.json', 'llmReranker')}>
                PrivacyQA Results
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderDiscussion = () => (
    <div className="discussion-section">
      <h2>Discussion</h2>
      
      <div className="discussion-content">
        <div className="section">
          <h3>Configuration 1 vs Configuration 2</h3>
          <p>
            While Configuration 1 serves as the primary setup for PAKTON, our evaluation indicates that Configuration 2 yields superior performance in terms of retrieval accuracy. However, this improvement comes at a cost: the second reranker in Configuration 2 is a large language model with 2.72 billion parameters, which introduces a significant latency overhead compared to the more lightweight setup in Configuration 1.
          </p>
          <p>
            Considering the trade-off between reranking accuracy and computational efficiency, Configuration 1 represents the most suitable choice for practical deployment scenarios where speed is a critical factor. Nevertheless, for applications where performance is prioritized over inference time, Configuration 2 may be preferred to achieve more competitive results.
          </p>
        </div>
        
        <div className="section">
          <h3>No LLM Filtering vs. LLM Filtering</h3>
          <p>
            In the legal domain, <strong>high recall</strong> is often of paramount importance, as omitting relevant spans can lead to incomplete or flawed legal reasoning. The <em>No LLM Filtering</em> configuration aligns better with this paradigm minimizing the risk of excluding potentially critical information. For this reason, it is selected as the primary setup in our evaluation.
          </p>
          <p>
            Nonetheless, there are scenarios where <strong>precision</strong> is more desirable—particularly when mitigating hallucination risks or when users require concise, targeted evidence rather than exhaustive retrieval. To accommodate such use cases, we evaluate an additional post-reranking stage employing the <em>LLM Filtering</em> variant, which identifies and extracts the most relevant sub-spans within each of the top-10 reranked chunks, thereby filtering the retrieval output to focus on the most contextually pertinent segments.
          </p>
          <p>
            This LLM Filtering variant significantly improves <strong>precision</strong>. However, this gain comes at the cost of <strong>recall</strong>, especially as the value of <code>top_k</code> increases, due to the stricter content selection. Based on these findings, we conclude that LLM Filtering is particularly advantageous for low <code>top_k</code> settings, where focused and precise evidence is preferred. In contrast, for higher <code>top_k</code> values, the unfiltered setup is more appropriate to maintain broader recall.
          </p>
        </div>
        
        <div className="section">
          <h3>Character-Based vs. Span-Based Calculation of Precision and Recall</h3>
          <p>
            The <strong>LegalBench-RAG</strong> paper adopts a character-based approach for computing precision and recall, and we follow the same protocol for our primary evaluation. However, we observe that this method may penalize retrieval strategies—particularly those targeting precision like the <em>LLM Filtering</em> variant—due to the fine-grained nature of the retrieved spans. Specifically, in many cases the retrieved content consists of subspans (often smaller than a sentence) that lie within the annotated answer span. Under the character-based metric, such partial matches are treated as incomplete, thereby reducing recall—even when the retrieved content is semantically relevant and informative.
          </p>
          <p>
            To further investigate this effect, we introduce a complementary <em>span-based</em> evaluation. In this setting, a retrieved span is considered a <em>hit</em> if it overlaps with any ground truth span, and a <em>miss</em> otherwise. This binary overlap-based metric provides clearer insight into how often irrelevant spans are retrieved or relevant spans are entirely missed.
          </p>
          <div className="image-container span-based-image-container">
            <img src="./legalbenchrag/SpanBasedConfiguration1.png" alt="Span-Based Configuration Performance Results" />
            <p className="image-caption">
              Performance comparison across different datasets in terms of Precision and Recall at various k values, using PAKTON's Researcher and Archivist components under Configuration 1, based on span-based calculation of Precision and Recall.
            </p>
          </div>
          <p>
            Overall, the span-based evaluation yields consistently higher values, with a particularly notable improvement in recall for the <em>LLM Filtering</em> variant. This suggests that character-level metrics may disproportionately penalize methods optimized for precision, potentially underestimating their effectiveness. It is also important to consider that different datasets contain varying numbers of ground truth spans per example, which can limit achievable recall at low <code>top_k</code> values.
            The following table presents the upper bounds on recall achievable under 100% precision.
          </p>
          <div className="image-container span-based-image-container perfect-recall">
            <img src="./legalbenchrag/PerfectRecall.png" alt="Span-Based Configuration Performance Results" />
            <p className="image-caption">
              Recall @ k for perfect retrieval using ground-truth snippets. Note: Precision is 100% for all cases.
            </p>
          </div>
          
        </div>
        
        <div className="section">
          <h3>Variation on Character Volume per chunk for different retrieval methods</h3>
          <p>
            Our analysis of precision and recall is conducted across varying <code>top_k</code> values. However, it is important to note that different retrieval methods return varying volumes of text, even when the same number of chunks is retrieved. For instance, one method may retrieve significantly fewer characters on average per chunk compared to another, despite retrieving the same number of chunks.
          </p>
          <p>
            This analysis allows us to assess the actual amount of information passed to the LLM across methods. Notably, the <em>LLM Filtering</em> variant consistently retrieves fewer characters than its unfiltered counterpart for the same number of chunks.
          </p>
          <p>
            Moreover, this analysis provides insight into the degree of document compression achieved during retrieval. For example, in the MAUD dataset, our <em>span-based</em> Recall@64 reaches 85.45% while retrieving, on average, 56,523 characters—compared to an average document length of 353,718 characters—indicating an approximate 84% compression of the original document content. Similarly, in the ContractNLI dataset, the <em>LLM Filtering</em> variant achieves a Recall@32 of 74.41% using only 1,081 characters, which corresponds to nearly 90% information compression.
          </p>
          
          <div className="image-container span-based-image-container">
            <img src="./legalbenchrag/CharactersRetrieved.png" alt="Characters Retrieved Performance Results" />
            <p className="image-caption">
              Average number of characters retrieved @ k for each dataset for PAKTON configuration 1. Comparison with average length of ground truth (answer) and document lengths.
            </p>
          </div>
        </div>
        
        <div className="section">
          <h3>Plots</h3>
          <p>
            The evaluation plots for all four methods of LegalBenchRAG and PAKTON, including Precision@k, Recall@k, and Precision–Recall curves across all datasets, are presented in the Visualizations tab. The results indicate that PAKTON consistently outperforms the other methods across all metrics.
          </p>
        </div>
        
        <div className="section">
          <h3>Conclusion</h3>
          <p>
            Taking into account the span-based evaluation metrics—which provide a more representative measure of retrieval quality—and the observed degree of information compression, the <em>Researcher</em> module demonstrates strong performance in the task of long-document retrieval within a practical deployment context.
          </p>
        </div>
      </div>
    </div>
  );

  const renderMethodology = () => (
    <div className="methodology-section">
      <h2>Methodology and Setup</h2>
      
      <div className="methodology-content">
        <div className="section">
          <h3>PAKTON System Assessment</h3>
          <p>
            To assess the retrieval capabilities of the <strong>PAKTON</strong> system on LegalBenchRAG, we evaluated the indexing and in-document retrieval functionality, which constitute the core components of the pipeline. In this setup:
          </p>
          <ul>
            <li>The <strong>Archivist</strong> component is responsible for document indexing.</li>
            <li>The <strong>Researcher</strong> performs in-document retrieval.</li>
            <li>Interactions through the <strong>Interrogator</strong> were bypassed to focus exclusively on retrieval performance.</li>
          </ul>
          <p>
            Each document from the dataset was indexed by the Archivist, and the corresponding queries were directly submitted to the Researcher. The retrieved spans were evaluated using the LegalBenchRAG scoring methodology.
          </p>
        </div>
        
        <div className="section">
          <h3>Configuration 1</h3>
          <div className="config-subsection">
            <h4>Archivist</h4>
            <ul>
              <li>Primary strategy: structural parsing.</li>
              <li>Fallback: Recursive Character Text Splitter with 1000-character chunks and no overlap if structural parsing failed.</li>
              <li>Embedding model: <code>text-embedding-3-large</code>.</li>
            </ul>
          </div>
          
          <div className="config-subsection">
            <h4>Researcher</h4>
            <ul>
              <li>Query optimization using gpt-4o and only in-document search as tool enabled.</li>
              <li>BM25 retrieves top-100 chunks with a similarity threshold of 0.6.</li>
              <li>Dense embedding retriever returns top-100 chunks with no similarity filtering using embeddings model <code>text-embedding-3-large</code></li>
              <li>Reciprocal Rank Fusion with equal weights for both retrievers to rerank chunks, pick top-64 chunks.</li>
              <li>Reranker: <code>BAAI/bge-reranker-v2-m3</code>, producing a top-64 reranked final list of chunks.</li>
              <li>Strip structural information of the chunk and keep only the original span.</li>
            </ul>
          </div>
          
          <div className="config-subsection">
            <h4>LLM Filtering</h4>
            <ul>
              <li>An additional post-reranking filtering stage is applied using <code>command-R</code> (Cohere), an open-source 35B parameter model specifically fine-tuned for Retrieval-Augmented Generation (RAG) applications.</li>
              <li>From the top-10 reranked chunks, the model identifies and extracts the most relevant sub-span(s) within each chunk, aiming to isolate highly precise evidence.</li>
              <li>This step is designed to enhance overall precision by focusing retrieval results on the most contextually pertinent portions of the content.</li>
            </ul>
          </div>
          
          <p className="config-note">
            Two variants are compared: one with and one without the LLM filtering step. The results reported and compared correspond to Configuration 1, specifically the variant without LLM filtering.
          </p>
        </div>
        
        <div className="section">
          <h3>Configuration 2</h3>
          <p>Same as Configuration 1 with the only change being the use of an alternative LLM-based reranker:</p>
          <ul>
            <li>Reranker: <code>BAAI/bge-reranker-v2-minicpm-layerwise</code> (2.72B parameters) with a 28-layer cutoff.</li>
          </ul>
        </div>
        
        <div className="section">
          <h3>Experimental Setup</h3>
          <p>
            The LegalBench-RAG benchmark was used to assess PAKTON's retrieval pipeline, specifically 
            the Archivist and Researcher modules, independently of answer generation. This evaluation 
            covers four contract-related domains:
          </p>
          <ul>
            <li><strong>NDAs:</strong> Non-Disclosure Agreements</li>
            <li><strong>M&A agreements:</strong> Merger and Acquisition contracts</li>
            <li><strong>Commercial contracts:</strong> Business-to-business agreements</li>
            <li><strong>Consumer-facing privacy policies:</strong> Privacy terms and conditions</li>
          </ul>
        </div>
        
        <div className="section">
          <h3>Baseline Comparisons</h3>
          <p>PAKTON was benchmarked against four baseline methods:</p>
          <ul>
            <li><strong>Naive:</strong> Fixed-size chunking with a window of 500 characters and no overlap; no reranker; embeddings generated using text-embedding-3-large.</li>
            <li><strong>RCTS:</strong> Recursive Character Text Splitter with no overlap; no reranker; embeddings generated using text-embedding-3-large.</li>
            <li><strong>Naive+Cohere:</strong> Naive Method followed by Cohere reranker rerank-english-v3.0</li>
            <li><strong>RCTS+Cohere:</strong> RCTS Method followed by Cohere reranker rerank-english-v3.0</li>
          </ul>
        </div>
        
        <div className="section">
          <h3>Evaluation Metrics</h3>
          <p>
          Performance was measured using precision and recall at various k thresholds (k = 1, 2, 4, 8, 16, 32, 64), 
          where k represents the number of top-ranked results considered. Precision@k quantifies how many of the top-k 
          retrieved items are actually relevant, indicating the accuracy of the model’s top predictions. In contrast, Recall@k 
          measures how many of the total relevant items were successfully retrieved within the top-k, reflecting the model’s 
          ability to cover all correct answers. 
          </p>
        </div>
        
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading LegalBench-RAG experiments data...</p>
      </div>
    );
  }

  return (
    <div className="legalbenchrag-page">
      <div className="page-header">
        <h1>LegalBench-RAG Experiments</h1>
        <p className="page-description">
          Evaluation of PAKTON's retrieval capabilities using the LegalBench-RAG benchmark 
          across different contract types with precision and recall metrics.
        </p>
      </div>

      <div className="tab-navigation">
        <button 
          className={activeTab === 'overview' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={activeTab === 'results' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('results')}
        >
          Results
        </button>
        <button 
          className={activeTab === 'images' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('images')}
        >
          Visualizations
        </button>
        <button 
          className={activeTab === 'methodology' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('methodology')}
        >
          Methodology
        </button>
        <button 
          className={activeTab === 'discussion' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('discussion')}
        >
          Discussion
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'results' && renderResults()}
        {activeTab === 'images' && renderImages()}
        {activeTab === 'methodology' && renderMethodology()}
        {activeTab === 'discussion' && renderDiscussion()}
      </div>

      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}
    </div>
  );
};

export default LegalBenchRAGPage;
