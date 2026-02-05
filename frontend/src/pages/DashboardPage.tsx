import { useState } from 'react'
import {
  SignalIcon,
  ComputerDesktopIcon,
  ArrowPathIcon,
  ChartBarIcon,
  CpuChipIcon,
} from '@heroicons/react/24/outline'
import { Spinner, Button } from '../components/ui'
import {
  StatCard,
  SystemStatsWidgets,
  ContainerStatsWidgets,
  UptimeDisplay,
  HistoryChart,
  DonutChart,
  NetworkTrafficChart,
} from '../components/dashboard'
import { useDashboardData, useSystemStats, useHistoricalStats, useAutoRefresh } from '../hooks'
import { SystemStatsResponse } from '../types'

type TimeRange = '1h' | '6h' | '24h' | '7d'

export default function DashboardPage() {
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [timeRange, setTimeRange] = useState<TimeRange>('1h')

  const { data: dashboardData, isLoading: dashboardLoading, error: dashboardError } = useDashboardData({
    enabled: true,
    interval: autoRefresh ? 5000 : undefined,
  })

  const { data: systemStats, isLoading: systemStatsLoading } = useSystemStats({
    enabled: true,
    interval: autoRefresh ? 5000 : undefined,
  })

  const { data: historyData } = useHistoricalStats(timeRange)

  const { refreshNow } = useAutoRefresh(autoRefresh, 5000)

  const handleRefresh = () => {
    refreshNow()
  }

  if (dashboardLoading || systemStatsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    )
  }

  if (dashboardError || !dashboardData) {
    return (
      <div className="flex flex-col items-center justify-center h-64 space-y-4">
        <div className="text-red-500">Error loading dashboard data</div>
        <Button onClick={handleRefresh} variant="primary">
          Try Again
        </Button>
      </div>
    )
  }

  const containerStatusData = [
    { name: 'Running', value: dashboardData.containers.running },
    { name: 'Stopped', value: dashboardData.containers.stopped },
    { name: 'Paused', value: dashboardData.containers.paused },
  ].filter(item => item.value > 0)

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Real-time system and container monitoring
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as TimeRange)}
            className="block w-32 rounded-md border-gray-300 dark:border-gray-600 
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-white 
                       shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          >
            <option value="1h">Last hour</option>
            <option value="6h">Last 6 hours</option>
            <option value="24h">Last 24 hours</option>
            <option value="7d">Last 7 days</option>
          </select>
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`p-2 rounded-lg transition-colors ${
              autoRefresh
                ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-600'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-500'
            }`}
            title={autoRefresh ? 'Auto-refresh enabled' : 'Auto-refresh disabled'}
          >
            <ArrowPathIcon className={`h-5 w-5 ${autoRefresh ? 'animate-spin-slow' : ''}`} />
          </button>
          <Button variant="secondary" onClick={handleRefresh} size="sm">
            Refresh
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="CPU Usage"
          value={systemStats?.cpu_usage.toFixed(1) || '0'}
          unit="%"
          icon={<CpuChipIcon className="h-6 w-6" />}
          color={systemStats && systemStats.cpu_usage >= 80 ? 'warning' : 'primary'}
          trend={{ value: 2.5, label: 'vs 5m ago' }}
        />
        <StatCard
          title="Memory Usage"
          value={systemStats?.memory_usage.toFixed(1) || '0'}
          unit="%"
          icon={<ChartBarIcon className="h-6 w-6" />}
          color={systemStats && systemStats.memory_usage >= 80 ? 'warning' : 'primary'}
          trend={{ value: -1.2, label: 'vs 5m ago' }}
        />
        <StatCard
          title="Containers Running"
          value={dashboardData.containers.running}
          icon={<ComputerDesktopIcon className="h-6 w-6 text-green-500" />}
          color="success"
        />
        <StatCard
          title="Network I/O"
          value={((systemStats?.network_rx || 0) / 1e6).toFixed(2)}
          unit="MB/s"
          icon={<SignalIcon className="h-6 w-6 text-blue-500" />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          {historyData?.stats && (
            <HistoryChart
              data={historyData.stats}
              metrics={['cpu_usage', 'memory_usage']}
              title="Resource Usage Over Time"
              timeRange={`Last ${timeRange}`}
              height={350}
            />
          )}
        </div>
        <div>
          <DonutChart
            data={containerStatusData}
            title="Container Status"
            size={220}
            innerRadius={70}
          />
        </div>
      </div>

      {systemStats && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <NetworkTrafficChart
              data={historyData?.stats?.slice(-20).map((s: SystemStatsResponse) => ({
                timestamp: s.timestamp,
                rx_bytes: s.network_rx || 0,
                tx_bytes: s.network_tx || 0,
              })) || []}
              title="Network Traffic"
              height={250}
            />
          </div>
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              System Uptime
            </h3>
            <UptimeDisplay uptime={systemStats.uptime} size="lg" variant="badge" />
            <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
              <div className="grid grid-cols-2 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {systemStats.cpu_cores}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">CPU Cores</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {(systemStats.memory_total / 1e9).toFixed(1)} GB
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Total Memory</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {systemStats && (
        <SystemStatsWidgets stats={systemStats} />
      )}

      {dashboardData && (
        <ContainerStatsWidgets data={dashboardData} />
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Quick Actions
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <button className="p-4 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 
                             hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20 
                             transition-colors group">
              <ComputerDesktopIcon className="h-8 w-8 mx-auto text-gray-400 group-hover:text-primary-500" />
              <span className="block mt-2 text-sm text-gray-600 dark:text-gray-400 group-hover:text-primary-600">
                View All Containers
              </span>
            </button>
            <button className="p-4 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 
                             hover:border-green-500 hover:bg-green-50 dark:hover:bg-green-900/20 
                             transition-colors group">
              <ArrowPathIcon className="h-8 w-8 mx-auto text-gray-400 group-hover:text-green-500" />
              <span className="block mt-2 text-sm text-gray-600 dark:text-gray-400 group-hover:text-green-600">
                Refresh All
              </span>
            </button>
            <button className="p-4 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 
                             hover:border-yellow-500 hover:bg-yellow-50 dark:hover:bg-yellow-900/20 
                             transition-colors group">
              <SignalIcon className="h-8 w-8 mx-auto text-gray-400 group-hover:text-yellow-500" />
              <span className="block mt-2 text-sm text-gray-600 dark:text-gray-400 group-hover:text-yellow-600">
                View Logs
              </span>
            </button>
            <button className="p-4 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 
                             hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 
                             transition-colors group">
              <ChartBarIcon className="h-8 w-8 mx-auto text-gray-400 group-hover:text-blue-500" />
              <span className="block mt-2 text-sm text-gray-600 dark:text-gray-400 group-hover:text-blue-600">
                Export Stats
              </span>
            </button>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            System Health
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-600 dark:text-gray-400">CPU Health</span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                Normal
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600 dark:text-gray-400">Memory Health</span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                Normal
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600 dark:text-gray-400">Disk Health</span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
                {systemStats?.disk_usage.toFixed(1)}% Used
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600 dark:text-gray-400">Network Status</span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                Connected
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
