import { ReactNode } from 'react'
import { clsx } from 'clsx'

interface StatCardProps {
  title: string
  value: string | number
  unit?: string
  icon?: ReactNode
  trend?: {
    value: number
    label: string
  }
  color?: 'default' | 'primary' | 'success' | 'warning' | 'danger'
  className?: string
}

export function StatCard({
  title,
  value,
  unit,
  icon,
  trend,
  color = 'default',
  className
}: StatCardProps) {
  const colors = {
    default: 'bg-white dark:bg-gray-800',
    primary: 'bg-white dark:bg-gray-800 border-l-4 border-primary-500',
    success: 'bg-white dark:bg-gray-800 border-l-4 border-green-500',
    warning: 'bg-white dark:bg-gray-800 border-l-4 border-yellow-500',
    danger: 'bg-white dark:bg-gray-800 border-l-4 border-red-500',
  }

  const iconColors = {
    default: 'text-gray-400',
    primary: 'text-primary-500',
    success: 'text-green-500',
    warning: 'text-yellow-500',
    danger: 'text-red-500',
  }

  return (
    <div className={clsx('overflow-hidden shadow rounded-lg', colors[color], className)}>
      <div className="p-5">
        <div className="flex items-center">
          {icon && (
            <div className={clsx('flex-shrink-0', iconColors[color])}>
              {icon}
            </div>
          )}
          <div className={clsx('flex-1', icon ? 'ml-5' : '')}>
            <dl>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                {title}
              </dt>
              <dd className="flex items-baseline">
                <div className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {typeof value === 'number' ? value.toLocaleString() : value}
                </div>
                {unit && (
                  <div className="ml-1 text-sm text-gray-500 dark:text-gray-400">
                    {unit}
                  </div>
                )}
              </dd>
            </dl>
          </div>
        </div>
      </div>
      {trend && (
        <div className={clsx(
          'px-5 py-3 border-t border-gray-200 dark:border-gray-700',
          trend.value > 0 ? 'bg-green-50 dark:bg-green-900/20' : 
          trend.value < 0 ? 'bg-red-50 dark:bg-red-900/20' : 
          'bg-gray-50 dark:bg-gray-700/50'
        )}>
          <div className="flex items-center text-sm">
            <span className={clsx(
              'font-medium',
              trend.value > 0 ? 'text-green-600 dark:text-green-400' : 
              trend.value < 0 ? 'text-red-600 dark:text-red-400' : 
              'text-gray-600 dark:text-gray-400'
            )}>
              {trend.value > 0 ? '+' : ''}{trend.value}%
            </span>
            <span className="ml-2 text-gray-500 dark:text-gray-400">
              {trend.label}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
