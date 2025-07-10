import React, { useState, useEffect } from 'react';
import BarChartView from '../../components/BarChartView';
import RadarChartView from '../../components/RadarChartView';
import DifferenceChartView from '../../components/DifferenceChartView';
import StrengthsPanel from '../../components/StrengthsPanel';
import BoxPlotView from '../../components/BoxPlotView';
import HeatmapView from '../../components/HeatmapView';
import ScatterPlotView from '../../components/ScatterPlotView';
import ExperimentDetailsView from '../../components/ExperimentsDetailsView';
import WinPlotView from '../../components/WinPlotView';

const GevalExperimentsPage = () => {
  const [data, setData] = useState([]);
  const [diffData, setDiffData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [paktonAvg, setPaktonAvg] = useState(0);
  const [gptAvg, setGptAvg] = useState(0);
  const [paktonStrengths, setPaktonStrengths] = useState([]);
  const [gptStrengths, setGptStrengths] = useState([]);
  const [activeChart, setActiveChart] = useState('bar');
  const [rawJsonData, setRawJsonData] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setIsLoading(true);
        
        // Fetch the JSON file
        const response = await fetch('./data/geval_scores.json');
        
        if (!response.ok) {
          throw new Error(`Failed to fetch data: ${response.status}`);
        }
        
        const jsonData = await response.json();
        setRawJsonData(jsonData);
        
        // Process the data
        processData(jsonData);
        setIsLoading(false);
      } catch (err) {
        console.error('Error loading data:', err);
        setError('Failed to load data. Please check if the JSON file exists and is accessible.');
        setIsLoading(false);
      }
    };
    
    loadData();
  }, []);
  
  const processData = (jsonData) => {
    const criterionMap = {}; // { criterion: { PAKTON: total, GPT: total, count: n }, ... }

    for (const testCaseKey in jsonData) {
      const testCaseData = jsonData[testCaseKey];
  
      if (!testCaseData?.PAKTON || !testCaseData?.GPT) continue;
  
      const paktonData = testCaseData.PAKTON;
      const gptData = testCaseData.GPT;
  
      for (const criterion in paktonData) {
        if (criterion === 'output') continue;
  
        const paktonScore = paktonData[criterion]?.score;
        const gptScore = gptData[criterion]?.score;
  
        if (paktonScore === undefined || gptScore === undefined) continue;
  
        if (!criterionMap[criterion]) {
          criterionMap[criterion] = { PAKTON: 0, GPT: 0, count: 0 };
        }
  
        criterionMap[criterion].PAKTON += paktonScore;
        criterionMap[criterion].GPT += gptScore;
        criterionMap[criterion].count += 1;
      }
    }
  
    // Prepare data array for charts
    const processedData = Object.entries(criterionMap).map(([criterion, scores]) => {
      const avgPakton = scores.PAKTON / scores.count;
      const avgGpt = scores.GPT / scores.count;
      const difference = avgPakton - avgGpt;
  
      return {
        criterion,
        PAKTON: avgPakton,
        GPT: avgGpt,
        difference
      };
    });
  
    setData(processedData);
    
    // Prepare data for differential chart
    const diffDataCalc = processedData.map(item => ({
      criterion: item.criterion,
      difference: item.difference,
      positive: item.difference > 0 ? item.difference : 0,
      negative: item.difference < 0 ? item.difference : 0,
    }));
    setDiffData(diffDataCalc);
    
    // Calculate overall average scores
    const paktonAvgCalc = processedData.reduce((sum, item) => sum + item.PAKTON, 0) / processedData.length;
    const gptAvgCalc = processedData.reduce((sum, item) => sum + item.GPT, 0) / processedData.length;
    setPaktonAvg(paktonAvgCalc);
    setGptAvg(gptAvgCalc);
    
    // Calculate strengths and weaknesses
    const sortedByDifference = [...processedData].sort((a, b) => b.difference - a.difference);

    const paktonStrengthsOnly = sortedByDifference
      .filter(item => item.difference > 0)
      .sort((a, b) => b.difference - a.difference)
      .slice(0, 3);

    setPaktonStrengths(paktonStrengthsOnly);

    const gptStrengthsOnly = sortedByDifference
      .filter(item => item.difference < 0) // GPT must outperform PAKTON
      .sort((a, b) => a.difference - b.difference) // Most negative first
      .slice(0, 3);

    setGptStrengths(gptStrengthsOnly);
  };

  if (isLoading) {
    return <div className="loading">Loading data...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="geval-page">
      <h1>PAKTON vs GPT-4o Performance Comparison using G-Eval Framework</h1>
      
      {/* Chart type selector */}
      <div className="chart-selector">
        <button 
          className={activeChart === 'bar' ? 'active' : ''} 
          onClick={() => setActiveChart('bar')}
        >
          Bar Chart
        </button>
        <button 
          className={activeChart === 'radar' ? 'active' : ''} 
          onClick={() => setActiveChart('radar')}
        >
          Radar Chart
        </button>
        <button 
          className={activeChart === 'diff' ? 'active' : ''} 
          onClick={() => setActiveChart('diff')}
        >
          Difference Chart
        </button>
        <button 
          className={activeChart === 'box' ? 'active' : ''} 
          onClick={() => setActiveChart('box')}
        >
          Box Plot
        </button>
        <button 
          className={activeChart === 'heatmap' ? 'active' : ''} 
          onClick={() => setActiveChart('heatmap')}
        >
          Heatmap
        </button>
        <button 
          className={activeChart === 'scatter' ? 'active' : ''} 
          onClick={() => setActiveChart('scatter')}
        >
          Scatter Plot
        </button>
        <button
          className={activeChart === 'win' ? 'active' : ''}
          onClick={() => setActiveChart('win')}
        >
          Win Plot
        </button>
        <button 
          className={activeChart === 'experiment' ? 'active' : ''} 
          onClick={() => setActiveChart('experiment')}
        >
          Experiment Details
        </button>
      </div>
      
      {/* Overall scores summary */}
      <div className="scores-summary">
        <h2>Overall Average Scores</h2>
        <div className="averages">
          <div className="score pakton">
            <div className="value">{paktonAvg.toFixed(4)}</div>
            <div className="label">PAKTON</div>
          </div>
          <div className="score gpt">
            <div className="value">{gptAvg.toFixed(4)}</div>
            <div className="label">GPT</div>
          </div>
          <div className="score difference">
            <div className="value">
              {paktonAvg > gptAvg ? '+' : ''}{(paktonAvg - gptAvg).toFixed(4)}
            </div>
            <div className="label">Difference</div>
          </div>
        </div>
      </div>
      
      {/* Chart visualization */}
      <div className="chart-container">
        {activeChart === 'bar' && <BarChartView data={data} />}
        {activeChart === 'radar' && <RadarChartView data={data} />}
        {activeChart === 'diff' && <DifferenceChartView data={diffData} />}
        {activeChart === 'box' && <BoxPlotView data={data} />}
        {activeChart === 'heatmap' && <HeatmapView data={data} />}
        {activeChart === 'scatter' && <ScatterPlotView data={data} />}
        {activeChart === 'win' && <WinPlotView />}
        {activeChart === 'experiment' && <ExperimentDetailsView jsonData={rawJsonData} />}
      </div>
      
      {/* Strengths panels */}
      {['bar', 'radar', 'diff', 'box'].includes(activeChart) && (
        <StrengthsPanel paktonStrengths={paktonStrengths} gptStrengths={gptStrengths} />
      )}
    </div>
  );
};

export default GevalExperimentsPage;