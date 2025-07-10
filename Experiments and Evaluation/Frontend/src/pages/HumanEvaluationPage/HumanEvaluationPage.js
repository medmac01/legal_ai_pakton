import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import Papa from 'papaparse';
import './HumanEvaluationPage.css';
import { criteria } from '../../constants/evaluationCriteria';
import { availableQuestions } from '../../constants/availableQuestions';

const HumanEvaluationPage = () => {
  const { questionId } = useParams(); // Get the questionId from URL parameters
  const navigate = useNavigate();
  const [evaluationData, setEvaluationData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [activeResponse, setActiveResponse] = useState(0);
  const [surveyFeedback, setSurveyFeedback] = useState([]);
  const [questionInfo, setQuestionInfo] = useState(null);
  
  useEffect(() => {
    // Find the current question info based on the URL parameter
    const currentQuestion = availableQuestions.find(q => q.id === questionId);
    
    if (!currentQuestion) {
      setError(`Question "${questionId}" not found`);
      setIsLoading(false);
      return;
    }
    
    setQuestionInfo(currentQuestion);
    
    const loadData = async () => {
      try {
        setIsLoading(true);
        
        // Fetch the CSV file for the current question
        // Use the filePath directly from currentQuestion, which now includes process.env.PUBLIC_URL
        const response = await fetch(currentQuestion.filePath);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch data: ${response.status}`);
        }
        
        const csvText = await response.text();
        
        // Parse CSV data
        Papa.parse(csvText, {
          header: true,
          complete: (results) => {
            processData(results.data, currentQuestion.description);
            extractSurveyFeedback(results.data);
            setIsLoading(false);
          },
          error: (error) => {
            console.error('Error parsing CSV:', error);
            setError('Failed to parse CSV data');
            setIsLoading(false);
          }
        });
        
      } catch (err) {
        console.error('Error loading data:', err);
        setError('Failed to load data. Please check if the CSV file exists and is accessible.');
        setIsLoading(false);
      }
    };
    
    loadData();
  }, [questionId]);
  
  // Extract survey feedback from CSV
  const extractSurveyFeedback = (data) => {
    const feedbackColumn = "Give Feedback about the Survey. \nYou can access the system here and test it with your own questions.";
    const feedbackData = data
      .filter(item => item[feedbackColumn] && item[feedbackColumn].trim() !== '')
      .map(item => item[feedbackColumn]);
    
    setSurveyFeedback(feedbackData);
  };
  
  // Handle tab navigation buttons
  useEffect(() => {
    const prevButton = document.querySelector('.prev-tab');
    const nextButton = document.querySelector('.next-tab');
    const tabsContainer = document.querySelector('.tabs-navigation');
    
    if (prevButton && nextButton && tabsContainer) {
      prevButton.addEventListener('click', () => {
        tabsContainer.scrollBy({ left: -200, behavior: 'smooth' });
      });
      
      nextButton.addEventListener('click', () => {
        tabsContainer.scrollBy({ left: 200, behavior: 'smooth' });
      });
      
      // Check if scroll buttons should be visible
      const checkScrollButtons = () => {
        const { scrollLeft, scrollWidth, clientWidth } = tabsContainer;
        
        prevButton.style.opacity = scrollLeft > 0 ? '1' : '0.3';
        nextButton.style.opacity = scrollLeft + clientWidth < scrollWidth - 10 ? '1' : '0.3';
      };
      
      tabsContainer.addEventListener('scroll', checkScrollButtons);
      window.addEventListener('resize', checkScrollButtons);
      
      // Initial check
      checkScrollButtons();
      
      return () => {
        tabsContainer.removeEventListener('scroll', checkScrollButtons);
        window.removeEventListener('resize', checkScrollButtons);
      };
    }
  }, [evaluationData]);
  
  // Process the CSV data
  const processData = (data, questionText) => {
    // Filter out empty rows
    const filteredData = data.filter(item => item.Timestamp && item.Timestamp.trim() !== '');
    
    // Process the data to extract responses for each criterion
    const processedData = {
      question: questionText,
      responses: filteredData,
      summary: {}
    };
    
    // Create summary statistics for each criterion
    criteria.forEach(criterion => {
      const responseField = criterion.column; // Use the exact column name
      const counts = {
        'PAKTON': 0,
        'Chat GPT (4o)': 0,
        'Neither': 0,
        'I am not sure': 0
      };
      
      filteredData.forEach(item => {
        const response = item[responseField];
        if (response && counts.hasOwnProperty(response)) {
          counts[response]++;
        }
      });
      
      processedData.summary[criterion.id] = counts;
    });
    
    setEvaluationData(processedData);
  };
  
  // Prepare data for bar chart visualization
  const getBarChartData = () => {
    if (!evaluationData) return [];
    
    return criteria.map(criterion => {
      const counts = evaluationData.summary[criterion.id];
      return {
        criterion: criterion.label,
        PAKTON: counts.PAKTON,
        'GPT-4o': counts['Chat GPT (4o)'],
        Neither: counts.Neither,
        'I am not sure': counts['I am not sure']
      };
    });
  };
  
  // Prepare data for pie chart visualization for a specific criterion
  const getPieChartData = (criterionId) => {
    if (!evaluationData) return [];
    
    const counts = evaluationData.summary[criterionId];
    return [
      { name: 'PAKTON', value: counts.PAKTON, color: '#3B82F6' },
      { name: 'GPT-4o', value: counts['Chat GPT (4o)'], color: '#EF4444' },
      { name: 'Neither', value: counts.Neither, color: '#F97316' },
      { name: 'I am not sure', value: counts['I am not sure'], color: '#10B981' }
    ].filter(item => item.value > 0);
  };
  
  // Get the explanations for a specific criterion
  const getExplanationsForCriterion = (criterionId) => {
    if (!evaluationData) return [];
    
    const criterion = criteria.find(c => c.id === criterionId);
    const responseField = criterion.column; // Use the exact column name
    
    // Find the explanation field for this specific criterion
    // In the CSV structure, each criterion's explanation field follows its response field
    return evaluationData.responses.map(item => {
      // For each response item, get the choice
      const choice = item[responseField] || 'No response';
      
      // This assumes that in the headers, the explanation column comes immediately after the criterion column
      // Let's determine the position of our criterion column in the columns array
      const headers = Object.keys(item);
      const criterionIndex = headers.indexOf(responseField);
      
      // The explanation should be the next column
      const explanationField = criterionIndex >= 0 && criterionIndex < headers.length - 1 
        ? headers[criterionIndex + 1] 
        : null;
      
      return {
        choice,
        explanation: explanationField && item[explanationField] 
          ? item[explanationField] 
          : 'No explanation provided'
      };
    });
  };
  
  // Navigation controls for responses
  const handlePrevResponse = () => {
    setActiveResponse(prev => (prev > 0 ? prev - 1 : evaluationData.responses.length - 1));
  };
  
  const handleNextResponse = () => {
    setActiveResponse(prev => (prev < evaluationData.responses.length - 1 ? prev + 1 : 0));
  };
  
  // Render overview tab content
  const renderOverview = () => {
    const barChartData = getBarChartData();
    
    // Calculate total preferences
    const totalPreferences = {
      PAKTON: 0,
      'GPT-4o': 0,
      Neither: 0,
      'I am not sure': 0
    };
    
    barChartData.forEach(item => {
      totalPreferences.PAKTON += item.PAKTON || 0;
      totalPreferences['GPT-4o'] += item['GPT-4o'] || 0;
      totalPreferences.Neither += item.Neither || 0;
      totalPreferences['I am not sure'] += item['I am not sure'] || 0;
    });
    
    const totalVotes = Object.values(totalPreferences).reduce((sum, val) => sum + val, 0);
    
    const pieData = [
      { name: 'PAKTON', value: totalPreferences.PAKTON, color: '#3B82F6' },
      { name: 'GPT-4o', value: totalPreferences['GPT-4o'], color: '#EF4444' },
      { name: 'Neither', value: totalPreferences.Neither, color: '#F97316' },
      { name: 'I am not sure', value: totalPreferences['I am not sure'], color: '#10B981' }
    ].filter(item => item.value > 0);
    
    return (
      <div className="overview-tab">
        <div className="hero-section">
          <div className="back-to-dashboard">
            <button onClick={() => navigate('/human-evaluation')} className="back-button">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
              </svg>
              Back to Dashboard
            </button>
          </div>
          <h2>Overall Evaluation Results</h2>
          <div className="question-container">
            <div className="question-badge">Evaluation Question</div>
            <p className="question-text">
              "{evaluationData.question}"
            </p>
          </div>
        </div>
        {/* Redesigned Model Responses Section - Compact Version */}
        {(questionInfo?.paktonResponse || questionInfo?.gptResponse) && (
          <div className="model-responses-compact">
            <div className="response-links">
              {questionInfo?.paktonResponse && (
                <a 
                  href={questionInfo.paktonResponse}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="response-link pakton-link"
                >
                  <div className="model-icon-small pakton-icon">P</div>
                  <span>PAKTON Response</span>
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="external-link-icon">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                    <polyline points="15 3 21 3 21 9"></polyline>
                    <line x1="10" y1="14" x2="21" y2="3"></line>
                  </svg>
                </a>
              )}
              
              {questionInfo?.gptResponse && (
                <a 
                  href={questionInfo.gptResponse}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="response-link gpt-link"
                >
                  <div className="model-icon-small gpt-icon">G</div>
                  <span>GPT-4o Response</span>
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="external-link-icon">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                    <polyline points="15 3 21 3 21 9"></polyline>
                    <line x1="10" y1="14" x2="21" y2="3"></line>
                  </svg>
                </a>
              )}
            </div>
          </div>
        )}
        <div className="summary-statistics">
          <div className="summary-card total-card">
            <div className="icon-container">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <h3>Total Evaluations</h3>
            <div className="stat-value">{evaluationData.responses.length}</div>
            
            {/* Response Link */}
            {questionInfo?.responseLink && (
              <div className="response-link-container">
                <a 
                  href={questionInfo.responseLink} 
                  className="response-link" 
                  target="_blank" 
                  rel="noopener noreferrer"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="link-icon">
                    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                  </svg>
                  View Original Survey Responses
                </a>
              </div>
            )}
          </div>
          
          <div className="summary-card total-card">
            <div className="icon-container">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
              </svg>
            </div>
            <h3>Total Votes</h3>
            <div className="stat-value">{evaluationData.responses.length * criteria.length}</div>
            <div className="stat-note">Each participant voted 9 times, once for each criterion</div>
          </div>
          
          <div className="summary-card comparison-card">
            <h3>Model Preference</h3>
            <div className="model-comparison">
              <div className="model-column pakton-column">
                <div className="model-icon pakton-icon">P</div>
                <div className="model-name">PAKTON</div>
                <div className="model-percentage">{Math.round((totalPreferences.PAKTON / totalVotes) * 100)}%</div>
                <div className="votes-count">{totalPreferences.PAKTON} votes</div>
              </div>
              
              <div className="versus-divider">
                <span>VS</span>
              </div>
              
              <div className="model-column gpt-column">
                <div className="model-icon gpt-icon">G</div>
                <div className="model-name">GPT-4o</div>
                <div className="model-percentage">{Math.round((totalPreferences['GPT-4o'] / totalVotes) * 100)}%</div>
                <div className="votes-count">{totalPreferences['GPT-4o']} votes</div>
              </div>
            </div>
            
            <div className="other-preferences">
              <div className="other-item">
                <span className="other-label">Neither:</span>
                <span className="other-value" style={{ color: '#F97316' }}>{totalPreferences.Neither} votes ({Math.round((totalPreferences.Neither / totalVotes) * 100)}%)</span>
              </div>
              <div className="other-item">
                <span className="other-label">I am not sure:</span>
                <span className="other-value" style={{ color: '#10B981' }}>{totalPreferences['I am not sure']} votes ({Math.round((totalPreferences['I am not sure'] / totalVotes) * 100)}%)</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="charts-container">
          <div className="chart-card">
            <h3>Overall Model Preference</h3>
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={350}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={120}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value} votes`, 'Count']} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          <div className="chart-card criteria-chart">
            <h3>Preferences by Criterion</h3>
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={400}>
                <BarChart
                  data={barChartData}
                  barSize={15}
                  layout="vertical"
                  margin={{ top: 20, right: 30, left: 50, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    type="number"
                    domain={[0, 10]} // sets the min and max values
                    ticks={[0, 2, 4, 6, 8, 10]} // sets tick intervals
                    />
                  <YAxis dataKey="criterion" type="category" width={150} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="PAKTON" name="PAKTON" fill="#3B82F6" stackId="a" />
                  <Bar dataKey="GPT-4o" name="GPT-4o" fill="#EF4444" stackId="a" />
                  <Bar dataKey="Neither" name="Neither" fill="#F97316" stackId="a" />
                  <Bar dataKey="I am not sure" name="I am not sure" fill="#10B981" stackId="a" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
        
        {/* Added Survey Feedback Section */}
        {surveyFeedback.length > 0 && (
          <div className="feedback-section">
            <h3>Survey Feedback</h3>
            <p className="feedback-intro">Comments and feedback provided by survey participants:</p>
            
            <div className="feedback-list">
              {surveyFeedback.map((feedback, index) => (
                <div key={index} className="feedback-item">
                  <div className="feedback-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                  </div>
                  <div className="feedback-content">
                    <p>"{feedback}"</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        <div className="insights-section">
          <div className="insights-header">
            <h3>Key Insights</h3>
            <p className="insights-description">Analysis of evaluation results across all criteria</p>
          </div>
          
          <div className="insights-grid">
            {criteria.map(criterion => {
              const counts = evaluationData.summary[criterion.id];
              const total = counts.PAKTON + counts['Chat GPT (4o)'] + counts.Neither + counts['I am not sure'];
              const paktonPercent = Math.round((counts.PAKTON / total) * 100);
              const gptPercent = Math.round((counts['Chat GPT (4o)'] / total) * 100);
              
              let insightMessage = '';
              let insightClass = '';
              
              if (paktonPercent > gptPercent + 10) {
                insightMessage = `PAKTON significantly outperforms GPT-4o (${paktonPercent}% vs ${gptPercent}%)`;
                insightClass = 'pakton-win';
              } else if (gptPercent > paktonPercent + 10) {
                insightMessage = `GPT-4o significantly outperforms PAKTON (${gptPercent}% vs ${paktonPercent}%)`;
                insightClass = 'gpt-win';
              } else {
                insightMessage = `Performance is similar between models (${paktonPercent}% vs ${gptPercent}%)`;
                insightClass = 'tie';
              }
              
              return (
                <div key={criterion.id} className={`insight-card ${insightClass}`}>
                  <h4>{criterion.label}</h4>
                  <p>{insightMessage}</p>
                  <div className="comparison-bar">
                    <div 
                      className="pakton-bar" 
                      style={{width: `${paktonPercent}%`}}
                    ></div>
                    <div 
                      className="gpt-bar" 
                      style={{width: `${gptPercent}%`}}
                    ></div>
                  </div>
                  <div className="labels">
                    <span className="pakton-label">PAKTON</span>
                    <span className="gpt-label">GPT-4o</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  };
  
  // Render criterion-specific tab content
  const renderCriterionTab = (criterionId) => {
    const criterion = criteria.find(c => c.id === criterionId);
    const pieData = getPieChartData(criterionId);
    const explanations = getExplanationsForCriterion(criterionId);
    
    // Get current explanation to display
    const currentExp = explanations[activeResponse] || { choice: 'No response', explanation: 'No explanation provided' };
    
    return (
      <div className="criterion-tab">
        <div className="criterion-header">
          <h2>{criterion.label}</h2>
          <div className="criterion-instruction">
            <h4>Instructions given to evaluators:</h4>
            <p>{criterion.instruction}</p>
          </div>
        </div>
        
        <div className="charts-container">
          <div className="chart-card">
            <h3>Model Preference Distribution</h3>
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={350}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={120}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value} votes`, 'Count']} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
        
        <div className="evaluator-explanations">
          <h3>Evaluator Explanations</h3>
          <p className="explanation-intro">Browse through individual evaluator explanations for this criterion:</p>
          
          <div className="explanation-container">
            <div className="explanation-content">
              <div className={`explanation-header ${currentExp.choice.includes('PAKTON') ? 'pakton-choice' : currentExp.choice.includes('GPT') ? 'gpt-choice' : 'other-choice'}`}>
                <div className="choice-badge">{currentExp.choice}</div>
              </div>
              <div className="explanation-body">
                <p>"{currentExp.explanation}"</p>
              </div>
            </div>
            
            <div className="explanation-navigation">
              <button className="nav-button prev-button" onClick={handlePrevResponse}>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="19" y1="12" x2="5" y2="12"></line>
                  <polyline points="12 19 5 12 12 5"></polyline>
                </svg>
                <span>Previous</span>
              </button>
              <span className="nav-counter">{activeResponse + 1} of {explanations.length}</span>
              <button className="nav-button next-button" onClick={handleNextResponse}>
                <span>Next</span>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                  <polyline points="12 5 19 12 12 19"></polyline>
                </svg>
              </button>
            </div>
          </div>
        </div>
        
        <div className="criterion-analysis">
          <h3>Analysis</h3>
          <div className="analysis-content">
            {pieData[0]?.name === 'PAKTON' && pieData[0]?.value > (pieData[1]?.value || 0) ? (
              <>
                <div className="analysis-conclusion pakton-win">
                  <div className="model-icon pakton-icon">P</div>
                  <h4>PAKTON Preferred</h4>
                </div>
                <p>Most evaluators preferred PAKTON's {criterion.label.toLowerCase()} capabilities in this case. The explanations often cite PAKTON's depth and thoroughness in this criterion.</p>
              </>
            ) : pieData[0]?.name === 'GPT-4o' && pieData[0]?.value > (pieData[1]?.value || 0) ? (
              <>
                <div className="analysis-conclusion gpt-win">
                  <div className="model-icon gpt-icon">G</div>
                  <h4>GPT-4o Preferred</h4>
                </div>
                <p>Most evaluators preferred GPT-4o's {criterion.label.toLowerCase()} capabilities. Explanations frequently mention GPT-4o's clarity and conciseness in this criterion.</p>
              </>
            ) : (
              <>
                <div className="analysis-conclusion tie">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                  </svg>
                  <h4>No Clear Preference</h4>
                </div>
                <p>There is no clear preference between the models for this criterion, suggesting similar performance or high variability in evaluator preferences.</p>
              </>
            )}
          </div>
        </div>
        
        <div className="back-to-overview">
          <button onClick={() => setActiveTab('overview')} className="back-button">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="19" y1="12" x2="5" y2="12"></line>
              <polyline points="12 19 5 12 12 5"></polyline>
            </svg>
            Back to Overview
          </button>
        </div>
      </div>
    );
  };
  
  if (isLoading) {
    return (
      <div className="human-evaluation-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading human evaluation data for {questionId}...</p>
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="human-evaluation-page">
        <div className="error-container">
          <h2>Error loading data</h2>
          <p>{error}</p>
          <button onClick={() => navigate('/human-evaluation')} className="back-button">
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }
  
  if (!evaluationData) {
    return (
      <div className="human-evaluation-page">
        <div className="error-container">
          <h2>No data available</h2>
          <p>Human evaluation data could not be loaded.</p>
          <button onClick={() => navigate('/human-evaluation')} className="back-button">
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="human-evaluation-page">
      <div className="page-header">
        <h1>Human Evaluation Results</h1>
        <p className="page-description">Comparative analysis of PAKTON vs. GPT-4o based on human evaluator judgments        </p>
      </div>
      
      <div className="tabs-container">
        <div className="tabs-navigation-container">
          <button className="tab-nav-button prev-tab">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
          </button>
          
          <div className="tabs-navigation">
            <button 
              className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
              </svg>
              Overview
            </button>
            
            {criteria.map(criterion => (
              <button 
                key={criterion.id}
                className={`tab-button ${activeTab === criterion.id ? 'active' : ''}`}
                onClick={() => setActiveTab(criterion.id)}
              >
                {criterion.label}
              </button>
            ))}
          </div>
          
          <button className="tab-nav-button next-tab">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </button>
        </div>
        
        <div className="tab-content">
          {activeTab === 'overview' ? renderOverview() : renderCriterionTab(activeTab)}
        </div>
      </div>
    </div>
  );
};

export default HumanEvaluationPage;