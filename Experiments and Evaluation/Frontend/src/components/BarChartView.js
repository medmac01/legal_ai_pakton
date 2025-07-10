import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const BarChartView = ({ data }) => {
  return (
    <>
      <h2>Score Comparison by Criterion</h2>
      <div style={{ width: '100%', height: 600 }}>
        <ResponsiveContainer>
          <BarChart
            data={data}
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
            <YAxis domain={[0, 1]} />
            <Tooltip formatter={(value) => value.toFixed(4)} />
            <Legend 
              verticalAlign="bottom" 
              height={36} 
              wrapperStyle={{ bottom: 0, paddingTop: "20px" }}
            />
            <Bar dataKey="PAKTON" fill="#3B82F6" name="PAKTON" />
            <Bar dataKey="GPT" fill="#EF4444" name="GPT" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </>
  );
};

export default BarChartView;