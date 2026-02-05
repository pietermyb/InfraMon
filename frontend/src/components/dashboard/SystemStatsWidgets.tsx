import { useMemo } from 'react'
import { clsx } from 'clsx'
import { SystemStatsResponse } from '../../types'
import { ResourceGauge } from './ResourceGauge'

interface SystemStatsWidgetsProps {
  stats: SystemStatsResponse
  className?: string
}

export function SystemStatsWidgets({ stats, className }: SystemStatsWidgetsProps) {
  const cpuColor = useMemo(() => {
    if (stats.cpu_usage >= 90) return 'danger'
    if (stats.cpu_usage >= 75) return 'warning'
    return 'primary'
  }, [stats.cpu_usage])

  const memoryColor = useMemo(() => {
    if (stats.memory_usage >= 90) return 'danger'
    if (stats.memory_usage >= 75) return 'warning'
    return 'primary'
  }, [stats.memory_usage])

  const diskColor = useMemo(() => {
    if (stats.disk_usage >= 90) return 'danger'
    if (stats.disk_usage >= 75) return 'warning'
    return 'primary'
  }, [stats.disk_usage])

  return (
    <div className={clsx('grid gap-6', className)}>
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          System Resources
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <ResourceGauge
            label="CPU Usage"
            used={stats.memory_used}
            total={stats.memory_total}
            percentage={stats.cpu_usage}
            color={cpuColor}
            size="lg"
            chart="donut"
          />
          <ResourceGauge
            label="Memory Usage"
            used={stats.memory_used}
            total={stats.memory_total}
            percentage={stats.memory_usage}
            color={memoryColor}
            size="lg"
            chart="donut"
          />
          <ResourceGauge
            label="Disk Usage"
            used={stats.disk_used}
            total={stats.disk_total}
            percentage={stats.disk_usage}
            color={diskColor}
            size="lg"
            chart="donut"
          />
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Load Average
        </h3>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="p-4 rounded-lg bg-gray-50 dark:bg-gray-700/50">
            <div className="text-3xl font-bold text-gray-900 dark:text-white">
              {stats.load_avg_1m.toFixed(2)}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">1 min</div>
          </div>
          <div className="p-4 rounded-lg bg-gray-50 dark:bg-gray-700/50">
            <div className="text-3xl font-bold text-gray-900 dark:text-white">
              {stats.load_avg_5m.toFixed(2)}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">5 min</div>
          </div>
          <div className="p-4 rounded-lg bg-gray-50 dark:bg-gray-700/50">
            <div className="text-3xl font-bold text-gray-900 dark:text-white">
              {stats.load_avg_15m.toFixed(2)}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">15 min</div>
          </div>
        </div>
        <div className="mt-4 text-sm text-gray-500 dark:text-gray-400">
          {stats.cpu_cores} CPU cores • {stats.load_percent.toFixed(1)}% load
        </div>
      </div>
    </div>
  )
}
