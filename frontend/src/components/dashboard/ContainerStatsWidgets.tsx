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

      <div className="bg-canvas-card border border-border-subtle shadow-sm rounded-2xl p-6">
        <h3 className="text-lg font-bold text-text-title mb-6">
          Resource Distribution
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="text-4xl font-extrabold text-text-title">
              {containers.running}
            </div>
            <div className="text-sm font-semibold text-text-body mt-1 uppercase tracking-wider">Running</div>
            <div className="mt-4 w-full bg-gray-100 dark:bg-gray-800 rounded-full h-2.5 overflow-hidden">
              <div
                className="bg-green-500 h-full rounded-full transition-all duration-1000"
                style={{ width: `${(containers.running / Math.max(1, containers.total_containers)) * 100}%` }}
              />
            </div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-extrabold text-text-title">
              {containers.stopped}
            </div>
            <div className="text-sm font-semibold text-text-body mt-1 uppercase tracking-wider">Stopped</div>
            <div className="mt-4 w-full bg-gray-100 dark:bg-gray-800 rounded-full h-2.5 overflow-hidden">
              <div
                className="bg-gray-400 h-full rounded-full transition-all duration-1000"
                style={{ width: `${(containers.stopped / Math.max(1, containers.total_containers)) * 100}%` }}
              />
            </div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-extrabold text-text-title">
              {containers.paused}
            </div>
            <div className="text-sm font-semibold text-text-body mt-1 uppercase tracking-wider">Paused</div>
            <div className="mt-4 w-full bg-gray-100 dark:bg-gray-800 rounded-full h-2.5 overflow-hidden">
              <div
                className="bg-yellow-500 h-full rounded-full transition-all duration-1000"
                style={{ width: `${(containers.paused / Math.max(1, containers.total_containers)) * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
