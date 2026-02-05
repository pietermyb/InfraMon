import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'
import { clsx } from 'clsx'
import { useTheme } from '../../hooks/useTheme'

interface DonutChartProps {
  data: Array<{
    name: string
    value: number
    color?: string
  }>
  title?: string
  size?: number
  innerRadius?: number
  showLegend?: boolean
  showLabels?: boolean
}

export function DonutChart({
  data,
  title,
  size = 200,
  innerRadius = 60,
  showLegend = true,
  showLabels = true,
}: DonutChartProps) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'

  const defaultColors = [
    '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
    '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1',
  ]

  const chartData = data.map((item, index) => ({
    ...item,
    color: item.color || defaultColors[index % defaultColors.length],
  }))

  const total = data.reduce((sum, item) => sum + item.value, 0)

  interface TooltipPayload {
    name: string
    value: number
    color: string
    payload?: {
      name: string
      value: number
    }
  }

  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: TooltipPayload[] }) => {
    if (active && payload && payload.length) {
      const data = payload[0]
      const percentage = total > 0 ? ((data?.value || 0) / total * 100).toFixed(1) : 0
      return (
        <div className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
          <p className="text-sm font-medium text-gray-900 dark:text-white">
            {data?.name}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {data?.value?.toLocaleString()} ({percentage}%)
          </p>
        </div>
      )
    }
    return null
  }

  const CustomLegend = ({ payload }: { payload?: Array<{ value: string; color: string }> }) => (
    <div className="flex flex-wrap justify-center gap-4 mt-4">
      {payload?.map((entry, index) => (
        <div key={index} className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {entry.value}
          </span>
        </div>
      ))}
    </div>
  )

  return (
    <div className={clsx('bg-white dark:bg-gray-800 shadow rounded-lg p-6', !title && 'h-full')}>
      {title && (
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          {title}
        </h3>
      )}
      <div className="flex flex-col items-center">
        <ResponsiveContainer width="100%" height={size}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={innerRadius}
              outerRadius={size / 2 - 10}
              paddingAngle={2}
              dataKey="value"
              label={showLabels ? ({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%` : false}
              labelLine={showLabels}
              isAnimationActive={false}
            >
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.color}
                  stroke={isDark ? '#1f2937' : '#ffffff'}
                  strokeWidth={2}
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
        {showLegend && <CustomLegend payload={chartData.map(d => ({ value: d.name, color: d.color }))} />}
        <div className="mt-4 text-center">
          <div className="text-3xl font-bold text-gray-900 dark:text-white">
            {total.toLocaleString()}
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400">Total</div>
        </div>
      </div>
    </div>
  )
}
