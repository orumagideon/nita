import React from 'react';
import { RefreshCw, AlertCircle } from 'lucide-react';
import nitaLogo from '../assets/images/NITA-Logo.png';

export const Header = ({ loading, error, onRefresh, lastUpdated }) => {
  return (
    <header className="bg-gradient-to-r from-white via-blue-50 to-indigo-100 border-b-2 border-blue-200 shadow-md sticky top-0 z-10">
      <div className="px-6 py-3">
        <div className="flex items-center justify-between mb-4">
          <img src={nitaLogo} alt="NITA Logo" className="h-14 object-contain" />
          <div className="flex-1 flex flex-col items-center">
            <h1 className="text-3xl font-bold text-gray-900">NITA Dashboard</h1>
            <p className="text-sm text-gray-500 mt-1">Real-time applicant analytics and insights</p>
          </div>
          <div className="w-14"></div>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex-1"></div>
          <div className="flex items-center gap-4">
            {error && (
              <div className="flex items-center gap-2 text-red-600">
                <AlertCircle className="w-5 h-5" />
                <span className="text-sm">Error loading data</span>
              </div>
            )}
            {lastUpdated && !error && (
              <p className="text-xs text-gray-500">
                Last updated: {new Date(lastUpdated).toLocaleTimeString()}
              </p>
            )}
            <button
              onClick={onRefresh}
              disabled={loading}
              className={`p-2 rounded-lg transition-colors ${
                loading
                  ? 'bg-gray-100 text-gray-400'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
              title="Refresh data"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
