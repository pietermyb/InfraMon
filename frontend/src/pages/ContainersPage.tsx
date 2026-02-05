import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../api/client'
import ContainerList from '../components/containers/ContainerList'
import ContainerGroups from '../components/containers/ContainerGroups'
import { ContainerResponse, ContainerListResponse } from '../types'
import { RefreshCw, LayoutGrid, Box, Activity } from 'lucide-react'
import { Button, Card, Spinner } from '../components/ui'

export default function ContainersPage() {
  const [selectedGroupName, setSelectedGroupName] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const { data: containerData, isLoading } = useQuery<ContainerListResponse>({
    queryKey: ['containers'],
    queryFn: async () => {
      const response = await api.get('/containers', {
        params: {
          all_containers: true,
        },
      })
      return (response.data as any).data
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

  const removeMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/containers/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['containers'] })
    },
  })

  return (
    <div className="flex flex-col space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
            <Box className="h-8 w-8 mr-3 text-primary-600" />
            Container Management
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Monitor and control your Docker infrastructure from one place.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="secondary"
            onClick={() => queryClient.invalidateQueries({ queryKey: ['containers'] })}
            isLoading={isLoading}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-5 gap-6">
        <aside className="md:col-span-1 lg:col-span-1 space-y-6">
          <Card padding="sm" className="sticky top-6">
            <ContainerGroups
              containers={containerData?.containers || []}
              selectedGroupName={selectedGroupName}
              onSelectGroup={setSelectedGroupName}
            />
          </Card>

          <Card padding="sm">
            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">Quick Stats</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Running</span>
                <span className="text-sm font-bold text-green-600">{containerData?.running || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Stopped</span>
                <span className="text-sm font-bold text-gray-500">{containerData?.stopped || 0}</span>
              </div>
              <div className="pt-4 border-t border-gray-100 dark:border-gray-700">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-500">Resource Load</span>
                  <Activity className="h-3 w-3 text-primary-500" />
                </div>
                <div className="w-full bg-gray-100 dark:bg-gray-800 rounded-full h-1.5">
                  <div className="bg-primary-600 h-1.5 rounded-full" style={{ width: '45%' }}></div>
                </div>
              </div>
            </div>
          </Card>
        </aside>

        <main className="md:col-span-3 lg:col-span-4 transition-all duration-300">
          <ContainerList
            containers={(containerData?.containers || []).filter(c => {
              if (!selectedGroupName) return true;
              const labels = (c as any).labels || {};
              const project = labels['com.docker.compose.project'] || labels['com.docker.stack.namespace'];
              if (project) return project === selectedGroupName;

              const name = c.name.replace(/^\//, '');
              const parts = name.split(/[-_]/);
              const prefix = parts.length > 1 ? parts[0] : 'Independent';
              return prefix === selectedGroupName;
            })}
            onStart={(id) => startMutation.mutate(id)}
            onStop={(id) => stopMutation.mutate(id)}
            onRestart={(id) => restartMutation.mutate(id)}
            onRemove={(id) => removeMutation.mutate(id)}
            isLoading={isLoading}
          />
        </main>
      </div>
    </div>
  )
}
