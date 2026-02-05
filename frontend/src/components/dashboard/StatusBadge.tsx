import { clsx } from 'clsx'
import { ArrowUpIcon, ArrowDownIcon, MinusIcon } from '@heroicons/react/24/solid'

interface StatusBadgeProps {
  status: 'running' | 'stopped' | 'paused' | 'created' | 'restarting' | 'removing' | 'unknown'
  size?: 'sm' | 'md' | 'lg'
  showPulse?: boolean
}

export function StatusBadge({ status, size = 'md', showPulse = true }: StatusBadgeProps) {
  interface StatusConfig {
    color: string
    text: string
    bg: string
    label: string
  }

  const statusConfig: Record<string, StatusConfig> = {
    running: { color: 'bg-green-500', text: 'text-green-700 dark:text-green-400', bg: 'bg-green-50 dark:bg-green-900/20', label: 'Running' },
    stopped: { color: 'bg-gray-500', text: 'text-gray-700 dark:text-gray-400', bg: 'bg-gray-50 dark:bg-gray-700/50', label: 'Stopped' },
    paused: { color: 'bg-yellow-500', text: 'text-yellow-700 dark:text-yellow-400', bg: 'bg-yellow-50 dark:bg-yellow-900/20', label: 'Paused' },
    created: { color: 'bg-blue-500', text: 'text-blue-700 dark:text-blue-400', bg: 'bg-blue-50 dark:bg-blue-900/20', label: 'Created' },
    restarting: { color: 'bg-orange-500', text: 'text-orange-700 dark:text-orange-400', bg: 'bg-orange-50 dark:bg-orange-900/20', label: 'Restarting' },
    removing: { color: 'bg-red-500', text: 'text-red-700 dark:text-red-400', bg: 'bg-red-50 dark:bg-red-900/20', label: 'Removing' },
    unknown: { color: 'bg-gray-400', text: 'text-gray-700 dark:text-gray-400', bg: 'bg-gray-50 dark:bg-gray-700/50', label: 'Unknown' },
  }

  const config = statusConfig[status] || statusConfig.unknown

  const sizes = {
    sm: { badge: 'px-2 py-0.5 text-xs', dot: 'w-1.5 h-1.5' },
    md: { badge: 'px-2.5 py-0.5 text-sm', dot: 'w-2 h-2' },
    lg: { badge: 'px-3 py-1 text-base', dot: 'w-2.5 h-2.5' },
  }

  return (
    <span className={clsx(
      'inline-flex items-center gap-1.5 font-medium rounded-full',
      config.bg,
      config.text,
      sizes[size].badge
    )}>
      {showPulse && status === 'running' && (
        <span className={clsx(sizes[size].dot, 'rounded-full animate-pulse', config.color)} />
      )}
      {config.label}
    </span>
  )
}

interface TrendIndicatorProps {
  value: number
  label?: string
  size?: 'sm' | 'md'
}

export function TrendIndicator({ value, label = 'vs last period', size = 'md' }: TrendIndicatorProps) {
  const isPositive = value > 0
  const isNegative = value < 0
  const isNeutral = value === 0

  return (
    <div className={clsx('flex items-center gap-1', size === 'sm' ? 'text-xs' : 'text-sm')}>
      {isPositive && <ArrowUpIcon className="w-4 h-4 text-green-500" />}
      {isNegative && <ArrowDownIcon className="w-4 h-4 text-red-500" />}
      {isNeutral && <MinusIcon className="w-4 h-4 text-gray-400" />}
      <span className={clsx(
        'font-medium',
        isPositive ? 'text-green-600 dark:text-green-400' : 
        isNegative ? 'text-red-600 dark:text-red-400' : 
        'text-gray-500 dark:text-gray-400'
      )}>
        {isPositive ? '+' : ''}{value.toFixed(1)}%
      </span>
      {label && <span className="text-gray-500 dark:text-gray-400">{label}</span>}
    </div>
  )
}
