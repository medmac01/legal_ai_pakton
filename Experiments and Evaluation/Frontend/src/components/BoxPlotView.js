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
  Rectangle
} from 'recharts';

// Custom Box Plot Component for Recharts
const BoxPlot = props => {
  const { x, y, width, height, min, max, median, q1, q3, color, name } = props;
  
  return (
    <g>
      {/* Vertical Line from Min to Max */}
      <line
        x1={x + width / 2}
        y1={y + height - max * height}
        x2={x + width / 2}
        y2={y + height - min * height}
        stroke={color}
        strokeWidth={1}
      />
      
      {/* Box from Q1 to Q3 */}
      <Rectangle
        x={x}
        y={y + height - q3 * height}
        width={width}
        height={(q3 - q1) * height}
        fill={color}
        fillOpacity={0.5}
        stroke={color}
      />
      
      {/* Median Line */}
      <line
        x1={x}
        y1={y + height - median * height}
        x2={x + width}
        y2={y + height - median * height}
        stroke={color}
        strokeWidth={2}
      />
      
      {/* Min Line (Whisker) */}
      <line
        x1={x + width * 0.25}
        y1={y + height - min * height}
        x2={x + width * 0.75}
        y2={y + height - min * height}
        stroke={color}
        strokeWidth={1}
      />
      
      {/* Max Line (Whisker) */}
      <line
        x1={x + width * 0.25}
        y1={y + height - max * height}
        x2={x + width * 0.75}
        y2={y + height - max * height}
        stroke={color}
        strokeWidth={1}
      />
      
      {/* Label for the box plot */}
      <text
        x={x + width / 2}
        y={y + height - max * height - 10}
        textAnchor="middle"
        fill={color}
        fontSize={10}
      >
        {name}
      </text>
    </g>
  );
};

// Custom Tooltip formatter
const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="custom-tooltip" style={{ 
        backgroundColor: '#fff', 
        padding: '10px', 
        border: '1px solid #ccc' 
      }}>
        <p><strong>{data.name}</strong></p>
        <p>Median: {data.median.toFixed(4)}</p>
        <p>Q1: {data.q1.toFixed(4)}</p>
        <p>Q3: {data.q3.toFixed(4)}</p>
        <p>Min: {data.min.toFixed(4)}</p>
        <p>Max: {data.max.toFixed(4)}</p>
        <p>Mean: {data.mean.toFixed(4)}</p>
      </div>
    );
  }

  return null;
};

const BoxPlotView = ({ data }) => {
  // Prepare data for box plot visualization
  const boxPlotData = useMemo(() => {
    // Extract all PAKTON scores and GPT scores
    const paktonScores = data.map(item => item.PAKTON);
    const gptScores = data.map(item => item.GPT);
    
    // Calculate statistics for PAKTON
    const paktonSorted = [...paktonScores].sort((a, b) => a - b);
    const paktonMin = paktonSorted[0];
    const paktonMax = paktonSorted[paktonSorted.length - 1];
    const paktonMedian = paktonSorted[Math.floor(paktonSorted.length / 2)];
    const paktonQ1 = paktonSorted[Math.floor(paktonSorted.length / 4)];
    const paktonQ3 = paktonSorted[Math.floor(3 * paktonSorted.length / 4)];
    const paktonMean = paktonScores.reduce((a, b) => a + b, 0) / paktonScores.length;
    
    // Calculate statistics for GPT
    const gptSorted = [...gptScores].sort((a, b) => a - b);
    const gptMin = gptSorted[0];
    const gptMax = gptSorted[gptSorted.length - 1];
    const gptMedian = gptSorted[Math.floor(gptSorted.length / 2)];
    const gptQ1 = gptSorted[Math.floor(gptSorted.length / 4)];
    const gptQ3 = gptSorted[Math.floor(3 * gptSorted.length / 4)];
    const gptMean = gptScores.reduce((a, b) => a + b, 0) / gptScores.length;
    
    return [
      {
        x: 1,
        y: 0,
        name: 'PAKTON',
        min: paktonMin,
        max: paktonMax,
        median: paktonMedian,
        q1: paktonQ1,
        q3: paktonQ3,
        mean: paktonMean,
        color: '#3B82F6'
      },
      {
        x: 2,
        y: 0,
        name: 'GPT',
        min: gptMin,
        max: gptMax,
        median: gptMedian,
        q1: gptQ1,
        q3: gptQ3,
        mean: gptMean,
        color: '#EF4444'
      }
    ];
  }, [data]);
  
  // List of statistics for the summary table
  const statisticsList = [
    { name: 'Minimum', pakton: boxPlotData[0].min, gpt: boxPlotData[1].min },
    { name: 'Q1 (25th percentile)', pakton: boxPlotData[0].q1, gpt: boxPlotData[1].q1 },
    { name: 'Median', pakton: boxPlotData[0].median, gpt: boxPlotData[1].median },
    { name: 'Q3 (75th percentile)', pakton: boxPlotData[0].q3, gpt: boxPlotData[1].q3 },
    { name: 'Maximum', pakton: boxPlotData[0].max, gpt: boxPlotData[1].max },
    { name: 'Mean', pakton: boxPlotData[0].mean, gpt: boxPlotData[1].mean }
  ];

  return (
    <>
      <h2>Score Distribution Analysis</h2>
      <div style={{ width: '100%', height: 400 }}>
        <ResponsiveContainer>
          <ScatterChart
            margin={{ top: 40, right: 40, bottom: 20, left: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              type="number" 
              dataKey="x" 
              name="Model" 
              domain={[0, 3]}
              ticks={[1, 2]} 
              tickFormatter={(value) => {
                if (value === 1) return 'PAKTON';
                if (value === 2) return 'GPT';
                return '';
              }}
            />
            <YAxis 
              type="number" 
              dataKey="y" 
              name="Score" 
              domain={[0, 1]} 
              tickCount={6}
            />
            <ZAxis type="number" range={[100]} />
            <Tooltip content={<CustomTooltip />} />
            <Scatter 
              data={boxPlotData} 
              shape={props => (
                <BoxPlot
                  {...props}
                  x={props.cx - 40}
                  y={props.cy - 300}
                  width={80}
                  height={300}
                  min={props.payload.min}
                  max={props.payload.max}
                  median={props.payload.median}
                  q1={props.payload.q1}
                  q3={props.payload.q3}
                  color={props.payload.color}
                  name={props.payload.name}
                />
              )}
            />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
      
      {/* Summary Statistics Table */}
      <div className="stats-table-container">
        <h3>Summary Statistics</h3>
        <table className="stats-table">
          <thead>
            <tr>
              <th>Statistic</th>
              <th>PAKTON</th>
              <th>GPT</th>
              <th>Difference</th>
            </tr>
          </thead>
          <tbody>
            {statisticsList.map((stat, index) => (
              <tr key={index}>
                <td>{stat.name}</td>
                <td>{stat.pakton.toFixed(4)}</td>
                <td>{stat.gpt.toFixed(4)}</td>
                <td className={stat.pakton > stat.gpt ? 'positive' : 'negative'}>
                  {(stat.pakton - stat.gpt).toFixed(4)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <style>{`
        .stats-table-container {
          margin-top: 30px;
          overflow-x: auto;
        }
        
        .stats-table {
          width: 100%;
          border-collapse: collapse;
          margin-top: 10px;
        }
        
        .stats-table th, .stats-table td {
          border: 1px solid #ddd;
          padding: 8px;
          text-align: right;
        }
        
        .stats-table th:first-child, .stats-table td:first-child {
          text-align: left;
        }
        
        .stats-table th {
          background-color: #f2f2f2;
        }
        
        .stats-table tr:nth-child(even) {
          background-color: #f9f9f9;
        }
        
        .stats-table .positive {
          color: #10B981;
        }
        
        .stats-table .negative {
          color: #EF4444;
        }
      `}</style>
    </>
  );
};

export default BoxPlotView;