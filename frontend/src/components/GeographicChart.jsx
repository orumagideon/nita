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
          line: {
            color: '#0891B2',
            width: 1
          }
        },
        hovertemplate: '<b>%{x}</b><br>Students: %{y}<extra></extra>',
      },
    ];
  }, [data]);

  const layout = {
    title: '',
    xaxis: { 
      title: 'County',
      tickangle: -45,
      gridcolor: '#E5E7EB',
    },
    yaxis: { 
      title: 'Number of Students',
      gridcolor: '#E5E7EB',
    },
    height: 400,
    margin: { l: 60, r: 20, t: 10, b: 100 },
    font: { family: 'system-ui, sans-serif' },
    plot_bgcolor: 'rgba(0,0,0,0)',
    paper_bgcolor: 'rgba(0,0,0,0)',
  };

  return (
    <div className="w-full overflow-hidden">
      <div className="mb-2 px-2">
        <h3 className="text-lg font-semibold text-gray-800">Geographic Distribution - Top 5 Counties</h3>
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

export default GeographicChart;
