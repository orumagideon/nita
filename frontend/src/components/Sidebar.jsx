import React, { useState } from 'react';
import { ChevronDown, X } from 'lucide-react';

export const Sidebar = ({ counties, levels, onCountyChange, onLevelChange, selectedCounty, selectedLevel }) => {
  const [isOpen, setIsOpen] = useState(true);
  const [expandedSections, setExpandedSections] = useState({
    county: true,
    level: true,
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const handleClearFilters = () => {
    onCountyChange(null);
    onLevelChange(null);
  };

  return (
    <>
      {/* Mobile toggle button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="lg:hidden fixed top-4 left-4 z-40 p-2 bg-blue-600 text-white rounded-lg"
      >
        {isOpen ? <X className="w-6 h-6" /> : <ChevronDown className="w-6 h-6" />}
      </button>

      {/* Sidebar */}
      <aside
        className={`fixed lg:relative left-0 top-0 h-screen lg:h-auto w-64 bg-gray-50 border-r border-gray-200 transform transition-transform duration-300 ease-in-out z-30 ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        } overflow-y-auto`}
      >
        <div className="p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Filters</h2>

          {/* Clear Filters */}
          {(selectedCounty || selectedLevel) && (
            <button
              onClick={handleClearFilters}
              className="w-full mb-4 px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
            >
              Clear All Filters
            </button>
          )}

          {/* County Filter */}
          <div className="mb-6">
            <button
              onClick={() => toggleSection('county')}
              className="flex items-center justify-between w-full p-3 rounded-lg hover:bg-gray-200 transition-colors"
            >
              <h3 className="text-sm font-semibold text-gray-700">County</h3>
              <ChevronDown
                className={`w-4 h-4 text-gray-600 transform transition-transform ${
                  expandedSections.county ? 'rotate-180' : ''
                }`}
              />
            </button>

            {expandedSections.county && (
              <div className="mt-2 space-y-2">
                <button
                  onClick={() => onCountyChange(null)}
                  className={`block w-full text-left px-3 py-2 text-sm rounded-md transition-colors ${
                    !selectedCounty
                      ? 'bg-blue-100 text-blue-700 font-medium'
                      : 'text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  All Counties
                </button>
                {counties && counties.map(county => (
                  <button
                    key={county}
                    onClick={() => onCountyChange(county)}
                    className={`block w-full text-left px-3 py-2 text-sm rounded-md transition-colors ${
                      selectedCounty === county
                        ? 'bg-blue-100 text-blue-700 font-medium'
                        : 'text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {county}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Level Filter */}
          <div className="mb-6">
            <button
              onClick={() => toggleSection('level')}
              className="flex items-center justify-between w-full p-3 rounded-lg hover:bg-gray-200 transition-colors"
            >
              <h3 className="text-sm font-semibold text-gray-700">Level of Training</h3>
              <ChevronDown
                className={`w-4 h-4 text-gray-600 transform transition-transform ${
                  expandedSections.level ? 'rotate-180' : ''
                }`}
              />
            </button>

            {expandedSections.level && (
              <div className="mt-2 space-y-2">
                <button
                  onClick={() => onLevelChange(null)}
                  className={`block w-full text-left px-3 py-2 text-sm rounded-md transition-colors ${
                    !selectedLevel
                      ? 'bg-blue-100 text-blue-700 font-medium'
                      : 'text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  All Levels
                </button>
                {levels && levels.map(level => (
                  <button
                    key={level}
                    onClick={() => onLevelChange(level)}
                    className={`block w-full text-left px-3 py-2 text-sm rounded-md transition-colors ${
                      selectedLevel === level
                        ? 'bg-blue-100 text-blue-700 font-medium'
                        : 'text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {level}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Footer info */}
          <div className="border-t border-gray-200 pt-4 mt-6">
            <p className="text-xs text-gray-500">
              Select filters to refine the dashboard data. All charts will update automatically.
            </p>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 lg:hidden z-20"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
};

export default Sidebar;
