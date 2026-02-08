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
        },
        hovertemplate: '<b>%{x}</b><br>Count: %{y}<extra></extra>',
      },
    ];
  }, [data]);

  const layout = {
    title: 'Top 5 Courses of Study',
    xaxis: { title: 'Course', tickangle: -45 },
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

export default CoursesChart;
