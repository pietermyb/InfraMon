import { clsx } from 'clsx'
import { DashboardResponse } from '../../types'
import { StatCard } from './StatCard'
import {
  CubeIcon,
  PlayCircleIcon,
  PauseCircleIcon,
  StopCircleIcon,
} from '@heroicons/react/24/outline'

interface ContainerStatsWidgetsProps {
  data: DashboardResponse
  className?: string
}

export function ContainerStatsWidgets({ data, className }: ContainerStatsWidgetsProps) {
  const { containers } = data

  return (
    <div className={clsx('space-y-6', className)}>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Containers"
          value={containers.total_containers}
          icon={<CubeIcon className="h-6 w-6" />}
          color="default"
        />
        <StatCard
          title="Running"
          value={containers.running}
          icon={<PlayCircleIcon className="h-6 w-6 text-green-500" />}
          color="success"
        />
        <StatCard
          title="Stopped"
          value={containers.stopped}
          icon={<StopCircleIcon className="h-6 w-6 text-gray-500" />}
          color="default"
        />
        <StatCard
          title="Paused"
          value={containers.paused}
          icon={<PauseCircleIcon className="h-6 w-6 text-yellow-500" />}
          color="warning"
        />
      </div>

      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Resource Distribution
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-4xl font-bold text-gray-900 dark:text-white">
              {containers.running}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">Running</div>
            <div className="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-green-500 h-2 rounded-full transition-all"
                style={{ width: `${(containers.running / Math.max(1, containers.total_containers)) * 100}%` }}
              />
            </div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-gray-900 dark:text-white">
              {containers.stopped}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">Stopped</div>
            <div className="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-gray-500 h-2 rounded-full transition-all"
                style={{ width: `${(containers.stopped / Math.max(1, containers.total_containers)) * 100}%` }}
              />
            </div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-gray-900 dark:text-white">
              {containers.paused}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">Paused</div>
            <div className="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-yellow-500 h-2 rounded-full transition-all"
                style={{ width: `${(containers.paused / Math.max(1, containers.total_containers)) * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
