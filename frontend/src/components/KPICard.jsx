import React from 'react';
import { CheckCircle, TrendingUp } from 'lucide-react';

export const KPICard = ({ title, value, subtitle, icon: Icon, trend, color = 'blue' }) => {
  const colorClasses = {
    blue: 'bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200',
    green: 'bg-gradient-to-br from-green-50 to-green-100 border-green-200',
    purple: 'bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200',
    orange: 'bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200',
  };

  const iconColorClasses = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    purple: 'text-purple-600',
    orange: 'text-orange-600',
  };

  return (
    <div className={`${colorClasses[color]} border rounded-xl p-4 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 backdrop-blur-sm`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-gray-600 text-sm font-medium">{title}</p>
          <div className="mt-2 flex items-baseline gap-2">
            <h3 className="text-3xl font-bold text-gray-900">{value}</h3>
            {trend && (
              <span className={`text-sm font-medium ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {trend > 0 ? '+' : ''}{trend}%
              </span>
            )}
          </div>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
        {Icon && <Icon className={`${iconColorClasses[color]} w-8 h-8`} />}
      </div>
    </div>
  );
};

export const KPIRow = ({ stats }) => {
  if (!stats) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <KPICard
        title="Total Applicants"
        value={stats.total_registrations || 0}
        color="blue"
        icon={TrendingUp}
      />
      <KPICard
        title="Placement Rate"
        value={`${stats.placement_rate || 0}%`}
        color="green"
        icon={CheckCircle}
      />
      <KPICard
        title="Male Applicants"
        value={`${stats.gender_ratio?.Male || 0}%`}
        color="purple"
      />
      <KPICard
        title="Female Applicants"
        value={`${stats.gender_ratio?.Female || 0}%`}
        color="orange"
      />
    </div>
  );
};

export default KPICard;
