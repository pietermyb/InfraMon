import { clsx } from 'clsx'

interface UptimeDisplayProps {
  uptime: number
  showLabels?: boolean
  size?: 'sm' | 'md' | 'lg'
  variant?: 'text' | 'badge'
}

export function UptimeDisplay({
  uptime,
  showLabels = true,
  size = 'md',
  variant = 'text'
}: UptimeDisplayProps) {
  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)

    const parts = []
    if (days > 0) parts.push(`${days}d`)
    if (hours > 0) parts.push(`${hours}h`)
    if (minutes > 0) parts.push(`${minutes}m`)
    parts.push(`${secs}s`)

    return parts.join(' ')
  }

  const sizes = {
    sm: 'text-sm',
    md: 'text-lg',
    lg: 'text-2xl',
  }

  const labels = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  }

  if (variant === 'badge') {
    return (
      <div className={clsx(
        'inline-flex items-center gap-2 px-3 py-1 rounded-full',
        'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
      )}>
        <span className={clsx('w-2 h-2 rounded-full bg-green-500 animate-pulse')} />
        <span className={clsx('font-medium', sizes[size])}>
          {formatUptime(uptime)}
        </span>
      </div>
    )
  }

  return (
    <div className="space-y-1">
      <span className={clsx('text-gray-500 dark:text-gray-400', labels[size])}>
        {showLabels && 'System Uptime'}
      </span>
      <div className={clsx('font-mono font-semibold text-gray-900 dark:text-white', sizes[size])}>
        {formatUptime(uptime)}
      </div>
    </div>
  )
}
