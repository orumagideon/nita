import React from 'react';
import { RefreshCw, AlertCircle } from 'lucide-react';

export const Header = ({ loading, error, onRefresh, lastUpdated }) => {
  return (
    <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-10">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900">NITA Dashboard</h1>
            <p className="text-sm text-gray-500 mt-1">Real-time applicant analytics and insights</p>
          </div>
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
