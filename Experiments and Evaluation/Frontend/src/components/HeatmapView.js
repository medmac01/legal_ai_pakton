import React from 'react';
import { ResponsiveContainer, Tooltip } from 'recharts';

const HeatmapView = ({ data }) => {
  // Cell color calculation based on value
  const getCellColor = (value, isForPakton) => {
    if (isForPakton) {
      // Color scale from light blue to dark blue for PAKTON
      const intensity = Math.min(Math.max(value, 0), 1);
      const r = Math.round(59 + (184 - 59) * (1 - intensity));
      const g = Math.round(130 + (246 - 130) * (1 - intensity));
      const b = Math.round(246 - 50 * (1 - intensity));
      return `rgb(${r}, ${g}, ${b})`;
    } else {
      // Color scale from light red to dark red for GPT
      const intensity = Math.min(Math.max(value, 0), 1);
      const r = Math.round(239 - 50 * (1 - intensity));
      const g = Math.round(68 + (180 - 68) * (1 - intensity));
      const b = Math.round(68 + (180 - 68) * (1 - intensity));
      return `rgb(${r}, ${g}, ${b})`;
    }
  };

  // Calculate difference color
  const getDifferenceColor = (value) => {
    if (value > 0) {
      // Positive difference (PAKTON better) - green gradient
      const intensity = Math.min(Math.abs(value) * 5, 1); // Scale for visibility
      return `rgba(16, 185, 129, ${intensity})`;
    } else {
      // Negative difference (GPT better) - red gradient
      const intensity = Math.min(Math.abs(value) * 5, 1); // Scale for visibility
      return `rgba(239, 68, 68, ${intensity})`;
    }
  };

  return (
    <>
      <h2>Performance Heatmap</h2>
      <p className="chart-note">Color intensity indicates performance level for each criterion.</p>
      
      <div className="heatmap-container">
        <div className="heatmap-header">
          <div className="heatmap-title">Criterion</div>
          <div className="heatmap-title pakton-title">PAKTON</div>
          <div className="heatmap-title gpt-title">GPT</div>
          <div className="heatmap-title diff-title">Difference</div>
        </div>
        
        {data.map((item, index) => (
          <div key={index} className="heatmap-row">
            <div className="heatmap-criterion">{item.criterion}</div>
            
            <div 
              className="heatmap-cell pakton-cell" 
              style={{ backgroundColor: getCellColor(item.PAKTON, true) }}
              title={`PAKTON: ${item.PAKTON.toFixed(4)}`}
            >
              {item.PAKTON.toFixed(4)}
            </div>
            
            <div 
              className="heatmap-cell gpt-cell" 
              style={{ backgroundColor: getCellColor(item.GPT, false) }}
              title={`GPT: ${item.GPT.toFixed(4)}`}
            >
              {item.GPT.toFixed(4)}
            </div>
            
            <div 
              className="heatmap-cell diff-cell" 
              style={{ backgroundColor: getDifferenceColor(item.difference) }}
              title={`Difference: ${item.difference.toFixed(4)}`}
            >
              {item.difference > 0 ? '+' : ''}{item.difference.toFixed(4)}
            </div>
          </div>
        ))}
        
        {/* Legend for the heatmap */}
        <div className="heatmap-legend">
          <div className="legend-section">
            <div className="legend-title">PAKTON Score</div>
            <div className="legend-gradient pakton-gradient"></div>
            <div className="legend-labels">
              <span>0</span>
              <span>0.5</span>
              <span>1</span>
            </div>
          </div>
          
          <div className="legend-section">
            <div className="legend-title">GPT Score</div>
            <div className="legend-gradient gpt-gradient"></div>
            <div className="legend-labels">
              <span>0</span>
              <span>0.5</span>
              <span>1</span>
            </div>
          </div>
          
          <div className="legend-section">
            <div className="legend-title">Difference</div>
            <div className="legend-gradient diff-gradient"></div>
            <div className="legend-labels">
              <span>GPT better</span>
              <span>Equal</span>
              <span>PAKTON better</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* CSS for the heatmap - to be added to App.css */}
      <style>{`
        .heatmap-container {
          display: flex;
          flex-direction: column;
          width: 100%;
          border-radius: 4px;
          overflow: hidden;
          font-size: 14px;
        }
        
        .heatmap-header {
          display: flex;
          background-color: #f3f4f6;
          font-weight: bold;
        }
        
        .heatmap-title {
          flex: 1;
          padding: 12px;
          text-align: center;
        }
        
        .heatmap-title:first-child {
          flex: 2;
          text-align: left;
        }
        
        .pakton-title {
          color: #3B82F6;
        }
        
        .gpt-title {
          color: #EF4444;
        }
        
        .diff-title {
          color: #6B7280;
        }
        
        .heatmap-row {
          display: flex;
          border-bottom: 1px solid #e5e7eb;
        }
        
        .heatmap-row:last-child {
          border-bottom: none;
        }
        
        .heatmap-criterion {
          flex: 2;
          padding: 10px 12px;
          background-color: #f9fafb;
          font-weight: 500;
        }
        
        .heatmap-cell {
          flex: 1;
          padding: 10px 12px;
          text-align: center;
          color: white;
          text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
        }
        
        .diff-cell {
          color: black;
          text-shadow: none;
        }
        
        .heatmap-legend {
          display: flex;
          margin-top: 20px;
          justify-content: space-around;
        }
        
        .legend-section {
          display: flex;
          flex-direction: column;
          align-items: center;
          margin: 0 10px;
        }
        
        .legend-title {
          font-weight: 500;
          margin-bottom: 5px;
        }
        
        .legend-gradient {
          height: 10px;
          width: 150px;
          border-radius: 2px;
          margin-bottom: 5px;
        }
        
        .pakton-gradient {
          background: linear-gradient(to right, rgba(59, 130, 246, 0.2), rgba(59, 130, 246, 1));
        }
        
        .gpt-gradient {
          background: linear-gradient(to right, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 1));
        }
        
        .diff-gradient {
          background: linear-gradient(to right, rgba(239, 68, 68, 1), rgba(229, 231, 235, 1), rgba(16, 185, 129, 1));
        }
        
        .legend-labels {
          display: flex;
          justify-content: space-between;
          width: 100%;
          font-size: 12px;
          color: #6B7280;
        }
        
        .chart-note {
          color: #6B7280;
          font-size: 0.9rem;
          margin-top: -10px;
          margin-bottom: 20px;
        }
      `}</style>
    </>
  );
};

export default HeatmapView;