import { useMemo } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { useTheme } from '../../hooks/useTheme'

interface HistoryChartProps {
  data: Array<{
    timestamp: string
    cpu_usage?: number
    memory_usage?: number
    disk_usage?: number
  }>
  metrics: Array<'cpu_usage' | 'memory_usage' | 'disk_usage'>
  title?: string
  height?: number
  showLegend?: boolean
  timeRange?: string
}

export function HistoryChart({
  data,
  metrics,
  title,
  height = 300,
  showLegend = true,
  timeRange,
}: HistoryChartProps) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'

  const formattedData = useMemo(() => {
    return data.map(point => {
      const date = new Date(point.timestamp)
      return {
        ...point,
        time: date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        fullDate: date.toLocaleString(),
      }
    })
  }, [data])

  const metricConfig = {
    cpu_usage: { color: '#3b82f6', label: 'CPU', unit: '%' },
    memory_usage: { color: '#10b981', label: 'Memory', unit: '%' },
    disk_usage: { color: '#f59e0b', label: 'Disk', unit: '%' },
  }

  const gridColor = isDark ? '#374151' : '#e5e7eb'
  const tickColor = isDark ? '#9ca3af' : '#6b7280'
  const textColor = isDark ? '#d1d5db' : '#374151'

  interface CustomTooltipPayload {
    name: string
    value: number
    color: string
    payload: {
      fullDate: string
    }
  }

  const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: CustomTooltipPayload[]; label?: string }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
          <p className="text-sm font-medium text-gray-900 dark:text-white mb-2">
            {payload[0]?.payload?.fullDate || label}
          </p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.value?.toFixed(1)}%
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      {(title || timeRange) && (
        <div className="flex items-center justify-between mb-4">
          {title && (
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              {title}
            </h3>
          )}
          {timeRange && (
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {timeRange}
            </span>
          )}
        </div>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
          <XAxis
            dataKey="time"
            tick={{ fill: tickColor, fontSize: 12 }}
            axisLine={{ stroke: gridColor }}
            tickLine={{ stroke: gridColor }}
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fill: tickColor, fontSize: 12 }}
            axisLine={{ stroke: gridColor }}
            tickLine={{ stroke: gridColor }}
            tickFormatter={(value) => `${value}%`}
          />
          <Tooltip content={<CustomTooltip />} />
          {showLegend && (
            <Legend
              wrapperStyle={{ paddingTop: '20px' }}
              formatter={(value) => (
                <span style={{ color: textColor }}>{value}</span>
              )}
            />
          )}
          {metrics.map(metric => (
            <Line
              key={metric}
              type="monotone"
              dataKey={metric}
              name={metricConfig[metric]?.label || metric}
              stroke={metricConfig[metric]?.color || '#3b82f6'}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
