import { motion } from 'framer-motion';
import clsx from 'clsx';

export default function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  color = 'primary',
  trend,
  index = 0
}) {
  const colorClasses = {
    primary: 'bg-primary-50 text-primary-600',
    green: 'bg-green-50 text-green-600',
    blue: 'bg-blue-50 text-blue-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    red: 'bg-red-50 text-red-600',
    purple: 'bg-purple-50 text-purple-600',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
          {trend && (
            <div className={clsx(
              'inline-flex items-center mt-2 text-xs font-medium px-2 py-1 rounded-full',
              trend.direction === 'up' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
            )}>
              <span>{trend.direction === 'up' ? '↑' : '↓'} {trend.value}</span>
            </div>
          )}
        </div>

        {Icon && (
          <div className={clsx('p-3 rounded-lg', colorClasses[color])}>
            <Icon className="h-6 w-6" />
          </div>
        )}
      </div>
    </motion.div>
  );
}
