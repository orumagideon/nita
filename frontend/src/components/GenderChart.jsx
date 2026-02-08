import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';

export const GenderChart = ({ data }) => {
  const chartData = useMemo(() => {
    if (!data) return [];
    
    const labels = Object.keys(data).filter(key => data[key] > 0);
    const values = labels.map(key => data[key]);

    return [
      {
        values,
        labels,
        type: 'pie',
        marker: {
          colors: ['#3B82F6', '#F97316', '#A855F7'],
        },
        hovertemplate: '<b>%{label}</b><br>%{value:.2f}%<extra></extra>',
      },
    ];
  }, [data]);

  const layout = {
    title: 'Gender Distribution',
    height: 400,
    margin: { l: 0, r: 0, t: 40, b: 0 },
    font: { family: 'system-ui, sans-serif' },
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <Plot data={chartData} layout={layout} config={{ responsive: true }} />
    </div>
  );
};

export default GenderChart;
