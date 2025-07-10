import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const WinPlotView = () => {
  const [winData, setWinData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [totalTestCases, setTotalTestCases] = useState(0);

  useEffect(() => {
    const loadData = async () => {
      try {
        setIsLoading(true);
        const response = await fetch('./data/geval_scores.json');
        if (!response.ok) {
          throw new Error(`Failed to fetch data: ${response.status}`);
        }
        const jsonData = await response.json();
        processWinData(jsonData);
        setIsLoading(false);
      } catch (err) {
        console.error('Error loading data:', err);
        setError('Failed to load data. Please check if the JSON file exists and is accessible.');
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  const processWinData = (jsonData) => {
    const testCases = Object.keys(jsonData);
    setTotalTestCases(testCases.length);

    const criterionWinMap = {};

    for (const testCaseKey of testCases) {
      const testCaseData = jsonData[testCaseKey];
      if (!testCaseData?.PAKTON || !testCaseData?.GPT) continue;

      const paktonData = testCaseData.PAKTON;
      const gptData = testCaseData.GPT;

      for (const criterion in paktonData) {
        if (criterion === 'output') continue;

        const paktonScore = paktonData[criterion]?.score;
        const gptScore = gptData[criterion]?.score;
        if (paktonScore === undefined || gptScore === undefined) continue;

        if (!criterionWinMap[criterion]) {
          criterionWinMap[criterion] = {
            paktonWins: 0,
            gptWins: 0,
            total: 0,
          };
        }

        if (paktonScore > gptScore) {
          criterionWinMap[criterion].paktonWins++;
          criterionWinMap[criterion].total++;
        } else if (gptScore > paktonScore) {
          criterionWinMap[criterion].gptWins++;
          criterionWinMap[criterion].total++;
        }
        // Ties are ignored
      }
    }

    const processedData = Object.entries(criterionWinMap).map(([criterion, counts]) => ({
      criterion,
      paktonWins: counts.paktonWins,
      gptWins: counts.gptWins,
      paktonWinPercentage: (counts.paktonWins / counts.total) * 100,
      gptWinPercentage: (counts.gptWins / counts.total) * 100,
    }));

    processedData.sort((a, b) => b.paktonWinPercentage - a.paktonWinPercentage);

    setWinData(processedData);
  };

  const tooltipFormatter = (value, name) => {
    // const label = name === 'paktonWins' ? 'PAKTON Wins' : 'GPT Wins';
    const label = name;
    return [`${value} (${(value / totalTestCases * 100).toFixed(1)}%)`, label];
  };

  if (isLoading) {
    return <div className="loading">Loading win count data...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <>
      <h2>Win Count Analysis by Criterion</h2>
      <p className="chart-description">
        This chart shows for each criterion, how many times PAKTON outperformed GPT across all test cases, 
        and vice versa. Out of {totalTestCases} total test cases, the bars show the count of wins for each model.
      </p>

      <div style={{ width: '100%', height: 600 }}>
        <ResponsiveContainer>
          <BarChart
            data={winData}
            margin={{ top: 20, right: 30, left: 20, bottom: 120 }}
            layout="vertical"
          >
            <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
            <XAxis
              type="number"
              domain={[0, totalTestCases]}
              allowDecimals={false}
            />
            <YAxis
              dataKey="criterion"
              type="category"
              width={150}
              tick={{ fontSize: 12 }}
            />
            <Tooltip formatter={tooltipFormatter} />
            <Legend />
            <Bar dataKey="paktonWins" stackId="a" fill="#3B82F6" name="PAKTON Wins" />
            <Bar dataKey="gptWins" stackId="a" fill="#EF4444" name="GPT Wins" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="win-count-table">
        <h3>Detailed Win Count by Criterion</h3>
        <table>
          <thead>
            <tr>
              <th>Criterion</th>
              <th>PAKTON Wins</th>
              <th>GPT Wins</th>
              <th>PAKTON Win %</th>
            </tr>
          </thead>
          <tbody>
            {winData.map((item, index) => (
              <tr key={index}>
                <td>{item.criterion}</td>
                <td className="pakton-cell">{item.paktonWins}</td>
                <td className="gpt-cell">{item.gptWins}</td>
                <td className={
                  item.paktonWinPercentage > 50
                    ? 'pakton-cell'
                    : item.paktonWinPercentage < 50
                    ? 'gpt-cell'
                    : ''
                }>
                  {item.paktonWinPercentage.toFixed(1)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <style>{`
        .chart-description {
          margin-bottom: 20px;
          color: #64748b;
        }

        .win-count-table {
          margin-top: 40px;
          overflow-x: auto;
        }

        .win-count-table table {
          width: 100%;
          border-collapse: collapse;
          margin-top: 15px;
        }

        .win-count-table th,
        .win-count-table td {
          padding: 8px 12px;
          border: 1px solid #e2e8f0;
          text-align: center;
        }

        .win-count-table th {
          background-color: #f1f5f9;
          font-weight: 600;
        }

        .win-count-table th:first-child,
        .win-count-table td:first-child {
          text-align: left;
        }

        .pakton-cell {
          color: #3B82F6;
          font-weight: 500;
        }

        .gpt-cell {
          color: #EF4444;
          font-weight: 500;
        }

        .win-count-table tr:hover {
          background-color: #f8fafc;
        }
      `}</style>
    </>
  );
};

export default WinPlotView;