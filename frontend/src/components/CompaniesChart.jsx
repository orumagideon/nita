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
          line: {
            color: '#D97706',
            width: 1
          }
        },
        hovertemplate: '<b>%{y}</b><br>Preferences: %{x}<extra></extra>',
      },
    ];
  }, [data]);

  const layout = {
    title: '',
    xaxis: { 
      title: 'Number of Preferences',
      gridcolor: '#E5E7EB',
    },
    yaxis: { 
      title: 'Company Name',
      automargin: true,
    },
    height: 450,
    margin: { l: 180, r: 10, t: 10, b: 40 },
    font: { family: 'system-ui, sans-serif' },
    plot_bgcolor: 'rgba(0,0,0,0)',
    paper_bgcolor: 'rgba(0,0,0,0)',
  };

  return (
    <div className="w-full overflow-hidden">
      <div className="mb-2 px-2">
        <h3 className="text-lg font-semibold text-gray-800">Top 10 Preferred Companies</h3>
      </div>
      <Plot
        data={chartData}
        layout={layout}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%', height: '100%' }}
        useResizeHandler={true}
      />
    </div>
  );
};

export default CompaniesChart;
