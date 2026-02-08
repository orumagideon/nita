import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';

export const CompaniesChart = ({ data }) => {
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return [];

    const companies = data.map(item => item.name).slice(0, 10);
    const counts = data.map(item => item.count).slice(0, 10);

    return [
      {
        x: counts,
        y: companies,
        type: 'bar',
        orientation: 'h',
        marker: {
          color: '#F59E0B',
        },
        hovertemplate: '<b>%{y}</b><br>Count: %{x}<extra></extra>',
      },
    ];
  }, [data]);

  const layout = {
    title: 'Top 10 Preferred Companies',
    xaxis: { title: 'Count' },
    yaxis: { title: 'Company' },
    height: 450,
    margin: { l: 250, r: 20, t: 40, b: 40 },
    font: { family: 'system-ui, sans-serif' },
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <Plot data={chartData} layout={layout} config={{ responsive: true }} />
    </div>
  );
};

export default CompaniesChart;
