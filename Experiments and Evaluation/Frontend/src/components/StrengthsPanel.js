import React from 'react';

const StrengthsPanel = ({ paktonStrengths, gptStrengths }) => {
  return (
    <div className="strengths-container">
      <div className="strengths-panel pakton-panel">
        <h3>PAKTON's Top Strengths</h3>
        {paktonStrengths.map((item, index) => (
          <div key={index} className="strength-item">
            <div className="strength-criterion">{item.criterion}</div>
            <div className="strength-stats">
              <span className="strength-score">Score: {item.PAKTON.toFixed(4)}</span>
              <span className="strength-difference">+{item.difference.toFixed(4)} vs GPT</span>
            </div>
          </div>
        ))}
      </div>
      
      <div className="strengths-panel gpt-panel">
        <h3>GPT's Top Strengths</h3>
        {gptStrengths.map((item, index) => (
          <div key={index} className="strength-item">
            <div className="strength-criterion">{item.criterion}</div>
            <div className="strength-stats">
              <span className="strength-score">Score: {item.GPT.toFixed(4)}</span>
              <span className="strength-difference">+{Math.abs(item.difference).toFixed(4)} vs PAKTON</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StrengthsPanel;