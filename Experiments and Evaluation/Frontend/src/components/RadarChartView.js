import React from 'react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend, Tooltip, ResponsiveContainer } from 'recharts';

const RadarChartView = ({ data }) => {
  return (
    <>
      <h2>Performance Profile Comparison</h2>
      <div style={{ width: '100%', height: 600 }}>
        <ResponsiveContainer>
          <RadarChart 
            cx="50%" 
            cy="50%" 
            outerRadius="80%" 
            data={data}
          >
            <PolarGrid />
            <PolarAngleAxis 
              dataKey="criterion" 
              tick={{ fontSize: 12 }}
            />
            <PolarRadiusAxis 
              angle={30} 
              domain={[0, 1]} 
              tickCount={6}
            />
            <Radar 
              name="PAKTON" 
              dataKey="PAKTON" 
              stroke="#3B82F6" 
              fill="#3B82F6" 
              fillOpacity={0.5} 
            />
            <Radar 
              name="GPT" 
              dataKey="GPT" 
              stroke="#EF4444" 
              fill="#EF4444" 
              fillOpacity={0.5} 
            />
            <Legend />
            <Tooltip formatter={(value) => value.toFixed(4)} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </>
  );
};

export default RadarChartView;