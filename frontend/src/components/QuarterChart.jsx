import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';

const PROFESSIONAL_COLORS = [
  '#1D4ED8',
  '#0F766E',
  '#7C3AED',
  '#B45309',
  '#BE123C',
  '#374151',
];

export const QuarterChart = ({ data, dataByYear = [] }) => {
  const quarterOrder = ['Q1 (Jul-Sep)', 'Q2 (Oct-Dec)', 'Q3 (Jan-Mar)', 'Q4 (Apr-Jun)'];

  const chartData = useMemo(() => {
    if (dataByYear && dataByYear.length > 0) {
      return dataByYear.map((yearRow, index) => {
        const countsByQuarter = Object.fromEntries(
          (yearRow.quarters || []).map(item => [item.quarter, item.count])
        );

        return {
          x: quarterOrder,
          y: quarterOrder.map(quarter => countsByQuarter[quarter] || 0),
          type: 'bar',
          name: String(yearRow.year),
          marker: {
            color: PROFESSIONAL_COLORS[index % PROFESSIONAL_COLORS.length],
            line: {
              color: '#334155',
              width: 0.8,
            },
          },
          hovertemplate: '<b>Year %{fullData.name}</b><br>%{x}<br>Students: %{y}<extra></extra>',
        };
      });
    }

    if (!data || data.length === 0) return [];

    const countsByQuarter = Object.fromEntries(data.map(item => [item.quarter, item.count]));
    const percentagesByQuarter = Object.fromEntries(data.map(item => [item.quarter, item.percentage]));

    return [
      {
        x: quarterOrder,
        y: quarterOrder.map(quarter => countsByQuarter[quarter] || 0),
        type: 'bar',
        name: 'All Years',
        marker: {
          color: '#1D4ED8',
          line: {
            color: '#334155',
            width: 0.8,
          }
        },
        hovertemplate: '<b>%{x}</b><br>Students: %{y}<br>%{customdata:.1f}%<extra></extra>',
        customdata: quarterOrder.map(quarter => percentagesByQuarter[quarter] || 0),
      },
    ];
  }, [data, dataByYear]);

  const layout = {
    title: '',
    xaxis: { 
      title: 'Quarter',
      gridcolor: '#E5E7EB',
    },
    yaxis: { 
      title: 'Number of Students',
      gridcolor: '#E5E7EB',
    },
    barmode: dataByYear && dataByYear.length > 0 ? 'group' : 'relative',
    legend: {
      title: { text: 'Year' },
      orientation: 'h',
      y: -0.2,
      x: 0,
    },
    height: 350,
    margin: { l: 60, r: 20, t: 10, b: 95 },
    font: { family: 'system-ui, sans-serif' },
    plot_bgcolor: 'rgba(0,0,0,0)',
    paper_bgcolor: 'rgba(0,0,0,0)',
  };

  if ((!data || data.length === 0) && (!dataByYear || dataByYear.length === 0)) {
    return (
      <div className="w-full overflow-hidden">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Enrollment by Quarter</h3>
        <div className="flex items-center justify-center h-64 text-gray-500">
          <p>No quarterly data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full overflow-hidden">
      <div className="mb-2 px-2">
        <h3 className="text-lg font-semibold text-gray-800">Enrollment by Quarter and Year</h3>
        <p className="text-sm text-gray-600">
          Q1: Jul-Sep | Q2: Oct-Dec | Q3: Jan-Mar | Q4: Apr-Jun
        </p>
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

export default QuarterChart;
