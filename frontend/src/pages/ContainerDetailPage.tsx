import { useState } from 'react'
import { useParams, useSearchParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../api/client'
import { ContainerDetailResponse } from '../types'
import {
  Box, Activity, Terminal as TerminalIcon, FileText, Search, Settings,
  Layout, Layers, Play, Square, RefreshCw, Trash2, ExternalLink, ChevronLeft
} from 'lucide-react'
// Last updated: 2026-02-05 12:51
import { Button, Card, Spinner, Badge } from '../components/ui'
import LogViewer from '../components/containers/LogViewer'
import Terminal from '../components/containers/Terminal'
import ContainerStats from '../components/containers/ContainerStats'
import ComposeDetails from '../components/containers/ComposeDetails'
import RemoveContainerModal from '../components/containers/RemoveContainerModal'
import { clsx } from 'clsx'

export default function ContainerDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [searchParams, setSearchParams] = useSearchParams()
  const activeTab = searchParams.get('tab') || 'overview'
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [isRemoveModalOpen, setIsRemoveModalOpen] = useState(false)

  const { data: container, isLoading, error } = useQuery<ContainerDetailResponse>({
    queryKey: ['container', id],
    queryFn: async () => {
      const response = await api.get(`/containers/${id}`)
      return response.data
    },
    refetchInterval: 5000,
  })

  const startMutation = useMutation({
    mutationFn: async () => api.post(`/containers/${id}/start`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['container', id] }),
  })

  const stopMutation = useMutation({
    mutationFn: async () => api.post(`/containers/${id}/stop`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['container', id] }),
  })

  const restartMutation = useMutation({
    mutationFn: async () => api.post(`/containers/${id}/restart`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['container', id] }),
  })

  const removeMutation = useMutation({
    mutationFn: async () => api.delete(`/containers/${id}`),
    onSuccess: () => navigate('/containers'),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    )
  }

  if (error || !container) {
    return (
      <Card className="max-w-md mx-auto mt-12 p-8 text-center">
        <div className="bg-red-100 dark:bg-red-900/20 h-16 w-16 rounded-full flex items-center justify-center mx-auto mb-4">
          <Box className="h-8 w-8 text-red-600" />
        </div>
        <h2 className="text-xl font-bold mb-2">Container Not Found</h2>
        <p className="text-gray-500 mb-6">The container you are looking for does not exist or has been removed.</p>
        <Button onClick={() => navigate('/containers')}>Back to Containers</Button>
      </Card>
    )
  }

  const tabs = [
    { id: 'overview', name: 'Overview', icon: Layout },
    { id: 'logs', name: 'Logs', icon: FileText },
    { id: 'shell', name: 'Terminal', icon: TerminalIcon },
    { id: 'stats', name: 'Statistics', icon: Activity },
    { id: 'compose', name: 'Docker Compose', icon: Layers },
    { id: 'inspect', name: 'Inspect', icon: Search },
  ]

  const handleTabChange = (tabId: string) => {
    setSearchParams({ tab: tabId })
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm" onClick={() => navigate('/containers')} className="p-2">
            <ChevronLeft className="h-5 w-5" />
          </Button>
          <div>
            <div className="flex items-center space-x-3 mb-1">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white uppercase">
                {container.name.replace(/^\//, '')}
              </h1>
              <Badge variant={container.status === 'running' ? 'success' : 'danger'}>
                {container.status}
              </Badge>
            </div>
            <p className="text-xs text-gray-500 font-mono">ID: {container.container_id}</p>
          </div>
        </div>

        <div className="flex items-center gap-2 bg-white dark:bg-gray-800 p-1.5 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
          {(() => {
            const ports = (container as any).ports || {};
            const mappedPorts = Object.entries(ports)
              .filter(([_, hostMappings]) => hostMappings && Array.isArray(hostMappings) && hostMappings.length > 0)
              .map(([containerPort, hostMappings]) => ({
                containerPort,
                hostPort: (hostMappings as any)[0].HostPort,
                proto: containerPort.includes('/') ? containerPort.split('/')[1] : 'tcp'
              }))
              .filter(p => p.proto === 'tcp');

            if (mappedPorts.length > 0) {
              const webPort = mappedPorts.find(p => ['80', '443', '8080', '3000', '5000', '8000'].some(wp => p.containerPort.startsWith(wp))) || mappedPorts[0];
              const protocol = webPort.containerPort.startsWith('443') ? 'https' : 'http';
              const url = `${protocol}://${window.location.hostname}:${webPort.hostPort}`;

              return (
                <a href={url} target="_blank" rel="noopener noreferrer">
                  <Button variant="secondary" size="sm" className="text-blue-600 border-blue-100 dark:border-blue-900/30">
                    <ExternalLink className="h-3.5 w-3.5 mr-1.5" />
                    Open
                  </Button>
                </a>
              );
            }
            return null;
          })()}
          <div className="w-px h-6 bg-gray-200 dark:bg-gray-700 mx-1" />
          {container.status === 'running' ? (
            <Button variant="secondary" size="sm" onClick={() => stopMutation.mutate()} isLoading={stopMutation.isPending}>
              <Square className="h-3.5 w-3.5 mr-1.5 fill-current" />
              Stop
            </Button>
          ) : (
            <Button variant="secondary" size="sm" onClick={() => startMutation.mutate()} isLoading={startMutation.isPending}>
              <Play className="h-3.5 w-3.5 mr-1.5 fill-current" />
              Start
            </Button>
          )}
          <Button variant="secondary" size="sm" onClick={() => restartMutation.mutate()} isLoading={restartMutation.isPending}>
            <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
            Restart
          </Button>
          <div className="w-px h-6 bg-gray-200 dark:bg-gray-700 mx-1" />
          <Button variant="ghost" size="sm" className="text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20" onClick={() => setIsRemoveModalOpen(true)}>
            <Trash2 className="h-3.5 w-3.5 text-red-500" />
            <span className="ml-1.5 hidden sm:inline">Remove</span>
          </Button>
        </div>
      </div>

      <div className="border-b border-gray-200 dark:border-gray-700 transition-all">
        <nav className="-mb-px flex space-x-8 overflow-x-auto overflow-y-hidden" aria-label="Tabs">
          {tabs.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => handleTabChange(tab.id)}
                className={clsx(
                  "group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap transition-all",
                  isActive
                    ? "border-primary-500 text-primary-600 dark:text-primary-400"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200"
                )}
              >
                <Icon className={clsx(
                  "mr-2 h-5 w-5 transition-colors",
                  isActive ? "text-primary-500" : "text-gray-400 group-hover:text-gray-500"
                )} />
                {tab.name}
              </button>
            )
          })}
        </nav>
      </div>

      <div className="mt-6 animation-fade-in">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-2">
              <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-6 flex items-center">
                <Layout className="h-4 w-4 mr-2" />
                Container Information
              </h3>
              <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-6">
                <div>
                  <dt className="text-xs font-semibold text-gray-500 uppercase tracking-tighter">Image</dt>
                  <dd className="mt-1 text-sm font-medium text-gray-900 dark:text-white break-all">{container.image}</dd>
                </div>
                <div>
                  <dt className="text-xs font-semibold text-gray-500 uppercase tracking-tighter">Command</dt>
                  <dd className="mt-1 text-sm text-gray-900 dark:text-white font-mono bg-gray-50 dark:bg-gray-900/50 p-1.5 rounded border border-gray-100 dark:border-gray-800">
                    {Array.isArray(container.command) ? container.command.join(' ') : (container.command || 'N/A')}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs font-semibold text-gray-500 uppercase tracking-tighter">Started At</dt>
                  <dd className="mt-1 text-sm text-gray-900 dark:text-white">{container.started_at || 'Not started'}</dd>
                </div>
                <div>
                  <dt className="text-xs font-semibold text-gray-500 uppercase tracking-tighter">IP Address</dt>
                  <dd className="mt-1 text-sm text-gray-900 dark:text-white font-mono">{container.ip_address || 'N/A'}</dd>
                </div>
              </dl>

              <h4 className="text-xs font-bold text-gray-400 uppercase mt-10 mb-4 tracking-widest">Port Mappings</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {container.ports && Object.keys(container.ports).length > 0 ? (
                  Object.entries(container.ports).map(([containerPort, hostPorts]) => (
                    <div key={containerPort} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-900/50 rounded border border-gray-100 dark:border-gray-800">
                      <span className="text-xs font-mono text-gray-500">{containerPort}</span>
                      <ChevronLeft className="h-3 w-3 rotate-180 text-gray-300" />
                      <span className="text-sm font-bold text-primary-600">
                        {Array.isArray(hostPorts) ? hostPorts.map(p => `${p.HostIp}:${p.HostPort}`).join(', ') : 'None'}
                      </span>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-gray-500 italic">No ports mapped</p>
                )}
              </div>
            </Card>

            <Card>
              <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-6 flex items-center">
                <Settings className="h-4 w-4 mr-2" />
                Environment
              </h3>
              <div className="space-y-3 max-h-[500px] overflow-auto pr-2">
                {container.environment && container.environment.length > 0 ? (
                  container.environment.map((env, idx) => (
                    <div key={idx} className="p-2 bg-gray-50 dark:bg-gray-900/50 rounded border border-gray-100 dark:border-gray-800">
                      <div className="text-[10px] font-bold text-gray-500 uppercase truncate mb-1" title={env.name}>{env.name}</div>
                      <div className="text-xs font-mono text-gray-900 dark:text-gray-100 break-all">{env.value}</div>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-gray-500 italic">No environment variables defined</p>
                )}
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'logs' && <LogViewer containerId={id || ''} />}

        {activeTab === 'shell' && <Terminal containerId={id || ''} />}

        {activeTab === 'stats' && <ContainerStats containerId={id || ''} />}

        {activeTab === 'compose' && <ComposeDetails containerId={id || ''} />}

        {activeTab === 'inspect' && (
          <Card padding="none" className="bg-gray-950 overflow-hidden border border-gray-800">
            <div className="bg-gray-800 px-4 py-2 border-b border-gray-700 flex justify-between items-center">
              <span className="text-xs font-bold text-gray-400 uppercase">Container Inspection (JSON)</span>
              <Button variant="ghost" size="sm" className="h-6 text-[10px]">Copy JSON</Button>
            </div>
            <pre className="p-6 overflow-auto max-h-[700px] text-xs font-mono text-blue-400">
              {JSON.stringify(container, null, 2)}
            </pre>
          </Card>
        )}
      </div>

      <RemoveContainerModal
        isOpen={isRemoveModalOpen}
        onClose={() => setIsRemoveModalOpen(false)}
        containerName={container.name}
        onConfirm={() => {
          removeMutation.mutate();
        }}
        isPending={removeMutation.isPending}
      />
    </div>
  )
}
