import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { useTheme } from '../../hooks/useTheme'

interface AreaChartProps {
  data: Array<{
    timestamp: string
    rx_bytes: number
    tx_bytes: number
  }>
  title?: string
  height?: number
  incomingLabel?: string
  outgoingLabel?: string
}

export function NetworkTrafficChart({
  data,
  title,
  height = 200,
  incomingLabel = 'Inbound',
  outgoingLabel = 'Outbound',
}: AreaChartProps) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'

  const formatBytes = (bytes: number) => {
    if (bytes >= 1e9) return `${(bytes / 1e9).toFixed(1)} GB`
    if (bytes >= 1e6) return `${(bytes / 1e6).toFixed(1)} MB`
    if (bytes >= 1e3) return `${(bytes / 1e3).toFixed(1)} KB`
    return `${bytes} B`
  }

  const formattedData = data.map(point => ({
    ...point,
    time: new Date(point.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    fullDate: new Date(point.timestamp).toLocaleString(),
    rx_display: formatBytes(point.rx_bytes),
    tx_display: formatBytes(point.tx_bytes),
  }))

  const gridColor = isDark ? '#374151' : '#e5e7eb'
  const tickColor = isDark ? '#9ca3af' : '#6b7280'

  interface NetworkTooltipPayload {
    name: string
    value: number
    payload: {
      rx_display?: string
      tx_display?: string
      fullDate?: string
    }
  }

  const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: NetworkTooltipPayload[]; label?: string }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
          <p className="text-sm font-medium text-gray-900 dark:text-white mb-2">
            {payload[0]?.payload?.fullDate || label}
          </p>
          <p className="text-sm text-blue-500">
            {incomingLabel}: {payload[0]?.payload?.rx_display || formatBytes(payload[0]?.value || 0)}
          </p>
          {payload[1] && (
            <p className="text-sm text-green-500">
              {outgoingLabel}: {payload[1]?.payload?.tx_display || formatBytes(payload[1]?.value || 0)}
            </p>
          )}
        </div>
      )
    }
    return null
  }

  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      {title && (
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          {title}
        </h3>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={formattedData}>
          <defs>
            <linearGradient id="rxGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="txGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
          <XAxis
            dataKey="time"
            tick={{ fill: tickColor, fontSize: 12 }}
            axisLine={{ stroke: gridColor }}
            tickLine={{ stroke: gridColor }}
          />
          <YAxis
            tick={{ fill: tickColor, fontSize: 12 }}
            axisLine={{ stroke: gridColor }}
            tickLine={{ stroke: gridColor }}
            tickFormatter={(value) => formatBytes(value)}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="rx_bytes"
            name={incomingLabel}
            stroke="#3b82f6"
            strokeWidth={2}
            fill="url(#rxGradient)"
            isAnimationActive={false}
          />
          <Area
            type="monotone"
            dataKey="tx_bytes"
            name={outgoingLabel}
            stroke="#10b981"
            strokeWidth={2}
            fill="url(#txGradient)"
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
