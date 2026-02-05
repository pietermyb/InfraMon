import { useQuery } from '@tanstack/react-query'
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    LineChart,
    Line,
} from 'recharts'
import { Card, Spinner, Badge, ProgressBar } from '../ui'
import api from '../../api/client'
import { ContainerStatsResponse, FormattedStats } from '../../types'
import { format } from 'date-fns'
import { Cpu, MemoryStick as Memory, Activity, HardDrive, Network } from 'lucide-react'

interface ContainerStatsProps {
    containerId: string
}

export default function ContainerStats({ containerId }: ContainerStatsProps) {
    const { data: stats, isLoading } = useQuery<ContainerStatsResponse[]>({
        queryKey: ['container-stats', containerId],
        queryFn: async () => {
            const response = await api.get(`/containers/${containerId}/stats/history`, {
                params: { period: '1h' }
            })
            return response.data.stats
        },
        refetchInterval: 5000,
    })

    const latestStats = stats?.[stats.length - 1]

    const formatByteSize = (bytes: number) => {
        if (bytes === 0) return '0 B'
        const k = 1024
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
        const i = Math.floor(Math.log(bytes) / Math.log(k))
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Spinner size="lg" />
            </div>
        )
    }

    const chartData = stats?.map(s => ({
        time: format(new Date(s.timestamp), 'HH:mm:ss'),
        cpu: s.cpu_usage,
        memory: s.memory_usage / 1024 / 1024, // MB
        network_rx: s.network_rx / 1024, // KB
        network_tx: s.network_tx / 1024, // KB
    }))

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card className="flex flex-col">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-500 font-medium uppercase tracking-wider">CPU Usage</span>
                        <Cpu className="h-4 w-4 text-primary-500" />
                    </div>
                    <div className="text-2xl font-bold mb-2">{latestStats?.cpu_usage.toFixed(2)}%</div>
                    <ProgressBar value={latestStats?.cpu_usage || 0} color="primary" size="sm" />
                </Card>

                <Card className="flex flex-col">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-500 font-medium uppercase tracking-wider">Memory</span>
                        <Memory className="h-4 w-4 text-purple-500" />
                    </div>
                    <div className="text-2xl font-bold mb-1">
                        {formatByteSize(latestStats?.memory_usage || 0)}
                    </div>
                    <div className="text-xs text-gray-500 mb-2">
                        Limit: {formatByteSize(latestStats?.memory_limit || 0)}
                    </div>
                    <ProgressBar
                        value={latestStats ? (latestStats.memory_usage / latestStats.memory_limit) * 100 : 0}
                        color="primary"
                        size="sm"
                    />
                </Card>

                <Card className="flex flex-col">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-500 font-medium uppercase tracking-wider">Network I/O</span>
                        <Network className="h-4 w-4 text-blue-500" />
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                        <div>
                            <div className="text-[10px] text-gray-400 uppercase">RX</div>
                            <div className="text-sm font-bold">{formatByteSize(latestStats?.network_rx || 0)}</div>
                        </div>
                        <div>
                            <div className="text-[10px] text-gray-400 uppercase">TX</div>
                            <div className="text-sm font-bold">{formatByteSize(latestStats?.network_tx || 0)}</div>
                        </div>
                    </div>
                </Card>

                <Card className="flex flex-col">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-500 font-medium uppercase tracking-wider">Block I/O</span>
                        <HardDrive className="h-4 w-4 text-orange-500" />
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                        <div>
                            <div className="text-[10px] text-gray-400 uppercase">Read</div>
                            <div className="text-sm font-bold">{formatByteSize(latestStats?.block_read || 0)}</div>
                        </div>
                        <div>
                            <div className="text-[10px] text-gray-400 uppercase">Write</div>
                            <div className="text-sm font-bold">{formatByteSize(latestStats?.block_write || 0)}</div>
                        </div>
                    </div>
                </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="h-80">
                    <h3 className="text-sm font-bold text-gray-700 dark:text-gray-300 mb-4 flex items-center">
                        <Activity className="h-4 w-4 mr-2 text-primary-500" />
                        CPU Utilization (%)
                    </h3>
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={chartData}>
                            <defs>
                                <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#374151" opacity={0.1} />
                            <XAxis dataKey="time" hide />
                            <YAxis />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#fff' }}
                                itemStyle={{ color: '#0ea5e9' }}
                            />
                            <Area type="monotone" dataKey="cpu" stroke="#0ea5e9" fillOpacity={1} fill="url(#colorCpu)" />
                        </AreaChart>
                    </ResponsiveContainer>
                </Card>

                <Card className="h-80">
                    <h3 className="text-sm font-bold text-gray-700 dark:text-gray-300 mb-4 flex items-center">
                        <Memory className="h-4 w-4 mr-2 text-purple-500" />
                        Memory Usage (MB)
                    </h3>
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={chartData}>
                            <defs>
                                <linearGradient id="colorMem" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#a855f7" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#374151" opacity={0.1} />
                            <XAxis dataKey="time" hide />
                            <YAxis />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#fff' }}
                                itemStyle={{ color: '#a855f7' }}
                            />
                            <Area type="monotone" dataKey="memory" stroke="#a855f7" fillOpacity={1} fill="url(#colorMem)" />
                        </AreaChart>
                    </ResponsiveContainer>
                </Card>
            </div>

            <Card className="h-80">
                <h3 className="text-sm font-bold text-gray-700 dark:text-gray-300 mb-4 flex items-center">
                    <Network className="h-4 w-4 mr-2 text-blue-500" />
                    Network Throughput (KB/s)
                </h3>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#374151" opacity={0.1} />
                        <XAxis dataKey="time" hide />
                        <YAxis />
                        <Tooltip
                            contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#fff' }}
                        />
                        <Line type="monotone" dataKey="network_rx" stroke="#3b82f6" dot={false} strokeWidth={2} name="RX" />
                        <Line type="monotone" dataKey="network_tx" stroke="#10b981" dot={false} strokeWidth={2} name="TX" />
                    </LineChart>
                </ResponsiveContainer>
            </Card>
        </div>
    )
}
