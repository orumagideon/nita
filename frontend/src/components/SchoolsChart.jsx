import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';

export const SchoolsChart = ({ data }) => {
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return [];

    // Filter out empty/invalid school names and limit to top 10
    const filteredData = data
      .filter(item => item.name && item.name.trim() !== '' && item.name.toLowerCase() !== 'unknown')
      .slice(0, 10);
    
    const schools = filteredData.map(item => item.name);
    const counts = filteredData.map(item => item.count);

    return [
      {
        x: counts,
        y: schools,
        type: 'bar',
        orientation: 'h',
        marker: {
          color: '#8B5CF6',
          line: {
            color: '#6D28D9',
            width: 1
          }
        },
        hovertemplate: '<b>%{y}</b><br>Students: %{x}<extra></extra>',
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
      title: 'School Name',
      automargin: true,
    },
    height: 450,
    margin: { l: 180, r: 10, t: 10, b: 40 },
    font: { family: 'system-ui, sans-serif' },
    plot_bgcolor: 'rgba(0,0,0,0)',
    paper_bgcolor: 'rgba(0,0,0,0)',
  };

  const config = {
    responsive: true,
    displayModeBar: false,
  };

  if (!data || data.length === 0) {
    return (
      <div className="w-full flex items-center justify-center h-64 text-gray-500">
        <p>No school data available</p>
      </div>
    );
  }

  return (
    <div className="w-full overflow-hidden">
      <div className="mb-2 px-2">
        <h3 className="text-lg font-semibold text-gray-800">Top 10 Schools</h3>
      </div>
      <Plot 
        data={chartData} 
        layout={layout} 
        config={config}
        style={{ width: '100%', height: '100%' }}
        useResizeHandler={true}
      />
    </div>
  );
};

export default SchoolsChart;
