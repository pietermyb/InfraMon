import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api/v1'

interface ContainerDetail {
  container_id: string
  name: string
  image: string
  status: string
  ports: Record<string, any>
  volumes: any
  environment: { name: string; value: string }[]
  networks: string[]
  labels: Record<string, string>
  command: string
  created: string
  started_at: string
  restart_policy: { Name: string }
  healthcheck: { test: string[]; interval: number; timeout: number; retries: number }
}

export default function ContainerDetailPage() {
  const { id } = useParams<{ id: string }>()
  
  const { data: container, isLoading, error } = useQuery<ContainerDetail>({
    queryKey: ['container', id],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/containers/${id}`)
      return response.data
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading container details...</div>
      </div>
    )
  }

  if (error || !container) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-500">Container not found</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{container.name}</h1>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
          container.status === 'running'
            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
            : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
        }`}>
          {container.status}
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">General Information</h3>
          <dl className="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Container ID</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-white">{container.container_id.slice(0, 12)}</dd>
            </div>
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Image</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-white">{container.image}</dd>
            </div>
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Command</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-white font-mono">{container.command || 'N/A'}</dd>
            </div>
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Restart Policy</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-white">{container.restart_policy?.Name || 'N/A'}</dd>
            </div>
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Created</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-white">{container.created || 'N/A'}</dd>
            </div>
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Started At</dt>
              <dd className="mt-1 text-sm text-gray-900 dark:text-white">{container.started_at || 'N/A'}</dd>
            </div>
          </dl>
        </div>

        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Ports</h3>
          {container.ports && Object.keys(container.ports).length > 0 ? (
            <ul className="divide-y divide-gray-200 dark:divide-gray-700">
              {Object.entries(container.ports).map(([containerPort, hostPorts]) => (
                <li key={containerPort} className="py-2">
                  <span className="text-sm text-gray-900 dark:text-white">
                    {containerPort} → {Array.isArray(hostPorts) ? hostPorts.join(', ') : hostPorts}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500 dark:text-gray-400">No ports mapped</p>
          )}
        </div>

        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Environment Variables</h3>
          {container.environment && container.environment.length > 0 ? (
            <ul className="divide-y divide-gray-200 dark:divide-gray-700 max-h-64 overflow-y-auto">
              {container.environment.map((env) => (
                <li key={env.name} className="py-2">
                  <span className="text-sm text-gray-900 dark:text-white font-mono break-all">
                    {env.name}={env.value}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500 dark:text-gray-400">No environment variables</p>
          )}
        </div>

        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Networks</h3>
          {container.networks && container.networks.length > 0 ? (
            <ul className="divide-y divide-gray-200 dark:divide-gray-700">
              {container.networks.map((network) => (
                <li key={network} className="py-2">
                  <span className="text-sm text-gray-900 dark:text-white">{network}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500 dark:text-gray-400">No networks</p>
          )}
        </div>

        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 lg:col-span-2">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Labels</h3>
          {container.labels && Object.keys(container.labels).length > 0 ? (
            <ul className="divide-y divide-gray-200 dark:divide-gray-700">
              {Object.entries(container.labels).map(([key, value]) => (
                <li key={key} className="py-2 flex justify-between">
                  <span className="text-sm text-gray-500 dark:text-gray-400">{key}</span>
                  <span className="text-sm text-gray-900 dark:text-white font-mono">{value}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500 dark:text-gray-400">No labels</p>
          )}
        </div>
      </div>
    </div>
  )
}
