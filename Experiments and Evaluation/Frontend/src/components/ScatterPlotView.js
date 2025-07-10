import React, { useMemo } from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Label
} from 'recharts';

const ScatterPlotView = ({ data }) => {
  // Calculate correlation between PAKTON and GPT scores
  const correlation = useMemo(() => {
    if (!data || data.length === 0) return 0;
    
    const n = data.length;
    const paktonScores = data.map(item => item.PAKTON);
    const gptScores = data.map(item => item.GPT);
    
    // Calculate means
    const paktonMean = paktonScores.reduce((a, b) => a + b, 0) / n;
    const gptMean = gptScores.reduce((a, b) => a + b, 0) / n;
    
    // Calculate covariance and variances
    let covariance = 0;
    let paktonVariance = 0;
    let gptVariance = 0;
    
    for (let i = 0; i < n; i++) {
      const paktonDiff = paktonScores[i] - paktonMean;
      const gptDiff = gptScores[i] - gptMean;
      covariance += paktonDiff * gptDiff;
      paktonVariance += paktonDiff * paktonDiff;
      gptVariance += gptDiff * gptDiff;
    }
    
    // Calculate Pearson correlation coefficient
    const correlation = covariance / (Math.sqrt(paktonVariance) * Math.sqrt(gptVariance));
    return correlation;
  }, [data]);
  
  // Transform data for scatter plot
  const scatterData = data.map(item => ({
    x: item.PAKTON,
    y: item.GPT,
    criterion: item.criterion,
    difference: item.difference
  }));
  
  // Custom tooltip for the scatter plot
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="custom-tooltip" style={{ 
          backgroundColor: '#fff', 
          padding: '10px', 
          border: '1px solid #ccc',
          borderRadius: '4px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <p style={{ fontWeight: 'bold', marginBottom: '5px' }}>{data.criterion}</p>
          <p>PAKTON: {data.x.toFixed(4)}</p>
          <p>GPT: {data.y.toFixed(4)}</p>
          <p style={{ 
            color: data.difference > 0 ? '#10B981' : '#EF4444',
            marginTop: '5px'
          }}>
            Difference: {data.difference > 0 ? '+' : ''}{data.difference.toFixed(4)}
          </p>
        </div>
      );
    }
    return null;
  };
  
  // Function to determine the color of each point based on which model performed better
  const getPointColor = (entry) => {
    return entry.difference > 0 ? '#3B82F6' : '#EF4444';
  };
  
  // Calculate min and max values for the axes with some padding
  const domainValues = useMemo(() => {
    if (!data || data.length === 0) return { min: 0, max: 1 };
    
    const allScores = [...data.map(item => item.PAKTON), ...data.map(item => item.GPT)];
    const min = Math.floor(Math.min(...allScores) * 10) / 10;
    const max = Math.ceil(Math.max(...allScores) * 10) / 10;
    
    return { min, max };
  }, [data]);

  // Create regression line data
  const regressionLine = useMemo(() => {
    if (!data || data.length === 0) return [];
    
    const paktonScores = data.map(item => item.PAKTON);
    const gptScores = data.map(item => item.GPT);
    
    // Calculate means
    const paktonMean = paktonScores.reduce((a, b) => a + b, 0) / paktonScores.length;
    const gptMean = gptScores.reduce((a, b) => a + b, 0) / gptScores.length;
    
    // Calculate slope and intercept for regression line
    let numerator = 0;
    let denominator = 0;
    
    for (let i = 0; i < paktonScores.length; i++) {
      numerator += (paktonScores[i] - paktonMean) * (gptScores[i] - gptMean);
      denominator += Math.pow(paktonScores[i] - paktonMean, 2);
    }
    
    const slope = numerator / denominator;
    const intercept = gptMean - slope * paktonMean;
    
    // Create line points
    return [
      { x: domainValues.min, y: slope * domainValues.min + intercept },
      { x: domainValues.max, y: slope * domainValues.max + intercept }
    ];
  }, [data, domainValues]);

  return (
    <>
      <h2>Model Correlation Analysis</h2>
      <div className="correlation-info">
        <p>Pearson Correlation Coefficient: <strong>{correlation.toFixed(4)}</strong></p>
        <p className="correlation-interpretation">
          {correlation > 0.7 ? 'Strong positive correlation: Both models tend to perform well or poorly on the same criteria.' :
          correlation > 0.4 ? 'Moderate positive correlation: Some alignment in model performance across criteria.' :
          correlation > 0 ? 'Weak positive correlation: Limited alignment in model performance.' :
          correlation < -0.4 ? 'Negative correlation: Models tend to perform in opposite ways on the same criteria.' :
          'Little to no correlation: No consistent relationship between model performances.'}
        </p>
      </div>
      
      <div style={{ width: '100%', height: 500 }}>
        <ResponsiveContainer>
          <ScatterChart
            margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
          >
            <CartesianGrid />
            <XAxis 
              type="number" 
              dataKey="x" 
              name="PAKTON Score" 
              domain={[domainValues.min, domainValues.max]}
              label={{ value: 'PAKTON Score', position: 'bottom', offset: 5 }}
            />
            <YAxis 
              type="number" 
              dataKey="y" 
              name="GPT Score" 
              domain={[domainValues.min, domainValues.max]}
              label={{ value: 'GPT Score', angle: -90, position: 'left', offset: 10 }}
            />
            <ZAxis range={[60, 60]} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            
            {/* Reference diagonal line (y=x) */}
            <ReferenceLine 
              segment={[
                { x: domainValues.min, y: domainValues.min },
                { x: domainValues.max, y: domainValues.max }
              ]} 
              stroke="#666"
              strokeDasharray="3 3" 
            >
              <Label value="Equal Performance" position="insideBottomRight" offset={-20} />
            </ReferenceLine>
            
            {/* Regression Line */}
            <ReferenceLine 
              segment={regressionLine} 
              stroke="#7c3aed"
              strokeWidth={2}
            >
              <Label value="Regression Line" position="insideTopRight" offset={-20} />
            </ReferenceLine>
            
            {/* Scatter Points */}
            <Scatter 
              name="Score Comparison" 
              data={scatterData} 
              fill="#8884d8"
              shape="circle"
              legendType="none"
            >
              {scatterData.map((entry, index) => (
                <cell key={`cell-${index}`} fill={getPointColor(entry)} />
              ))}
            </Scatter>
            
            {/* Legend for point colors */}
            <Legend 
              payload={[
                { value: 'PAKTON Better', type: 'circle', color: '#3B82F6' },
                { value: 'GPT Better', type: 'circle', color: '#EF4444' }
              ]}
            />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
      
      <div className="quadrant-explanation">
        <h3>How to Interpret the Scatter Plot:</h3>
        <ul>
          <li><strong>Points above the diagonal line:</strong> GPT performs better for these criteria</li>
          <li><strong>Points below the diagonal line:</strong> PAKTON performs better for these criteria</li>
          <li><strong>Distance from line:</strong> Magnitude of performance difference</li>
          <li><strong>Regression line:</strong> Shows the overall relationship trend between model scores</li>
          <li><strong>Point clustering:</strong> Indicates consistency in relative performance</li>
        </ul>
      </div>
      
      <style>{`
        .correlation-info {
          background-color: #f8f9fa;
          padding: 15px;
          border-radius: 8px;
          margin-bottom: 20px;
        }
        
        .correlation-interpretation {
          font-style: italic;
          color: #666;
          margin-top: 5px;
        }
        
        .quadrant-explanation {
          margin-top: 30px;
          background-color: #f8f9fa;
          padding: 15px;
          border-radius: 8px;
        }
        
        .quadrant-explanation h3 {
          margin-top: 0;
          margin-bottom: 10px;
        }
        
        .quadrant-explanation ul {
          padding-left: 20px;
        }
        
        .quadrant-explanation li {
          margin-bottom: 8px;
        }
      `}</style>
    </>
  );
};

export default ScatterPlotView;