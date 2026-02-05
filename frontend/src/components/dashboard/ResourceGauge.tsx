import { clsx } from 'clsx'
import { ProgressBar } from '../ui'

interface ResourceGaugeProps {
  label: string
  used: number
  total: number
  percentage?: number
  showDetails?: boolean
  color?: 'primary' | 'success' | 'warning' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  chart?: 'gauge' | 'bar' | 'donut'
}

export function ResourceGauge({
  label,
  used,
  total,
  percentage,
  showDetails = true,
  color = 'primary',
  size = 'md',
  chart = 'bar'
}: ResourceGaugeProps) {
  const value = percentage ?? ((used / total) * 100)
  
  const getColor = () => {
    if (value >= 90) return 'danger'
    if (value >= 75) return 'warning'
    return color
  }

  const formatBytes = (bytes: number) => {
    if (bytes >= 1e12) return `${(bytes / 1e12).toFixed(2)} TB`
    if (bytes >= 1e9) return `${(bytes / 1e9).toFixed(2)} GB`
    if (bytes >= 1e6) return `${(bytes / 1e6).toFixed(2)} MB`
    if (bytes >= 1e3) return `${(bytes / 1e3).toFixed(2)} KB`
    return `${bytes} B`
  }

  if (chart === 'donut') {
    const radius = 40
    const circumference = 2 * Math.PI * radius
    const strokeDashoffset = circumference - (value / 100) * circumference
    
    return (
      <div className="flex flex-col items-center">
        <div className="relative w-32 h-32">
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="64"
              cy="64"
              r={radius}
              stroke="currentColor"
              strokeWidth="8"
              fill="transparent"
              className="text-gray-200 dark:text-gray-700"
            />
            <circle
              cx="64"
              cy="64"
              r={radius}
              stroke="currentColor"
              strokeWidth="8"
              fill="transparent"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              className={clsx(
                'transition-all duration-500',
                getColor() === 'danger' ? 'text-red-500' :
                getColor() === 'warning' ? 'text-yellow-500' :
                'text-primary-500'
              )}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-2xl font-bold text-gray-900 dark:text-white">
              {value.toFixed(1)}%
            </span>
          </div>
        </div>
        {showDetails && (
          <div className="mt-2 text-center">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{label}</span>
            <span className="text-xs text-gray-500 dark:text-gray-400 block">
              {formatBytes(used)} / {formatBytes(total)}
            </span>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className={clsx(size === 'lg' ? 'space-y-3' : 'space-y-2')}>
      {showDetails && (
        <div className="flex justify-between items-center">
          <span className={clsx(
            'font-medium text-gray-700 dark:text-gray-300',
            size === 'lg' ? 'text-base' : 'text-sm'
          )}>
            {label}
          </span>
          <span className={clsx(
            'text-gray-500 dark:text-gray-400',
            size === 'lg' ? 'text-sm' : 'text-xs'
          )}>
            {formatBytes(used)} / {formatBytes(total)}
          </span>
        </div>
      )}
      <ProgressBar
        value={value}
        color={getColor() === 'danger' ? 'danger' : getColor() === 'warning' ? 'warning' : 'primary'}
        size={size}
      />
    </div>
  )
}
