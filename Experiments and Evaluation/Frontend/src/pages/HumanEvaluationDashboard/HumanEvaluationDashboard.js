import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Papa from 'papaparse';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  PieChart, Pie, Cell, Sector,
  LineChart, Line,
  ScatterChart, Scatter, ZAxis
} from 'recharts';

import './HumanEvaluationDashboard.css';

import { criteria } from '../../constants/evaluationCriteria';
import { availableQuestions } from '../../constants/availableQuestions';

// Custom components for visualizations
const CustomActiveShape = (props) => {
  const RADIAN = Math.PI / 180;
  const { cx, cy, midAngle, innerRadius, outerRadius, startAngle, endAngle,
    fill, payload, percent, value, name } = props;
  const sin = Math.sin(-RADIAN * midAngle);
  const cos = Math.cos(-RADIAN * midAngle);
  const sx = cx + (outerRadius + 10) * cos;
  const sy = cy + (outerRadius + 10) * sin;
  const mx = cx + (outerRadius + 30) * cos;
  const my = cy + (outerRadius + 30) * sin;
  const ex = mx + (cos >= 0 ? 1 : -1) * 22;
  const ey = my;
  const textAnchor = cos >= 0 ? 'start' : 'end';

  return (
    <g>
      <text x={cx} y={cy} dy={8} textAnchor="middle" fill={fill}>{payload.name}</text>
      <Sector
        cx={cx}
        cy={cy}
        innerRadius={innerRadius}
        outerRadius={outerRadius}
        startAngle={startAngle}
        endAngle={endAngle}
        fill={fill}
      />
      <Sector
        cx={cx}
        cy={cy}
        startAngle={startAngle}
        endAngle={endAngle}
        innerRadius={outerRadius + 6}
        outerRadius={outerRadius + 10}
        fill={fill}
      />
      <path d={`M${sx},${sy}L${mx},${my}L${ex},${ey}`} stroke={fill} fill="none" />
      <circle cx={ex} cy={ey} r={2} fill={fill} stroke="none" />
      <text x={ex + (cos >= 0 ? 1 : -1) * 12} y={ey} textAnchor={textAnchor} fill="#333">{`${name}: ${value}`}</text>
      <text x={ex + (cos >= 0 ? 1 : -1) * 12} y={ey} dy={18} textAnchor={textAnchor} fill="#999">
        {`(${(percent * 100).toFixed(2)}%)`}
      </text>
    </g>
  );
};

// Custom tooltip for the difference gauge
const DifferenceGaugeTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip">
        <p className="label">{`${payload[0].payload.name}`}</p>
        <p>{`Difference: ${payload[0].value}%`}</p>
      </div>
    );
  }
  return null;
};

const HumanEvaluationDashboard = () => {
  const [questions, setQuestions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [aggregateData, setAggregateData] = useState(null);
  const [activeIndex, setActiveIndex] = useState(0);
  const [activeChartType, setActiveChartType] = useState('votes');
  const navigate = useNavigate();

  // Function to navigate to experiment details page
  const handleExperimentDetailsClick = () => {
    navigate('/experiment-details');
  };

  useEffect(() => {
    const loadQuestionList = async () => {
      try {
        setIsLoading(true);

        setQuestions(availableQuestions);
        
        // Load all question data to compute aggregate statistics
        const allQuestionsData = await Promise.all(
          availableQuestions.map(async (question) => {
            try {
              const response = await fetch(question.filePath);
              if (!response.ok) {
                console.error(`Failed to fetch ${question.id}: ${response.status}`);
                return null;
              }
              const csvText = await response.text();
              return new Promise((resolve) => {
                Papa.parse(csvText, {
                  header: true,
                  complete: (results) => {
                    resolve({
                      questionId: question.id,
                      data: results.data.filter(item => item.Timestamp && item.Timestamp.trim() !== '')
                    });
                  },
                  error: (error) => {
                    console.error(`Error parsing ${question.id} CSV:`, error);
                    resolve(null);
                  }
                });
              });
            } catch (err) {
              console.error(`Error loading ${question.id}:`, err);
              return null;
            }
          })
        );

        // Filter out any failed loads
        const validData = allQuestionsData.filter(data => data !== null);
        
        // Process aggregate data
        processAggregateData(validData);
        setIsLoading(false);
      } catch (err) {
        console.error('Error loading questions:', err);
        setError('Failed to load questions. Please try again later.');
        setIsLoading(false);
      }
    };

    loadQuestionList();
  }, []);

  const processAggregateData = (allQuestionsData) => {
    if (!allQuestionsData.length) return;

    // Initialize aggregate counters
    const totalResponses = allQuestionsData.reduce(
      (sum, question) => sum + question.data.length, 
      0
    );
    
    // Initialize aggregate model preference counters with consistent naming
    const modelPreferences = {
      total: {
        PAKTON: 0,
        'Chat GPT (4o)': 0,
        Neither: 0,
        'I am not sure': 0
      },
      // Also track preferences by criterion
      byCriterion: {}
    };
    
    // Initialize criterion structure
    criteria.forEach(criterion => {
      modelPreferences.byCriterion[criterion.id] = {
        PAKTON: 0,
        'Chat GPT (4o)': 0,
        Neither: 0,
        'I am not sure': 0
      };
    });

    // Aggregate the data across all questions
    let validVotesCount = 0;
    
    allQuestionsData.forEach(questionData => {
      if (!questionData || !questionData.data) return;
      
      questionData.data.forEach(response => {
        // Process each criterion
        criteria.forEach(criterion => {
          const preference = response[criterion.column];
          
          if (preference && modelPreferences.byCriterion[criterion.id][preference] !== undefined) {
            modelPreferences.byCriterion[criterion.id][preference]++;
            modelPreferences.total[preference]++;
            validVotesCount++;
          }
        });
      });
    });

    // Calculate percentages and prepare data for visualization
    // Use validVotesCount instead of summing the values, to ensure accuracy
    const totalVotes = validVotesCount;
    
    // Prepare criterion comparison data for visualization
    const criterionComparison = criteria.map(criterion => {
      const counts = modelPreferences.byCriterion[criterion.id];
      const totalCriterionVotes = Object.values(counts).reduce((sum, count) => sum + count, 0);
      
      return {
        criterion: criterion.label,
        PAKTON: counts.PAKTON,
        'GPT-4o': counts['Chat GPT (4o)'],
        Neither: counts.Neither,
        'I am not sure': counts['I am not sure'],
        paktonPercent: totalCriterionVotes > 0 ? Math.round((counts.PAKTON / totalCriterionVotes) * 100) : 0,
        gptPercent: totalCriterionVotes > 0 ? Math.round((counts['Chat GPT (4o)'] / totalCriterionVotes) * 100) : 0,
        // Add difference value for visualizations
        difference: totalCriterionVotes > 0 ? 
          Math.round((counts.PAKTON / totalCriterionVotes) * 100) - 
          Math.round((counts['Chat GPT (4o)'] / totalCriterionVotes) * 100) : 0
      };
    });
    
    // Create radar chart data
    const radarData = [
      ...criterionComparison.map(item => ({
        criterion: item.criterion,
        PAKTON: item.paktonPercent,
        'GPT-4o': item.gptPercent,
      }))
    ];
    
    // Create pie chart data
    const pieData = Object.entries(modelPreferences.total).map(([name, value]) => ({
      name: name === 'Chat GPT (4o)' ? 'GPT-4o' : name,
      value
    }));
    
    // Create trend data for line chart - which shows how performance varies across criteria
    const trendData = criterionComparison.map((item, index) => ({
      name: item.criterion,
      PAKTON: item.paktonPercent,
      'GPT-4o': item.gptPercent,
      difference: item.difference
    }));
    
    // Create scatter plot data
    const scatterData = criterionComparison.map((item, index) => ({
      criterion: item.criterion,
      x: item.paktonPercent, 
      y: item.gptPercent,
      z: 10, // Size of point
      difference: item.difference
    }));
    
    // Sort by difference for highlighting strengths
    const sortedByDifference = [...criterionComparison].sort((a, b) => b.difference - a.difference);
    
    const paktonStrengths = sortedByDifference
      .filter(item => item.difference > 0)
      .slice(0, 3);
      
    const gptStrengths = sortedByDifference
      .filter(item => item.difference < 0)
      .sort((a, b) => a.difference - b.difference)
      .slice(0, 3);
    
    // Calculate overall performance 
    const paktonOverall = Object.values(modelPreferences.total).reduce((sum, count) => sum + count, 0) > 0 ?
      Math.round((modelPreferences.total.PAKTON / validVotesCount) * 100) : 0;
      
    const gptOverall = Object.values(modelPreferences.total).reduce((sum, count) => sum + count, 0) > 0 ?
      Math.round((modelPreferences.total['Chat GPT (4o)'] / validVotesCount) * 100) : 0;
    
    const overallDifference = paktonOverall - gptOverall;
    
    // Create gauge data for the difference visualization
    const gaugeData = [
      { name: 'PAKTON leads by', value: Math.max(0, overallDifference), fill: '#3b82f6' },
      { name: 'GPT-4o leads by', value: Math.abs(Math.min(0, overallDifference)), fill: '#ef4444' }
    ].filter(item => item.value > 0);

    setAggregateData({
      totalResponses,
      totalQuestions: allQuestionsData.length,
      modelPreferences,
      totalVotes,
      criterionComparison,
      radarData,
      pieData,
      trendData,
      scatterData,
      paktonStrengths,
      gptStrengths,
      paktonOverall,
      gptOverall,
      overallDifference,
      gaugeData
    });
  };

  const handleQuestionClick = (questionId) => {
    navigate(`/human-evaluation/${questionId}`);
  };
  
  // Handler for pie chart active section
  const onPieEnter = (_, index) => {
    setActiveIndex(index);
  };
  
  // Toggle between chart types
  const toggleChartType = (chartType) => {
    setActiveChartType(chartType);
  };

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading evaluation data...</p>
      </div>
    );
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  // Helper function to render the appropriate visualization based on activeChartType
  const renderVisualization = () => {
    switch (activeChartType) {
      case 'votes':
        return (
          <>
            <h3>Vote Distribution by Criterion</h3>
            <p className="chart-description">
              This chart shows the raw vote counts for each model across all evaluation criteria, aggregated from all questions.
            </p>
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={500}>
                <BarChart
                  data={aggregateData.criterionComparison}
                  margin={{
                    top: 20, right: 30, left: 20, bottom: 120,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="criterion" 
                    angle={-45} 
                    textAnchor="end"
                    height={100}
                    interval={0}
                  />
                  <YAxis 
                    label={{ value: 'Vote Count', angle: -90, position: 'insideLeft' }}
                  />
                  <Tooltip formatter={(value) => [value, 'Votes']} />
                  <Legend verticalAlign="top" wrapperStyle={{ paddingBottom: "10px" }} />
                  <Bar dataKey="PAKTON" name="PAKTON" fill="#3b82f6" />
                  <Bar dataKey="GPT-4o" name="GPT-4o" fill="#ef4444" />
                  <Bar dataKey="Neither" name="Neither" fill="#f97316" />
                  <Bar dataKey="I am not sure" name="I am not sure" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </>
        );
      case 'radar':
        return (
          <>
            <h3>Performance Comparison by Criterion (Radar)</h3>
            <p className="chart-description">
              This radar chart shows how each model performs across all evaluation criteria. 
              Greater distance from the center indicates better performance.
            </p>
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={500}>
                <RadarChart outerRadius={150} data={aggregateData.radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="criterion" />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} />
                  <Radar name="PAKTON" dataKey="PAKTON" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                  <Radar name="GPT-4o" dataKey="GPT-4o" stroke="#ef4444" fill="#ef4444" fillOpacity={0.6} />
                  <Legend />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </>
        );
      case 'pie':
        return (
          <>
            <h3>Overall Vote Distribution</h3>
            <p className="chart-description">
              This pie chart shows the distribution of all votes across the models. 
              Click on a segment to see details.
            </p>
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={400}>
                <PieChart>
                  <Pie
                    activeIndex={activeIndex}
                    activeShape={CustomActiveShape}
                    data={aggregateData.pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={70}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    onMouseEnter={onPieEnter}
                  >
                    {aggregateData.pieData.map((entry, index) => {
                      let color;
                      switch(entry.name) {
                        case 'PAKTON': color = '#3b82f6'; break;
                        case 'GPT-4o': color = '#ef4444'; break;
                        case 'Neither': color = '#f97316'; break;
                        default: color = '#10b981';
                      }
                      return <Cell key={`cell-${index}`} fill={color} />;
                    })}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </>
        );
      case 'trend':
        return (
          <>
            <h3>Performance Trend Across Criteria</h3>
            <p className="chart-description">
              This line chart shows how model performance varies across different evaluation criteria.
            </p>
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={400}>
                <LineChart
                  data={aggregateData.trendData}
                  margin={{
                    top: 20, right: 30, left: 20, bottom: 120,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                  <YAxis label={{ value: 'Performance (%)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Legend verticalAlign="top" />
                  <Line type="monotone" dataKey="PAKTON" stroke="#3b82f6" strokeWidth={2} dot={{ stroke: '#3b82f6', strokeWidth: 2, r: 4 }} />
                  <Line type="monotone" dataKey="GPT-4o" stroke="#ef4444" strokeWidth={2} dot={{ stroke: '#ef4444', strokeWidth: 2, r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </>
        );
      case 'scatter':
        return (
          <>
            <h3>Direct Performance Comparison</h3>
            <p className="chart-description">
              This scatter plot directly compares PAKTON vs GPT-4o performance for each criterion.
              Points above the diagonal line indicate PAKTON performed better, below means GPT-4o performed better.
            </p>
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={500}>
                <ScatterChart
                  margin={{
                    top: 20, right: 20, bottom: 20, left: 20,
                  }}
                >
                  <CartesianGrid />
                  <XAxis type="number" dataKey="x" name="PAKTON" domain={[0, 100]} label={{ value: 'PAKTON (%)', position: 'insideBottom', offset: -5 }} />
                  <YAxis type="number" dataKey="y" name="GPT-4o" domain={[0, 100]} label={{ value: 'GPT-4o (%)', angle: -90, position: 'insideLeft' }} />
                  <ZAxis type="number" dataKey="z" range={[60, 200]} />
                  <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                  <Scatter name="Models Comparison" data={aggregateData.scatterData} fill="#8884d8">
                    {aggregateData.scatterData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.difference > 0 ? '#3b82f6' : entry.difference < 0 ? '#ef4444' : '#f97316'} />
                    ))}
                  </Scatter>
                  {/* This is a diagonal line for reference - if point is above line, PAKTON wins, below line GPT wins */}
                  <Line type="monotone" dataKey="x" stroke="#777777" strokeWidth={1} dot={false} data={[{x: 0, y: 0}, {x: 100, y: 100}]} />
                </ScatterChart>
              </ResponsiveContainer>
              <div className="scatter-legend">
                <div className="legend-item"><span className="legend-color pakton"></span> PAKTON better</div>
                <div className="legend-item"><span className="legend-color gpt"></span> GPT-4o better</div>
                <div className="legend-item"><span className="legend-color tie"></span> Tie</div>
              </div>
            </div>
          </>
        );
      case 'strengths':
        return (
          <>
            <h3>Model Strengths Analysis</h3>
            <p className="chart-description">
              This visualization highlights the top 3 evaluation criteria where each model performed best relative to the other.
            </p>
            <div className="strengths-container">
              <div className="model-strengths pakton-strengths">
                <h4>PAKTON's Strengths</h4>
                <div className="strengths-bars">
                  {aggregateData.paktonStrengths.map((item, index) => (
                    <div className="strength-item" key={`pakton-strength-${index}`}>
                      <div className="strength-label">{item.criterion}</div>
                      <div className="strength-bar-container">
                        <div className="strength-comparison">
                          <div className="pakton-bar" style={{width: `${item.paktonPercent}%`}}></div>
                          <div className="pakton-value">{item.paktonPercent}%</div>
                        </div>
                        <div className="strength-comparison">
                          <div className="gpt-bar" style={{width: `${item.gptPercent}%`}}></div>
                          <div className="gpt-value">{item.gptPercent}%</div>
                        </div>
                      </div>
                      <div className="strength-diff positive-diff">+{item.difference}%</div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="model-strengths gpt-strengths">
                <h4>GPT-4o's Strengths</h4>
                <div className="strengths-bars">
                  {aggregateData.gptStrengths.map((item, index) => (
                    <div className="strength-item" key={`gpt-strength-${index}`}>
                      <div className="strength-label">{item.criterion}</div>
                      <div className="strength-bar-container">
                        <div className="strength-comparison">
                          <div className="pakton-bar" style={{width: `${item.paktonPercent}%`}}></div>
                          <div className="pakton-value">{item.paktonPercent}%</div>
                        </div>
                        <div className="strength-comparison">
                          <div className="gpt-bar" style={{width: `${item.gptPercent}%`}}></div>
                          <div className="gpt-value">{item.gptPercent}%</div>
                        </div>
                      </div>
                      <div className="strength-diff negative-diff">{item.difference}%</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </>
        );
      default:
        return <div>Select a visualization type</div>;
    }
  };

  return (
    <div className="human-evaluation-dashboard">
      <div className="hero-section">
        <h1>Human Evaluation Survey Results</h1>
        <p className="subtitle">
          Comparison of PAKTON and GPT-4o responses across multiple evaluation questions
        </p>
      </div>
      
      {aggregateData && (
        <div className="aggregate-stats">
          <div className="stats-cards">
            <div className="stat-card">
              <div className="stat-icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div className="stat-title">Total Questions</div>
              <div className="stat-value">{aggregateData.totalQuestions}</div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <div className="stat-title">Total Evaluations</div>
              <div className="stat-value">{aggregateData.totalResponses}</div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="stat-title">Total Evaluation Criteria</div>
              <div className="stat-value">{criteria.length}</div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
                </svg>
              </div>
              <div className="stat-title">Total Votes</div>
              <div className="stat-value">{aggregateData.totalVotes}</div>
              <div className="stat-note">Each participant voted 9 times, once for each evaluation criterion.</div>
            </div>

            <div 
              className="stat-card experiment-card" 
              onClick={handleExperimentDetailsClick}
            >
              <div className="exp-card-content">
                <div className="exp-left">
                  <div className="stat-icon experiment-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                    </svg>
                  </div>
                </div>
                <div className="exp-right">
                  <div className="stat-title">Experiment Details</div>
                  <div className="stat-value">View Full Methodology</div>
                  <div className="exp-description">
                    See the technical setup, evaluation criteria, and methodology of the human evaluation experiment in detail
                  </div>
                  <div className="view-details-btn">
                    <span>View Details</span>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Combined Chart Type Selector and Visualization Card - UPDATED */}
          <div className="visualization-card">
            <h2>Model Performance Visualizations</h2>
            <div className="chart-type-buttons">
              <button 
                className={activeChartType === 'votes' ? 'active' : ''}
                onClick={() => toggleChartType('votes')}
              >
                Vote Distribution
              </button>
              <button 
                className={activeChartType === 'radar' ? 'active' : ''}
                onClick={() => toggleChartType('radar')}
              >
                Radar Chart
              </button>
              <button 
                className={activeChartType === 'pie' ? 'active' : ''}
                onClick={() => toggleChartType('pie')}
              >
                Pie Chart
              </button>
              <button 
                className={activeChartType === 'trend' ? 'active' : ''}
                onClick={() => toggleChartType('trend')}
              >
                Trend Chart
              </button>
              <button 
                className={activeChartType === 'scatter' ? 'active' : ''}
                onClick={() => toggleChartType('scatter')}
              >
                Comparison Plot
              </button>
              <button 
                className={activeChartType === 'strengths' ? 'active' : ''}
                onClick={() => toggleChartType('strengths')}
              >
                Model Strengths
              </button>
            </div>
            
            {/* Dynamic Chart Content */}
            {renderVisualization()}
          </div>
          
          {/* Questions List */}
          <div className="questions-section">
            <h2>Evaluation Questions</h2>
            <div className="questions-grid">
                {questions.map((question, index) => (
                <div 
                    key={index} 
                    className="question-card" 
                    onClick={() => handleQuestionClick(question.id)}
                >
                    <div className="question-number">{index + 1}</div>
                    <div className="question-content">
                    <h3>{question.title}</h3>
                    <p className="question-description">"{question.description}"</p>
                    <div className="question-meta">
                        <span className="responses-count">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                        View Details
                        </span>
                    </div>
                    </div>
                </div>
                ))}
            </div>
        </div>

          <div className="overall-preference">
            <h2>Overall Model Preference</h2>
            <div className="preference-bars">
              {[
                {name: 'PAKTON', key: 'PAKTON'},
                {name: 'GPT-4o', key: 'Chat GPT (4o)'},
                {name: 'Neither', key: 'Neither'},
                {name: 'I am not sure', key: 'I am not sure'}
              ].map(model => {
                const count = aggregateData.modelPreferences.total[model.key] || 0;
                const percent = aggregateData.totalVotes > 0 
                  ? Math.round((count / aggregateData.totalVotes) * 100) 
                  : 0;
                
                let colorClass = '';
                switch(model.name) {
                  case 'PAKTON': 
                    colorClass = 'pakton-bar'; 
                    break;
                  case 'GPT-4o': 
                    colorClass = 'gpt-bar'; 
                    break;
                  case 'Neither': 
                    colorClass = 'neither-bar'; 
                    break;
                  default: 
                    colorClass = 'unsure-bar';
                }
                
                return (
                  <div key={model.name} className="preference-bar-container">
                    <div className="bar-label">
                      {model.name}
                    </div>
                    <div className="bar-container">
                      <div 
                        className={`bar ${colorClass}`} 
                        style={{width: `${percent}%`}}
                      ></div>
                      <span className="bar-value">
                        {percent}% ({count} votes)
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
          
          <div className="criteria-summary">
            <h2>Performance (Win Rate) by Criterion</h2>
            <div className="criteria-table">
              <table>
                <thead>
                  <tr>
                    <th>Criterion</th>
                    <th>PAKTON</th>
                    <th>GPT-4o</th>
                    <th>Difference</th>
                  </tr>
                </thead>
                <tbody>
                  {aggregateData.criterionComparison.map((item, index) => {
                    const diff = item.paktonPercent - item.gptPercent;
                    const diffClass = diff > 0 ? 'positive-diff' : diff < 0 ? 'negative-diff' : '';
                    
                    return (
                      <tr key={index}>
                        <td>{item.criterion}</td>
                        <td>{item.paktonPercent}%</td>
                        <td>{item.gptPercent}%</td>
                        <td className={diffClass}>
                          {diff > 0 ? '+' : ''}{diff}%
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div className="evaluation-criteria-section">
                <h3>Evaluation Criteria</h3>
                <p className="criteria-description">
                    The following criteria were used by evaluators to assess model responses:
                </p>
                
                <div className="criteria-list">
                    {criteria.map(criterion => (
                    <div key={criterion.id} className="criterion-item">
                        <h4>{criterion.label}</h4>
                        <p>{criterion.instruction}</p>
                    </div>
                    ))}
                </div>
           </div>
        </div>
      )}
    </div>
  );
};

export default HumanEvaluationDashboard;