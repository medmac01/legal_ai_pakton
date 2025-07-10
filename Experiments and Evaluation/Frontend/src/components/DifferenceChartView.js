import React from 'react';
import { ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const DifferenceChartView = ({ data }) => {
  // Sort data by difference value for better visualization
  const sortedData = [...data].sort((a, b) => b.difference - a.difference);
  
  // Calculate max absolute difference to set domain symmetrically
  const maxDiff = Math.max(...data.map(item => Math.abs(item.difference)));
  const domain = [-Math.min(maxDiff * 1.1, 0.3), Math.min(maxDiff * 1.1, 0.3)];

  return (
    <>
      <h2>Performance Difference Analysis</h2>
      <div style={{ width: '100%', height: 600 }}>
        <ResponsiveContainer>
          <ComposedChart
            data={sortedData}
            margin={{ top: 20, right: 30, left: 20, bottom: 120 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="criterion" 
              angle={-45} 
              textAnchor="end" 
              height={100} 
              tick={{ dy: 10 }}
            />
            <YAxis domain={domain} />
            <Tooltip formatter={(value) => value.toFixed(4)} />
            <Legend 
              verticalAlign="bottom" 
              height={36} 
              wrapperStyle={{ bottom: 0, paddingTop: "20px" }}
            />
            <Bar dataKey="positive" fill="#10B981" name="PAKTON Advantage" />
            <Bar dataKey="negative" fill="#EF4444" name="GPT Advantage" />
            <Line 
              type="monotone" 
              dataKey="difference" 
              stroke="#6B7280" 
              dot={{ fill: '#6B7280' }} 
              name="Net Difference" 
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </>
  );
};

export default DifferenceChartView;