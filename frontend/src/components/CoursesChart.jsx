import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';

export const CoursesChart = ({ data }) => {
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return [];

    const courses = data.map(item => item.name);
    const counts = data.map(item => item.count);

    return [
      {
        x: courses,
        y: counts,
        type: 'bar',
        marker: {
          color: '#8B5CF6',
          line: {
            color: '#7C3AED',
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
      title: 'Course Name',
      tickangle: -45,
      gridcolor: '#E5E7EB',
    },
    yaxis: { 
      title: 'Number of Students',
      gridcolor: '#E5E7EB',
    },
    height: 400,
    margin: { l: 60, r: 20, t: 10, b: 120 },
    font: { family: 'system-ui, sans-serif' },
    plot_bgcolor: 'rgba(0,0,0,0)',
    paper_bgcolor: 'rgba(0,0,0,0)',
  };

  return (
    <div className="w-full overflow-hidden">
      <div className="mb-2 px-2">
        <h3 className="text-lg font-semibold text-gray-800">Top 5 Courses of Study</h3>
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

export default CoursesChart;
