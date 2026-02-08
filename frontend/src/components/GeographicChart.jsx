import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';

export const GeographicChart = ({ data }) => {
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return [];

    const counties = data.map(item => item.county);
    const counts = data.map(item => item.count);

    return [
      {
        x: counties,
        y: counts,
        type: 'bar',
        marker: {
          color: '#06B6D4',
        },
        hovertemplate: '<b>%{x}</b><br>Count: %{y}<extra></extra>',
      },
    ];
  }, [data]);

  const layout = {
    title: 'Geographic Distribution (Top 5 Counties)',
    xaxis: { title: 'County', tickangle: -45 },
    yaxis: { title: 'Count' },
    height: 400,
    margin: { l: 50, r: 20, t: 40, b: 100 },
    font: { family: 'system-ui, sans-serif' },
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <Plot data={chartData} layout={layout} config={{ responsive: true }} />
    </div>
  );
};

export default GeographicChart;
