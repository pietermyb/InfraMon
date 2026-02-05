import { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import {
    Search,
    Filter,
    MoreVertical,
    Play,
    Square,
    RefreshCw,
    Trash2,
    Terminal,
    FileText,
    ExternalLink,
    ChevronUp,
    ChevronDown,
    Download,
} from 'lucide-react'
import { Badge, Button, Card, Input, Tooltip } from '../ui'
import { ContainerResponse } from '../../types'
import { clsx } from 'clsx'

interface ContainerListProps {
    containers: ContainerResponse[]
    onStart: (id: string) => void
    onStop: (id: string) => void
    onRestart: (id: string) => void
    onRemove: (id: string) => void
    isLoading?: boolean
}

type SortField = 'name' | 'image' | 'status' | 'created_at'
type SortOrder = 'asc' | 'desc'

export default function ContainerList({
    containers,
    onStart,
    onStop,
    onRestart,
    onRemove,
    isLoading,
}: ContainerListProps) {
    const [searchTerm, setSearchTerm] = useState('')
    const [statusFilter, setStatusFilter] = useState<string>('all')
    const [sortField, setSortField] = useState<SortField>('name')
    const [sortOrder, setSortOrder] = useState<SortOrder>('asc')
    const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())

    const filteredAndSortedContainers = useMemo(() => {
        return containers
            .filter((c) => {
                const matchesSearch =
                    c.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    c.image?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    c.container_id?.toLowerCase().includes(searchTerm.toLowerCase())
                const matchesStatus = statusFilter === 'all' || c.status === statusFilter
                return matchesSearch && matchesStatus
            })
            .sort((a, b) => {
                const aValue = a[sortField]
                const bValue = b[sortField]

                if (aValue === undefined || bValue === undefined) return 0

                if (sortOrder === 'asc') {
                    return aValue > bValue ? 1 : -1
                } else {
                    return aValue < bValue ? 1 : -1
                }
            })
    }, [containers, searchTerm, statusFilter, sortField, sortOrder])

    const toggleSort = (field: SortField) => {
        if (sortField === field) {
            setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
        } else {
            setSortField(field)
            setSortOrder('asc')
        }
    }

    const toggleSelectAll = () => {
        if (selectedIds.size === filteredAndSortedContainers.length) {
            setSelectedIds(new Set())
        } else {
            setSelectedIds(new Set(filteredAndSortedContainers.map((c) => c.container_id)))
        }
    }

    const toggleSelect = (id: string) => {
        const newSelected = new Set(selectedIds)
        if (newSelected.has(id)) {
            newSelected.delete(id)
        } else {
            newSelected.add(id)
        }
        setSelectedIds(newSelected)
    }

    const getStatusVariant = (status: string) => {
        switch (status.toLowerCase()) {
            case 'running':
                return 'success'
            case 'exited':
            case 'stopped':
                return 'danger'
            case 'paused':
                return 'warning'
            case 'restarting':
                return 'info'
            default:
                return 'default'
        }
    }

    const handleExport = () => {
        const data = filteredAndSortedContainers.map(c => ({
            name: c.name || '-',
            image: c.image || '-',
            status: c.status || '-',
            id: c.container_id || '-',
            created: c.created_at || '-'
        }))
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'containers.json'
        a.click()
    }

    return (
        <div className="space-y-4">
            <Card padding="none" className="overflow-visible">
                <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex flex-wrap items-center justify-between gap-4">
                    <div className="flex items-center space-x-4 flex-1 min-w-[300px]">
                        <div className="relative flex-1">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                            <Input
                                placeholder="Search containers..."
                                className="pl-10"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>
                        <select
                            value={statusFilter}
                            onChange={(e) => setStatusFilter(e.target.value)}
                            className="block w-40 pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                        >
                            <option value="all">All Status</option>
                            <option value="running">Running</option>
                            <option value="exited">Stopped</option>
                            <option value="paused">Paused</option>
                            <option value="restarting">Restarting</option>
                        </select>
                    </div>

                    <div className="flex items-center space-x-2">
                        <Button variant="secondary" size="sm" onClick={handleExport}>
                            <Download className="h-4 w-4 mr-2" />
                            Export
                        </Button>
                        {selectedIds.size > 0 && (
                            <div className="flex items-center space-x-2 bg-primary-50 dark:bg-primary-900/20 px-3 py-1 rounded-md border border-primary-100 dark:border-primary-800">
                                <span className="text-sm font-medium text-primary-700 dark:text-primary-300">
                                    {selectedIds.size} selected
                                </span>
                                <Button variant="ghost" size="sm" className="text-red-600">
                                    <Trash2 className="h-4 w-4" />
                                </Button>
                            </div>
                        )}
                    </div>
                </div>

                <div className="overflow-x-auto scrollbar-thin">
                    <table className="min-w-[1000px] w-full divide-y divide-gray-200 dark:divide-gray-700 table-fixed">
                        <thead className="bg-gray-50 dark:bg-gray-900/50">
                            <tr>
                                <th scope="col" className="w-14 px-6 py-3 text-left whitespace-nowrap">
                                    <input
                                        type="checkbox"
                                        checked={selectedIds.size === filteredAndSortedContainers.length && filteredAndSortedContainers.length > 0}
                                        onChange={toggleSelectAll}
                                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                                    />
                                </th>
                                <th
                                    scope="col"
                                    className="w-80 px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer group whitespace-nowrap"
                                    onClick={() => toggleSort('name')}
                                >
                                    <div className="flex items-center space-x-1">
                                        <span>Name</span>
                                        <span className="flex-none rounded text-gray-400 transition-colors group-hover:text-gray-600">
                                            {sortField === 'name' ? (
                                                sortOrder === 'asc' ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />
                                            ) : (
                                                <ChevronUp className="h-4 w-4 opacity-0 group-hover:opacity-100" />
                                            )}
                                        </span>
                                    </div>
                                </th>
                                <th
                                    scope="col"
                                    className="w-32 px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer group whitespace-nowrap"
                                    onClick={() => toggleSort('status')}
                                >
                                    <div className="flex items-center space-x-1">
                                        <span>Status</span>
                                        {sortField === 'status' && (
                                            sortOrder === 'asc' ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />
                                        )}
                                    </div>
                                </th>
                                <th scope="col" className="w-auto min-w-[300px] px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">
                                    Image
                                </th>
                                <th scope="col" className="w-40 px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">
                                    IP Address
                                </th>
                                <th scope="col" className="w-52 relative px-6 py-3 whitespace-nowrap">
                                    <span className="sr-only">Actions</span>
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                            {filteredAndSortedContainers.map((container) => (
                                <tr
                                    key={container.container_id}
                                    className={clsx(
                                        'transition-all duration-150',
                                        selectedIds.has(container.container_id)
                                            ? 'bg-primary-50 dark:bg-primary-900/40'
                                            : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'
                                    )}
                                >
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <input
                                            type="checkbox"
                                            checked={selectedIds.has(container.container_id)}
                                            onChange={() => toggleSelect(container.container_id)}
                                            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                                        />
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap overflow-hidden">
                                        <div className="flex flex-col max-w-full">
                                            <Link
                                                to={`/containers/${container.container_id}`}
                                                className="text-sm font-semibold text-primary-600 hover:text-primary-500 dark:text-primary-400 truncate block"
                                                title={container.name?.replace(/^\//, '')}
                                            >
                                                {container.name?.replace(/^\//, '') || 'Unknown'}
                                            </Link>
                                            <span className="text-xs text-gray-500 dark:text-gray-400 font-mono truncate">
                                                {container.container_id?.slice(0, 12)}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <Badge variant={getStatusVariant(container.status)}>
                                            {container.status}
                                        </Badge>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap overflow-hidden">
                                        <div className="text-sm text-gray-900 dark:text-gray-100 truncate" title={container.image}>
                                            {container.image}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm text-gray-500 dark:text-gray-400 font-mono">
                                            {/* IP address would come from a more detailed response, but we'll show a placeholder if not present */}
                                            {(container as any).ip_address || '-'}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                        <div className="flex items-center justify-end space-x-2">
                                            {(() => {
                                                const ports = container.ports || {};
                                                const mappedPorts = Object.entries(ports)
                                                    .filter(([_, hostMappings]) => hostMappings && Array.isArray(hostMappings) && hostMappings.length > 0)
                                                    .map(([containerPort, hostMappings]) => ({
                                                        containerPort,
                                                        hostPort: (hostMappings as any)[0].HostPort,
                                                        proto: containerPort.includes('/') ? containerPort.split('/')[1] : 'tcp'
                                                    }))
                                                    .filter(p => p.proto === 'tcp');

                                                if (mappedPorts.length > 0) {
                                                    // Prefer common web ports
                                                    const webPort = mappedPorts.find(p => ['80', '443', '8080', '3000', '5000', '8000'].some(wp => p.containerPort.startsWith(wp))) || mappedPorts[0];
                                                    const protocol = webPort.containerPort.startsWith('443') ? 'https' : 'http';
                                                    const url = `${protocol}://${window.location.hostname}:${webPort.hostPort}`;

                                                    return (
                                                        <Tooltip content={`Open in Browser (${webPort.hostPort})`}>
                                                            <a href={url} target="_blank" rel="noopener noreferrer">
                                                                <Button variant="ghost" size="sm" className="p-1.5 text-blue-600 hover:text-blue-700 hover:bg-blue-50 dark:hover:bg-blue-900/20">
                                                                    <ExternalLink className="h-4 w-4" />
                                                                </Button>
                                                            </a>
                                                        </Tooltip>
                                                    );
                                                }
                                                return null;
                                            })()}
                                            <Tooltip content="Live Logs">
                                                <Link to={`/containers/${container.container_id}?tab=logs`}>
                                                    <Button variant="ghost" size="sm" className="p-1.5">
                                                        <FileText className="h-4 w-4" />
                                                    </Button>
                                                </Link>
                                            </Tooltip>
                                            <Tooltip content="Attach Shell">
                                                <Link to={`/containers/${container.container_id}?tab=shell`}>
                                                    <Button variant="ghost" size="sm" className="p-1.5">
                                                        <Terminal className="h-4 w-4" />
                                                    </Button>
                                                </Link>
                                            </Tooltip>
                                            <div className="h-4 w-px bg-gray-300 dark:bg-gray-600 mx-1" />
                                            {container.status === 'running' ? (
                                                <Tooltip content="Stop">
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        className="p-1.5 text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
                                                        onClick={() => onStop(container.container_id)}
                                                    >
                                                        <Square className="h-4 w-4" />
                                                    </Button>
                                                </Tooltip>
                                            ) : (
                                                <Tooltip content="Start">
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        className="p-1.5 text-green-600 hover:text-green-700 hover:bg-green-50 dark:hover:bg-green-900/20"
                                                        onClick={() => onStart(container.container_id)}
                                                    >
                                                        <Play className="h-4 w-4" />
                                                    </Button>
                                                </Tooltip>
                                            )}
                                            <Tooltip content="Restart">
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    className="p-1.5 text-yellow-600 hover:text-yellow-700 hover:bg-yellow-50 dark:hover:bg-yellow-900/20"
                                                    onClick={() => onRestart(container.container_id)}
                                                >
                                                    <RefreshCw className="h-4 w-4" />
                                                </Button>
                                            </Tooltip>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                            {filteredAndSortedContainers.length === 0 && !isLoading && (
                                <tr>
                                    <td colSpan={6} className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                                        <div className="flex flex-col items-center">
                                            <Filter className="h-10 w-10 text-gray-400 mb-2" />
                                            <p className="text-lg font-medium">No containers found</p>
                                            <p className="text-sm">Try adjusting your search or filters</p>
                                        </div>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    )
}
