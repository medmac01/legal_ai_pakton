import React, { useState, useEffect } from 'react';
import './ContractNLIPage.css';

const ContractNLIPage = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedImage, setSelectedImage] = useState(null);

  // Handle download for results
  const handleDownload = (filename) => {
    // Create download for results zip
    const link = document.createElement('a');
    link.href = `./contractNLI/results.zip`;
    link.download = 'contractnli_results.zip';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Handle image click to enlarge
  const handleImageClick = (imageSrc, imageAlt) => {
    setSelectedImage({ src: imageSrc, alt: imageAlt });
  };

  // Handle modal close
  const handleCloseModal = () => {
    setSelectedImage(null);
  };

  // Handle keyboard events
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape' && selectedImage) {
        handleCloseModal();
      }
    };

    if (selectedImage) {
      document.addEventListener('keydown', handleKeyDown);
      // Prevent body scrolling when modal is open
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [selectedImage]);

  const renderOverviewTab = () => (
    <div className="tab-content">
      <div className="section">
        <h3>ContractNLI Experiments Overview</h3>
        <p>
          PAKTON was evaluated on the ContractNLI dataset to assess its end-to-end generation performance. ContractNLI is a dataset that requires models to determine whether 
          a hypothesis is entailed by, contradicted by, or neutral with respect to a contract.
        </p>
      </div>

      <div className="results-table-section">
        <h4>Performance Results</h4>
        <div className="overview-images-container">
          <div className="image-container">
            <img 
              src="./contractNLI/zs_pakton_orthogonal_regression.png" 
              alt="Zero-Shot vs PAKTON Performance" 
              className="results-table-image clickable-image"
              onClick={() => handleImageClick('./contractNLI/zs_pakton_orthogonal_regression.png', 'Zero-Shot vs PAKTON Performance')}
            />
            <p className="image-caption">
              Performance of LLMs with and without PAKTON
            </p>
          </div>
          
          <div className="image-container">
            <img 
              src="./contractNLI/results.png" 
              alt="ContractNLI Performance Comparison" 
              className="results-table-image clickable-image enlarged-image"
              onClick={() => handleImageClick('./contractNLI/results.png', 'ContractNLI Performance Comparison')}
            />
            <p className="image-caption">
              Performance comparison of PAKTON and other methods across models on the ContractNLI test set. 
              The highest accuracy and F1[w] are shown in bold.
            </p>
          </div>
        </div>
      </div>

      <div className="section">
        <h3>Key Findings</h3>
        <div className="findings-grid">
          <div className="finding-card">
            <h4>Superior Performance</h4>
            <p>
              PAKTON consistently outperforms baseline methods across all evaluated models, 
              including domain-specific fine-tuned models like Saul. PAKTON with open source models matches and surpasses proprietary models like GPT-4o.
            </p>
          </div>
          <div className="finding-card">
            <h4>Robustness Analysis</h4>
            <p>
              PAKTON reduces performance disparities among diverse LLMs while preserving consistently high accuracy. Such robustness is particularly advantageous in the legal domain, where relying on open–source models alleviates the privacy risks associated with sending sensitive contractual or legal information to proprietary systems.
            </p>
          </div>
          
        </div>
      </div>
    </div>
  );

  const renderResultsTab = () => (
    <div className="tab-content">
      <div className="section">
        <h3>Detailed Experimental Results</h3>
        <p>
          Complete results from our ContractNLI experiments across multiple models, prompting strategies, 
          and configurations. All experiments were conducted on the ContractNLI test set containing 2,091 samples.
        </p>
      </div>

      <div className="download-section">
        <h4>Download Complete Results</h4>
        <p>
          Access the full experimental data including predictions, metrics, and configuration details 
          for all 210 distinct experiments conducted.
        </p>
        <button 
          className="download-button"
          onClick={() => handleDownload('contractnli_results.zip')}
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          Download All Results
        </button>
      </div>

      <div className="detailed-results-section">
        <h4>Baseline Performance Results</h4>
        <div className="results-images-grid">
          <div className="image-container">
            <img 
              src="./contractNLI/detailed_results_1.png" 
              alt="Detailed Results Part 1" 
              className="detailed-results-image clickable-image"
              onClick={() => handleImageClick('./contractNLI/detailed_results_1.png', 'Detailed Results Part 1')}
            />
            <p className="image-caption">
              Baseline performance of models across multiple evaluation runs on the ContractNLI test set. (Part 1 of 3)
            </p>
          </div>
          
          <div className="image-container">
            <img 
              src="./contractNLI/detailed_results_2.png" 
              alt="Detailed Results Part 2" 
              className="detailed-results-image clickable-image"
              onClick={() => handleImageClick('./contractNLI/detailed_results_2.png', 'Detailed Results Part 2')}
            />
            <p className="image-caption">
              Baseline performance of models across multiple evaluation runs on the ContractNLI test set. (Part 2 of 3)
            </p>
          </div>
          
          <div className="image-container">
            <img 
              src="./contractNLI/detailed_results_3.png" 
              alt="Detailed Results Part 3" 
              className="detailed-results-image clickable-image"
              onClick={() => handleImageClick('./contractNLI/detailed_results_3.png', 'Detailed Results Part 3')}
            />
            <p className="image-caption">
              Baseline performance of models across multiple evaluation runs on the ContractNLI test set. (Part 3 of 3)
            </p>
          </div>
          
          <div className="image-container">
            <img 
              src="./contractNLI/detailed_results_4.png" 
              alt="Detailed Results Part 4" 
              className="detailed-results-image clickable-image"
              onClick={() => handleImageClick('./contractNLI/detailed_results_4.png', 'Detailed Results Part 4')}
            />
            <p className="image-caption">
              Performance results with isolated spans configuration on the ContractNLI test set. (Part 1 of 3)
            </p>
          </div>
          
          <div className="image-container">
            <img 
              src="./contractNLI/detailed_results_5.png" 
              alt="Detailed Results Part 5" 
              className="detailed-results-image clickable-image"
              onClick={() => handleImageClick('./contractNLI/detailed_results_5.png', 'Detailed Results Part 5')}
            />
            <p className="image-caption">
              Performance results with isolated spans configuration on the ContractNLI test set. (Part 2 of 3)
            </p>
          </div>
          
          <div className="image-container">
            <img 
              src="./contractNLI/detailed_results_6.png" 
              alt="Detailed Results Part 6" 
              className="detailed-results-image clickable-image"
              onClick={() => handleImageClick('./contractNLI/detailed_results_6.png', 'Detailed Results Part 6')}
            />
            <p className="image-caption">
              Performance results with isolated spans configuration on the ContractNLI test set. (Part 3 of 3)
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderMethodologyTab = () => (
    <div className="tab-content">
      <div className="section">
        <h3>Experimental Setup</h3>
        <p>
          For the quantitative evaluation, PAKTON was evaluated on the ContractNLI dataset. In this dataset, 
          a premise denotes an entire contract document, with each premise paired with a corresponding hypothesis. 
          The classification task involves determining whether the hypothesis is entailed by, contradicted by, 
          or not addressed in (neutral with respect to) the associated contract. Given the substantial length 
          of the contracts, the dataset also provides annotated spans that indicate the specific portions of 
          text necessary for making the classification decision.
        </p>
        
        <p>
          We evaluate PAKTON on ContractNLI by comparing its performance against several baselines, including 
          models specifically pretrained on legal corpora (e.g., Saul) and models employing different prompting 
          techniques. The evaluation metrics presented include overall accuracy and the weighted F1-score (F1[W]), 
          alongside the individual F1-scores for the entailment, contradiction, and neutral classes.
        </p>
        
        <p>
          The prompting approaches examined include zero-shot (ZS), few-shot (FS)—where entire contractual 
          documents are used as exemplars—and an alternative few-shot setting (FS-Spans), in which only the 
          relevant spans influencing classification are provided. The results indicate a clear superiority of 
          PAKTON across all evaluated methods, notably outperforming even domain-specific fine-tuned models.
        </p>
      </div>

      <div className="section">
        <h3>Results Analysis</h3>
        <p>
          Firstly, PAKTON consistently outperforms the baseline methods across all models. Comparing the results 
          of Mistral and Mixtral with Saul, we observe that PAKTON yields better performance even compared to 
          fine-tuning on related legal corpora. Notably, Mistral 7B with PAKTON surpasses Saul 54B—a model 
          derived from the larger Mixtral 54B and fine-tuned on legal data. Furthermore, Mistral 7B with PAKTON 
          even outperforms GPT-4o in a FS setting.
        </p>
        
        <p>
          Furthermore, a notable observation emerges from comparing the performance across different core language 
          models utilizing our framework. The variation in performance among models integrated with PAKTON was 
          minimal, highlighting the robustness of the proposed framework. For example, the F1[W] for Llama 3.1 70B 
          score with PAKTON is 79.03%, while for Gemma 3 27B is 82.83%, yielding a modest difference of only 3.8 
          percentage points. In contrast, the performance gap between these models under the ZS prompting scenario 
          is significantly larger (22.83%), clearly demonstrating that Gemma 3 27B substantially outperforms 
          Llama 3.1 70B in the baseline ZS setting. This considerable reduction in performance disparity indicates 
          that PAKTON's architecture effectively mitigates the inherent variability among underlying LLMs, ensuring 
          consistently high performance regardless of the core model employed.
        </p>
        
        <p>
          To further investigate PAKTON's robustness, we conduct a targeted statistical analysis focusing on 
          variability and dependency. First, we compute the coefficient of variation (CV) across all models' 
          PAKTON-based F1[W] scores, obtaining a low CV of 12.6% (for comparison, ZS scores typically exhibit 
          CVs &gt;25%). This indicates minimal relative variability and, consequently, high robustness. Second, 
          we perform a one-way ANOVA by splitting models into two groups according to the median of their ZS scores. 
          The test reveals no statistically significant difference in PAKTON performance between the high- and 
          low-ZS groups (F-statistic = 3.05, p=0.12).
        </p>
        
        <p>
          Lastly, linear regression analysis is conducted to assess the direct relationship between baseline ZS 
          performance and PAKTON, yielding a shallow slope of 0.44, demonstrating that every unit of baseline 
          gain translates into less than half a unit under PAKTON, thereby compressing absolute performance gaps.
        </p>
        
        <p>
          Collectively, these findings demonstrate that PAKTON substantially reduces performance disparities among 
          diverse LLMs while preserving consistently high accuracy. Such robustness is particularly advantageous 
          in the legal domain, where relying on open-source models alleviates the privacy risks associated with 
          sending sensitive contractual or legal information to proprietary systems.
        </p>
      </div>

      <div className="section">
        <h3>Dataset Overview</h3>
        <p>
          We conduct all experiments on the test split of the ContractNLI dataset, which contains 2,091 samples. 
          Each sample consists of a full non-disclosure agreement (NDA) as the <em>premise</em>, a legal statement 
          as the <em>hypothesis</em>, and an <em>inference label</em> indicating whether the hypothesis is entailed, 
          contradicted, or neutral with respect to the contract.
        </p>
        
        <h4>Dataset Subsets</h4>
        <ul>
          <li>
            <strong>contractnli_b:</strong> The full version of the dataset. It includes 7.19K samples in the 
            training split, 1.04K in the validation split, and 2.09K in the test split. The full contract is 
            used as the premise for each example.
          </li>
          <li>
            <strong>contractnli_a:</strong> A filtered version of contractnli_b in which only the minimal spans 
            necessary to determine the correct label are retained as the premise, significantly reducing the input 
            length. Experiments using this subset simulate ideal retrieval conditions and serve as an upper bound 
            for the potential performance of a perfect RAG system.
          </li>
        </ul>
      </div>

      <div className="section">
        <h3>Prompting Strategies</h3>
        <p>We experiment with the following prompting techniques:</p>
        
        <div className="prompting-strategies">
          <div className="strategy-card">
            <h4>Naive Zero-shot (ZS)</h4>
            <p>
              No examples are given. A basic description of the label classes is provided, and the full contract 
              is used as the premise. This serves as a solid baseline for performance.
            </p>
          </div>
          
          <div className="strategy-card">
            <h4>Optimized Zero-shot (opt. ZS)</h4>
            <p>
              Uses hardcoded explanations of the classes and improved prompt structure. Still uses the full contract 
              as the premise. Explores the effect of manual prompt engineering.
            </p>
          </div>
          
          <div className="strategy-card">
            <h4>Naive Few-shot (FS)</h4>
            <p>
              Builds on the optimized zero-shot format, but includes three random training examples (contract, 
              hypothesis, and label) in the prompt. The full contract is used as the premise in both the examples 
              and the current input.
            </p>
          </div>
          
          <div className="strategy-card">
            <h4>Few-shot Isolated Spans (FS+Spans)</h4>
            <p>
              Similar to naive few-shot, but in the training examples, only the relevant spans (rather than the 
              entire contract) are provided as the premise.
            </p>
          </div>
          
          <div className="strategy-card">
            <h4>Few-shot Spans + Hypothesis (FS+Spans+Hyp)</h4>
            <p>
              A refinement where few-shot examples are dynamically selected to match the hypothesis of the current 
              sample, increasing semantic alignment. Shows the effect of using effective cross-document retrieval.
            </p>
          </div>
          
          <div className="strategy-card">
            <h4>Chain of Thought (CoT)</h4>
            <p>
              Extends the previous method by also including reasoning steps (i.e., rationales or justifications) 
              in the answers of the few-shot examples, encouraging more explicit reasoning in the final output.
            </p>
          </div>
        </div>
      </div>

      <div className="section">
        <h3>PAKTON Execution Details</h3>
        <p>
          To simulate a <em>cross-document retrieval</em> setting, we indexed the training and validation splits 
          of the ContractNLI dataset, preserving each example alongside its corresponding ground-truth label. 
          Each contract chunk was embedded and stored in the most appropriate index, where grouping was determined 
          by the combination of the hypothesis and its associated label. This approach emulates the core behavior 
          of the <em>Archivist</em> module, which supports organizing textual segments into logically distinct 
          indices—such as by contract type or clause category.
        </p>
        
        <p>
          For example, all instances associated with the hypothesis "The Receiving Party shall not disclose the 
          fact that the Agreement was agreed or negotiated" and labeled as <em>Neutral</em> were stored within 
          a single index, while examples labeled as <em>Entailment</em> or <em>Contradiction</em> were assigned 
          to their respective indices.
        </p>
        
        <p>
          Each set of indices corresponding to the same hypothesis was interconnected into a composable graph 
          using the LlamaIndex framework. These hypothesis-specific graphs were then integrated into a unified, 
          higher-level composable graph. Every node—whether a graph or a leaf index—was annotated with a brief 
          natural language description summarizing the content it encapsulated.
        </p>
        
        <p>
          At inference time, this hierarchical structure was traversed recursively. At each level of the graph, 
          a similarity comparison was conducted between the input query and the textual descriptions of child 
          nodes to determine the most relevant subgraph to explore. This hierarchical traversal mechanism enables 
          efficient prioritization of semantically aligned indices, thereby improving retrieval relevance.
        </p>
        
        <p>
          The <em>Researcher</em> module utilized this architecture as a cross-document retrieval system, returning 
          the top-3 most relevant examples for a given query. As for the <em>Researcher</em> module, we utilized 
          <strong>Configuration 1</strong>, with <em>No LLM filtering</em> and kept the top-10 reranked chunks 
          to generate the response back to the Interrogator.
        </p>
        
        <p>
          Regarding the interrogation process, we capped the maximum number of turns to five in order to maintain 
          efficiency and avoid excessively long interaction sequences.
        </p>
      </div>

      <div className="section">
        <h3>Experimental Infrastructure</h3>
        <p>
          <strong>Hardware:</strong> All local experiments were conducted on a server equipped with 4x NVIDIA A6000 GPUs, 
          each with 48GB VRAM, using the AI adaptive infrastructure.
        </p>
        
        <p>
          <strong>Quantization:</strong> We employed multiple quantization levels to evaluate performance under 
          varying resource constraints. The specific techniques and configurations used are available in our 
          GitHub repository.
        </p>
        
        <p>
          <strong>Scale:</strong> In total, we ran 210 distinct experiments (each one for the whole test set of 
          ContractNLI) across model, prompting, and input configurations.
        </p>
      </div>
    </div>
  );

  return (
    <div className="contractnli-page">
      <div className="page-header">
        <h1>ContractNLI Experiments</h1>
        <p className="page-description">
          Comprehensive evaluation of PAKTON on the ContractNLI dataset for natural language inference 
          in legal contract documents using metrics like accuracy and F1-score.
        </p>
      </div>

      <div className="tab-navigation">
        <button 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab ${activeTab === 'results' ? 'active' : ''}`}
          onClick={() => setActiveTab('results')}
        >
          Results
        </button>
        <button 
          className={`tab ${activeTab === 'methodology' ? 'active' : ''}`}
          onClick={() => setActiveTab('methodology')}
        >
          Methodology
        </button>
      </div>

      <div className="content-container">
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'results' && renderResultsTab()}
        {activeTab === 'methodology' && renderMethodologyTab()}
      </div>

      {/* Image Modal */}
      {selectedImage && (
        <div className="image-modal" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="close-button" onClick={handleCloseModal}>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
            <img 
              src={selectedImage.src} 
              alt={selectedImage.alt} 
              className="modal-image"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default ContractNLIPage;
