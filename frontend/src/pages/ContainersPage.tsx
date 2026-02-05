import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import api from '../api/client'

interface Container {
  id: string
  short_id: string
  name: string
  image: string
  status: string
  compose_file: string | null
  labels: Record<string, string>
  ports: Record<string, any>
}

interface ContainerListResponse {
  success: boolean
  data: {
    containers: Container[]
    total: number
    running: number
    stopped: number
  }
}

export default function ContainersPage() {
  const [showAll, setShowAll] = useState(false)
  const queryClient = useQueryClient()

  const { data: containers, isLoading } = useQuery<Container[]>({
    queryKey: ['containers', showAll],
    queryFn: async () => {
      const response = await api.get<ContainerListResponse>('/containers', {
        params: { all_containers: showAll },
      })
      return response.data.data.containers
    },
    refetchInterval: 10000,
  })

  const startMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.post(`/containers/${id}/start`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['containers'] })
    },
  })

  const stopMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.post(`/containers/${id}/stop`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['containers'] })
    },
  })

  const restartMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.post(`/containers/${id}/restart`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['containers'] })
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading containers...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Containers</h1>
        <div className="flex items-center space-x-4">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={showAll}
              onChange={(e) => setShowAll(e.target.checked)}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-gray-700 dark:text-gray-300">Show all containers</span>
          </label>
          <button
            onClick={() => queryClient.invalidateQueries({ queryKey: ['containers'] })}
            className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200 dark:divide-gray-700">
          {containers?.map((container) => (
            <li key={container.id} className="px-4 py-4 sm:px-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    container.status === 'running'
                      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                      : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                  }`}>
                    {container.status}
                  </span>
                  <div>
                    <p className="text-sm font-medium text-primary-600 dark:text-primary-400">
                      {container.name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {container.short_id}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Link
                    to={`/containers/${container.short_id}`}
                    className="px-3 py-1 text-sm text-primary-600 hover:text-primary-500"
                  >
                    Details
                  </Link>
                  {container.status === 'running' ? (
                    <button
                      onClick={() => stopMutation.mutate(container.short_id)}
                      className="px-3 py-1 text-sm text-red-600 hover:text-red-500"
                    >
                      Stop
                    </button>
                  ) : (
                    <button
                      onClick={() => startMutation.mutate(container.short_id)}
                      className="px-3 py-1 text-sm text-green-600 hover:text-green-500"
                    >
                      Start
                    </button>
                  )}
                  <button
                    onClick={() => restartMutation.mutate(container.short_id)}
                    className="px-3 py-1 text-sm text-yellow-600 hover:text-yellow-500"
                  >
                    Restart
                  </button>
                </div>
              </div>
              <div className="mt-2">
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Image: {container.image}
                </p>
              </div>
            </li>
          ))}
        </ul>
        {(!containers || containers.length === 0) && (
          <div className="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
            No containers found
          </div>
        )}
      </div>
    </div>
  )
}
