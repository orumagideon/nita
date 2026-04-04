import React, { useEffect, useMemo, useState } from 'react';
import Plot from 'react-plotly.js';

const PROFESSIONAL_COLORS = [
  '#1D4ED8',
  '#0F766E',
  '#7C3AED',
  '#B45309',
  '#BE123C',
  '#374151',
];

const QUARTER_ORDER = ['Q1 (Jul-Sep)', 'Q2 (Oct-Dec)', 'Q3 (Jan-Mar)', 'Q4 (Apr-Jun)'];

export const QuarterChart = ({ data, dataByYear = [] }) => {
  const [selectedYear, setSelectedYear] = useState('');

  const currentYearNumber = new Date().getFullYear();

  const availableYears = useMemo(() => {
    const yearsFromDataNumbers = (dataByYear || [])
      .map((row) => Number(row.year))
      .filter((year) => Number.isFinite(year));

    const earliestDataYear = yearsFromDataNumbers.length
      ? Math.min(...yearsFromDataNumbers)
      : currentYearNumber - 5;

    const startYear = Math.min(earliestDataYear, currentYearNumber - 5);
    const endYear = currentYearNumber + 15;

    const generatedYears = [];
    for (let year = startYear; year <= endYear; year += 1) {
      generatedYears.push(String(year));
    }

    const yearsFromData = yearsFromDataNumbers.map((year) => String(year));

    return Array.from(new Set([...generatedYears, ...yearsFromData]))
      .sort((a, b) => Number(b) - Number(a));
  }, [dataByYear, currentYearNumber]);

  useEffect(() => {
    if (availableYears.length === 0) {
      setSelectedYear('');
      return;
    }

    const currentYear = String(currentYearNumber);

    if (availableYears.includes(currentYear)) {
      setSelectedYear(currentYear);
      return;
    }

    setSelectedYear(availableYears[0]);
  }, [availableYears, currentYearNumber]);

  const chartData = useMemo(() => {
    if (dataByYear && dataByYear.length > 0) {
      const selectedYearRow = dataByYear.find(
        (yearRow) => String(yearRow.year) === selectedYear
      );

      const countsByQuarter = Object.fromEntries(
        ((selectedYearRow && selectedYearRow.quarters) || []).map((item) => [item.quarter, item.count])
      );

      return [
        {
          x: QUARTER_ORDER,
          y: QUARTER_ORDER.map((quarter) => countsByQuarter[quarter] || 0),
          type: 'bar',
          name: String(selectedYear || currentYearNumber),
          marker: {
            color: PROFESSIONAL_COLORS[0],
            line: {
              color: '#334155',
              width: 0.8,
            },
          },
          hovertemplate: '<b>Year %{fullData.name}</b><br>%{x}<br>Students: %{y}<extra></extra>',
        },
      ];
    }

    if (!data || data.length === 0) return [];

    const countsByQuarter = Object.fromEntries(data.map(item => [item.quarter, item.count]));
    const percentagesByQuarter = Object.fromEntries(data.map(item => [item.quarter, item.percentage]));

    return [
      {
        x: QUARTER_ORDER,
        y: QUARTER_ORDER.map(quarter => countsByQuarter[quarter] || 0),
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
        customdata: QUARTER_ORDER.map(quarter => percentagesByQuarter[quarter] || 0),
      },
    ];
  }, [data, dataByYear, selectedYear, currentYearNumber]);

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
    barmode: 'relative',
    legend: {
      title: { text: '' },
      orientation: 'h',
      x: 0,
      xanchor: 'left',
      y: 1.12,
      yanchor: 'bottom',
    },
    height: 350,
    margin: { l: 60, r: 20, t: 30, b: 60 },
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
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-800">Enrollment by Quarter and Year</h3>
            <p className="text-sm text-gray-600">
              Q1: Jul-Sep | Q2: Oct-Dec | Q3: Jan-Mar | Q4: Apr-Jun
            </p>
          </div>

          {availableYears.length > 0 && (
            <div className="flex items-center gap-2">
              <label htmlFor="year-filter" className="text-sm font-medium text-gray-700">
                Year
              </label>
              <select
                id="year-filter"
                value={selectedYear}
                onChange={(e) => setSelectedYear(e.target.value)}
                className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {availableYears.map((year) => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
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
