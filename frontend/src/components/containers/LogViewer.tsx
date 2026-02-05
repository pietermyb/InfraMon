import { useState, useEffect, useRef } from 'react'
import { Terminal, Download, Trash2, Pause, Play, ChevronDown, Clock, Search } from 'lucide-react'
import { Button, Card, Spinner, Input } from '../ui'
import { ContainerLogsResponse } from '../../types'
import api from '../../api/client'
import { clsx } from 'clsx'

interface LogViewerProps {
    containerId: string
}

export default function LogViewer({ containerId }: LogViewerProps) {
    const [logs, setLogs] = useState<string>('')
    const [isLoading, setIsLoading] = useState(true)
    const [isPaused, setIsPaused] = useState(false)
    const [showTimestamps, setShowTimestamps] = useState(false)
    const [searchTerm, setSearchTerm] = useState('')
    const [tail, setTail] = useState('100')
    const logEndRef = useRef<HTMLDivElement>(null)
    const pollingInterval = useRef<NodeJS.Timeout | null>(null)

    const fetchLogs = async () => {
        try {
            const response = await api.get<ContainerLogsResponse>(`/containers/${containerId}/logs`, {
                params: {
                    tail,
                    timestamps: showTimestamps,
                },
            })
            setLogs(response.data.logs)
        } catch (error) {
            console.error('Failed to fetch logs:', error)
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        fetchLogs()

        if (!isPaused) {
            pollingInterval.current = setInterval(fetchLogs, 3000)
        }

        return () => {
            if (pollingInterval.current) {
                clearInterval(pollingInterval.current)
            }
        }
    }, [containerId, isPaused, tail, showTimestamps])

    useEffect(() => {
        if (!isPaused) {
            logEndRef.current?.scrollIntoView({ behavior: 'smooth' })
        }
    }, [logs])

    const handleDownload = () => {
        const blob = new Blob([logs], { type: 'text/plain' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `container-${containerId.slice(0, 8)}-logs.txt`
        a.click()
    }

    const handleClear = () => {
        setLogs('')
    }

    const highlightSearch = (text: string) => {
        if (!searchTerm) return text
        const parts = text.split(new RegExp(`(${searchTerm})`, 'gi'))
        return parts.map((part, i) =>
            part.toLowerCase() === searchTerm.toLowerCase()
                ? <mark key={i} className="bg-yellow-500/50 text-white rounded px-0.5">{part}</mark>
                : part
        )
    }

    return (
        <div className="flex flex-col h-[600px] space-y-4">
            <div className="flex items-center justify-between flex-wrap gap-4 bg-gray-50 dark:bg-gray-900/50 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                        <span className="text-xs font-medium text-gray-500 uppercase">Tail</span>
                        <select
                            value={tail}
                            onChange={(e) => setTail(e.target.value)}
                            className="bg-transparent text-sm border-none focus:ring-0 p-0 font-semibold text-primary-600 cursor-pointer"
                        >
                            <option value="50">50 lines</option>
                            <option value="100">100 lines</option>
                            <option value="500">500 lines</option>
                            <option value="1000">1000 lines</option>
                            <option value="all">All</option>
                        </select>
                    </div>
                    <div className="h-4 w-px bg-gray-300 dark:bg-gray-700" />
                    <button
                        onClick={() => setShowTimestamps(!showTimestamps)}
                        className={clsx(
                            "flex items-center space-x-1 text-xs font-medium transition-colors",
                            showTimestamps ? "text-primary-600" : "text-gray-500 hover:text-gray-700"
                        )}
                    >
                        <Clock className="h-3.5 w-3.5" />
                        <span>Timestamps</span>
                    </button>
                </div>

                <div className="flex items-center space-x-2 flex-1 max-w-sm">
                    <div className="relative flex-1">
                        <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-gray-400" />
                        <input
                            type="text"
                            placeholder="Filter logs..."
                            className="w-full pl-8 pr-3 py-1.5 text-xs bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 rounded-md focus:ring-primary-500 focus:border-primary-500 dark:text-gray-200"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                </div>

                <div className="flex items-center space-x-2">
                    <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => setIsPaused(!isPaused)}
                        className="h-8"
                    >
                        {isPaused ? <Play className="h-3.5 w-3.5 mr-1.5" /> : <Pause className="h-3.5 w-3.5 mr-1.5" />}
                        {isPaused ? 'Resume' : 'Pause'}
                    </Button>
                    <Button variant="secondary" size="sm" onClick={handleDownload} className="h-8">
                        <Download className="h-3.5 w-3.5 mr-1.5" />
                        Download
                    </Button>
                    <Button variant="ghost" size="sm" onClick={handleClear} className="h-8 text-gray-500 hover:text-red-600">
                        <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                </div>
            </div>

            <div className="flex-1 min-h-0 bg-gray-950 rounded-lg overflow-hidden border border-gray-800 flex flex-col relative group">
                {isLoading && (
                    <div className="absolute inset-0 flex items-center justify-center bg-gray-950/50 z-10">
                        <Spinner size="lg" />
                    </div>
                )}

                <div className="flex-1 overflow-auto p-4 font-mono text-sm leading-relaxed scrollbar-thin scrollbar-thumb-gray-800 scrollbar-track-transparent">
                    <pre className="text-gray-300 whitespace-pre-wrap break-all">
                        {logs ? (
                            highlightSearch(logs)
                        ) : (
                            <span className="text-gray-600 italic">No logs available for this container.</span>
                        )}
                    </pre>
                    <div ref={logEndRef} />
                </div>

                {!isPaused && (
                    <div className="absolute bottom-4 right-6 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity">
                        <div className="bg-primary-600 text-white text-[10px] px-2 py-0.5 rounded-full flex items-center space-x-1 animate-pulse">
                            <span className="h-1.5 w-1.5 bg-white rounded-full" />
                            <span>LIVE UPDATING</span>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
