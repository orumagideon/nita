import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';

export const EducationChart = ({ data }) => {
  const chartData = useMemo(() => {
    if (!data || Object.keys(data).length === 0) return [];

    // Filter and sort education levels, removing empty/unknown entries
    const filteredData = Object.entries(data)
      .filter(([level]) => level && level.trim() !== '' && level.toLowerCase() !== 'unknown')
      .sort((a, b) => b[1] - a[1]);
    
    const levels = filteredData.map(([level]) => level);
    const counts = filteredData.map(([_, count]) => count);

    return [
      {
        x: counts,
        y: levels,
        type: 'bar',
        orientation: 'h',
        marker: {
          color: '#10B981',
          line: {
            color: '#059669',
            width: 1
          }
        },
        hovertemplate: '<b>%{y}</b><br>Count: %{x}<extra></extra>',
      },
    ];
  }, [data]);

  const layout = {
    title: '',
    xaxis: { 
      title: 'Number of Students',
      gridcolor: '#E5E7EB',
    },
    yaxis: { 
      title: 'Level of Training',
      automargin: true,
    },
    height: 400,
    margin: { l: 130, r: 10, t: 10, b: 40 },
    font: { family: 'system-ui, sans-serif' },
    plot_bgcolor: 'rgba(0,0,0,0)',
    paper_bgcolor: 'rgba(0,0,0,0)',
  };

  return (
    <div className="w-full overflow-hidden">
      <div className="mb-2 px-2">
        <h3 className="text-lg font-semibold text-gray-800">Education Level Distribution</h3>
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

export default EducationChart;
