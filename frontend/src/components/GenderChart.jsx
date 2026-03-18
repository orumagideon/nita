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
    title: '',
    height: 400,
    margin: { l: 0, r: 0, t: 10, b: 0 },
    font: { family: 'system-ui, sans-serif' },
    plot_bgcolor: 'rgba(0,0,0,0)',
    paper_bgcolor: 'rgba(0,0,0,0)',
  };

  return (
    <div className="w-full overflow-hidden">
      <div className="mb-2 px-2">
        <h3 className="text-lg font-semibold text-gray-800">Gender Distribution</h3>
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

export default GenderChart;
