import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';

export const EducationChart = ({ data }) => {
  const chartData = useMemo(() => {
    if (!data || Object.keys(data).length === 0) return [];

    const levels = Object.keys(data);
    const counts = Object.values(data);

    return [
      {
        x: counts,
        y: levels,
        type: 'bar',
        orientation: 'h',
        marker: {
          color: '#10B981',
        },
        hovertemplate: '<b>%{y}</b><br>Count: %{x}<extra></extra>',
      },
    ];
  }, [data]);

  const layout = {
    title: 'Education Level Distribution',
    xaxis: { title: 'Count' },
    yaxis: { title: 'Level of Training' },
    height: 400,
    margin: { l: 150, r: 20, t: 40, b: 40 },
    font: { family: 'system-ui, sans-serif' },
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <Plot data={chartData} layout={layout} config={{ responsive: true }} />
    </div>
  );
};

export default EducationChart;
