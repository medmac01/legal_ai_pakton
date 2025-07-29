import React from 'react';
import { useNavigate } from 'react-router-dom';

import styles from './HomePage.css';

const HomePage = () => {
  const navigate = useNavigate();
  const [currentSlide, setCurrentSlide] = React.useState(0);

  const navigateToGeval = () => {
    navigate('/geval');
  };

  const navigateToHumanEval = () => {
    navigate('/human-evaluation');
  };
  
  const navigateToAbout = () => {
    navigate('/about');
  };

  const cards = [
    {
      id: 'contractnli',
      title: 'ContractNLI Experiments',
      description: 'View the results of the experiments made on the ContractNLI dataset. These results target the end-to-end generation ability of the system in a classification task.',
      metrics: ['Classification', 'Generation ability', 'Accuracy', 'F1 score'],
      buttonText: 'View ContractNLI results',
      onClick: () => navigate('/contractnli-evaluation'),
      headerClass: 'contractnli-header',
      buttonClass: 'contractnli-button',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M9 12l2 2 4-4"></path>
          <circle cx="12" cy="12" r="9"></circle>
        </svg>
      )
    },
    {
      id: 'retrieval',
      title: 'LegalBenchRAG Experiments',
      description: 'View the results of the experiments made on the LegalBenchRAG benchmark. These experiments assess the Researcher\'s ability to retrieve relevant information.',
      metrics: ['Retrieval Augmented Generation (RAG)', 'Researcher', 'Precision', 'Recall'],
      buttonText: 'View LegalBenchRAG results',
      onClick: () => navigate('/retrieval-evaluation'),
      headerClass: 'retrieval-header',
      buttonClass: 'retrieval-button',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <path d="m21 21-4.35-4.35"></path>
        </svg>
      )
    },
    {
      id: 'geval',
      title: 'G-Eval Framework Experiments',
      description: 'View automatic evaluations comparing PAKTON and GPT-4o (with RAG) performance using the G-Eval framework across multiple dimensions.',
      metrics: ['Explainability', 'Justification', 'Contextual Understanding', '+ 5 more metrics'],
      buttonText: 'View G-Eval Results',
      onClick: navigateToGeval,
      headerClass: 'geval-header',
      buttonClass: 'geval-button',
      icon: (
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          viewBox="0 0 24 24" 
          fill="currentColor"
          stroke="none"
          className="nav-icon"
          role="img"
        >
          <title>OpenAI icon</title>
          <path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1686a.071.071 0 0 1 .038.052v5.5826a4.504 4.504 0 0 1-4.4945 4.4944zm-9.6607-4.1254a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1408-1.6464zM2.3408 7.8956a4.485 4.485 0 0 1 2.3655-1.9728V11.6a.7664.7664 0 0 0 .3879.6765l5.8144 3.3543-2.0201 1.1685a.0757.0757 0 0 1-.071 0l-4.8303-2.7865A4.504 4.504 0 0 1 2.3408 7.872zm16.5963 3.8558L13.1038 8.364 15.1192 7.2a.0757.0757 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6772a.79.79 0 0 0-.407-.667zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.7759.7759 0 0 0-.7854 0L9.409 9.2297V6.8974a.0662.0662 0 0 1 .0284-.0615l4.8303-2.7866a4.4992 4.4992 0 0 1 6.6802 4.66zM8.3065 12.863l-2.02-1.1638a.0804.0804 0 0 1-.038-.0567V6.0742a4.4992 4.4992 0 0 1 7.3757-3.4537l-.142.0805L8.704 5.459a.7948.7948 0 0 0-.3927.6813zm1.0976-2.3654l2.602-1.4998 2.6069 1.4998v2.9994l-2.5974 1.4997-2.6067-1.4997Z"/>
        </svg>
      )
    },
    {
      id: 'human',
      title: 'Human Evaluation Surveys',
      description: 'See the results of human evaluations comparing the output quality of PAKTON and GPT-4o in a real-world legal use case.',
      metrics: ['Preference Ratings', 'Quality Assessment', 'Usefulness', 'Clarity & Precision'],
      buttonText: 'View Human Evaluations',
      onClick: navigateToHumanEval,
      headerClass: 'human-header',
      buttonClass: 'human-button',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
          <circle cx="9" cy="7" r="4"></circle>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
          <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
        </svg>
      )
    }
  ];

  const nextSlide = () => {
    // Allow scrolling until the last card is fully visible
    const maxSlide = Math.max(0, cards.length - 1);
    setCurrentSlide((prev) => Math.min(prev + 1, maxSlide));
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => Math.max(prev - 1, 0));
  };

  const maxSlide = Math.max(0, cards.length - 1);
  const canGoNext = currentSlide < maxSlide;
  const canGoPrev = currentSlide > 0;

  return (
    <div className="home-page">
      <div className="hero-section">
        <h1>PAKTON Evaluation Dashboard</h1>
        <p className="subtitle">Evaluating the performance of PAKTON in different subtasks and settings</p>
        
        <div className="resource-buttons">
          <a href="https://arxiv.org/abs/2506.00608" target="_blank" rel="noopener noreferrer" className="resource-button paper-button">
            <svg className="svg-inline--fa fa-file-pdf fa-w-12" aria-hidden="true" focusable="false" data-prefix="fas" data-icon="file-pdf" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" data-fa-i2svg="">
              <path fill="currentColor" d="M181.9 256.1c-5-16-4.9-46.9-2-46.9 8.4 0 7.6 36.9 2 46.9zm-1.7 47.2c-7.7 20.2-17.3 43.3-28.4 62.7 18.3-7 39-17.2 62.9-21.9-12.7-9.6-24.9-23.4-34.5-40.8zM86.1 428.1c0 .8 13.2-5.4 34.9-40.2-6.7 6.3-29.1 24.5-34.9 40.2zM248 160h136v328c0 13.3-10.7 24-24 24H24c-13.3 0-24-10.7-24-24V24C0 10.7 10.7 0 24 0h200v136c0 13.2 10.8 24 24 24zm-8 171.8c-20-12.2-33.3-29-42.7-53.8 4.5-18.5 11.6-46.6 6.2-64.2-4.7-29.4-42.4-26.5-47.8-6.8-5 18.3-.4 44.1 8.1 77-11.6 27.6-28.7 64.6-40.8 85.8-.1 0-.1.1-.2.1-27.1 13.9-73.6 44.5-54.5 68 5.6 6.9 16 10 21.5 10 17.9 0 35.7-18 61.1-61.8 25.8-8.5 54.1-19.1 79-23.2 21.7 11.8 47.1 19.5 64 19.5 29.2 0 31.2-32 19.7-43.4-13.9-13.6-54.3-9.7-73.6-7.2zM377 105L279 7c-4.5-4.5-10.6-7-17-7h-6v128h128v-6.1c0-6.3-2.5-12.4-7-16.9zm-74.1 255.3c4.1-2.7-2.5-11.9-42.8-9 37.1 15.8 42.8 9 42.8 9z"></path>
            </svg>
            Paper
          </a>
          <a href="https://github.com/petrosrapto/PAKTON" target="_blank" rel="noopener noreferrer" className="resource-button github-button">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
            </svg>
            Code
          </a>
        </div>
      </div>
      
      <div className="carousel-container">
        <button 
          className="carousel-arrow carousel-arrow-left" 
          onClick={prevSlide}
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>
        
        <div className="experiment-cards">
          <div className="carousel-wrapper" style={{ transform: `translateX(-${currentSlide * 10}%)` }}>
            {cards.map((card, index) => (
              <div key={card.id} className="card" onClick={card.onClick}>
                <div className={`card-header ${card.headerClass}`}>
                  <div className="icon-wrapper">
                    {card.icon}
                  </div>
                </div>
                <div className="card-content">
                  <h2>{card.title}</h2>
                  <p>{card.description}</p>
                  <div className="metrics-preview">
                    {card.metrics.map((metric, i) => (
                      <span key={i}>{metric}</span>
                    ))}
                  </div>
                  <button className={`view-button ${card.buttonClass}`}>
                    <span>{card.buttonText}</span>
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="5" y1="12" x2="19" y2="12"></line>
                      <polyline points="12 5 19 12 12 19"></polyline>
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <button 
          className="carousel-arrow carousel-arrow-right" 
          onClick={nextSlide}
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </button>
      </div>
      
      {/* About Card - separate from carousel */}
      <div className="card about-card">
        <div className="card-content">
          <h2>About PAKTON</h2>
          <p>
          A multi-agent framework specifically designed for contract analysis, enabling users to better understand contract content through question answering.
          </p>
          <div className="advantages-grid">
            <div className="advantage-item">
              <div className="advantage-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                  <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
              </div>
              <h3>Improved Perfomance in Contract Analysis</h3>
              <p>According to experiments, PAKTON achieves better accuracy in subtasks in the field of contract analysis compared to general-purpose models.</p>
            </div>
            
            <div className="advantage-item">
              <div className="advantage-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
                </svg>
              </div>
              <h3>Enhanced Explainability</h3>
              <p>Explanations of the reasoning process are provided, ensuring interpretable decision-making. Statements are supported by evidence and any knowledge gaps are explicitly stated. </p>
            </div>

            <div className="advantage-item">
              <div className="advantage-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                </svg>
              </div>
              <h3>Advanced Reasoning and Retrieval</h3>
              <p>The process of answering a user question involves multiple iterations of retrieval and refinement, providing completeness and understanding.</p>
            </div>
            
            <div className="advantage-item">
              <div className="advantage-icon">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <ellipse cx="12" cy="5" rx="9" ry="3" />
                  <path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5" />
                  <path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3" />
                </svg>
              </div>
              <h3>Broad Integration</h3>
              <p>
                Aggregates data from various sources, filters for relevance, and combines insights from web, in-document and cross-document search, as well as external legal databases.
              </p>
            </div>
          </div>
          
          <button onClick={navigateToAbout} className="view-button about-button">
            <span>Learn More About PAKTON</span>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default HomePage;