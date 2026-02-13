import React, { useState, useEffect, useCallback } from 'react';
import Header from '../components/Header';
import Sidebar from '../components/Sidebar';
import Footer from '../components/Footer';
import { KPIRow } from '../components/KPICard';
import GenderChart from '../components/GenderChart';
import EducationChart from '../components/EducationChart';
import CompaniesChart from '../components/CompaniesChart';
import CoursesChart from '../components/CoursesChart';
import GeographicChart from '../components/GeographicChart';
import { apiService } from '../services/api';

export const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [counties, setCounties] = useState([]);
  const [levels, setLevels] = useState([]);
  const [selectedCounty, setSelectedCounty] = useState(null);
  const [selectedLevel, setSelectedLevel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Fetch filter options
  useEffect(() => {
    const fetchFilterOptions = async () => {
      try {
        const [countiesRes, levelsRes] = await Promise.all([
          apiService.getCounties(),
          apiService.getLevels(),
        ]);
        setCounties(countiesRes.data.counties || []);
        setLevels(levelsRes.data.levels || []);
      } catch (err) {
        console.error('Failed to fetch filter options:', err);
      }
    };

    fetchFilterOptions();
  }, []);

  // Fetch statistics
  const fetchStats = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiService.getStats(selectedCounty, selectedLevel);
      setStats(response.data);
      setLastUpdated(new Date().toISOString());
    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch statistics:', err);
    } finally {
      setLoading(false);
    }
  }, [selectedCounty, selectedLevel]);

  // Fetch stats on component mount and when filters change
  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  const handleCountyChange = (county) => {
    setSelectedCounty(county);
  };

  const handleLevelChange = (level) => {
    setSelectedLevel(level);
  };

  return (
    <div className="flex flex-col h-screen nita-dashboard-bg">
      {/* Header */}
      <Header
        loading={loading}
        error={error}
        onRefresh={fetchStats}
        lastUpdated={lastUpdated}
      />

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <Sidebar
          counties={counties}
          levels={levels}
          onCountyChange={handleCountyChange}
          onLevelChange={handleLevelChange}
          selectedCounty={selectedCounty}
          selectedLevel={selectedLevel}
        />

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Content */}
          <div className="flex-1 overflow-auto">
            <div className="p-6 max-w-7xl mx-auto">
              {/* KPI Row */}
              <KPIRow stats={stats} />

              {/* Charts Grid */}
              {stats && !loading && !error ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Row 1 */}
                  <div className="bg-gradient-to-br from-white to-blue-50 backdrop-blur-md rounded-xl shadow-lg hover:shadow-2xl p-4 transition-all duration-300 border border-blue-100/30">
                    <GenderChart data={stats.gender_ratio} />
                  </div>
                  <div className="bg-gradient-to-br from-white to-blue-50 backdrop-blur-md rounded-xl shadow-lg hover:shadow-2xl p-4 transition-all duration-300 border border-blue-100/30">
                    <EducationChart data={stats.education_breakdown} />
                  </div>

                  {/* Row 2 */}
                  <div className="lg:col-span-2 bg-gradient-to-br from-white to-blue-50 backdrop-blur-md rounded-xl shadow-lg hover:shadow-2xl p-4 transition-all duration-300 border border-blue-100/30">
                    <CoursesChart data={stats.top_courses} />
                  </div>

                  {/* Row 3 */}
                  <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-md p-4 hover:shadow-lg transition-shadow">
                    <GeographicChart data={stats.geographic_distribution} />
                  </div>

                  {/* Row 4 */}
                  <div className="lg:col-span-2 bg-gradient-to-br from-white to-blue-50 backdrop-blur-md rounded-xl shadow-lg hover:shadow-2xl p-4 transition-all duration-300 border border-blue-100/30">
                    <CompaniesChart data={stats.preferred_companies} />
                  </div>
                </div>
              ) : loading ? (
                <div className="flex items-center justify-center h-96">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="text-gray-600 mt-4">Loading dashboard data...</p>
                  </div>
                </div>
              ) : error ? (
                <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
                  <p className="text-red-800 font-medium">Error loading data</p>
                  <p className="text-red-600 text-sm mt-2">{error}</p>
                  <button
                    onClick={fetchStats}
                    className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                  >
                    Retry
                  </button>
                </div>
              ) : null}
            </div>
          </div>

          {/* Footer */}
          <Footer />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
