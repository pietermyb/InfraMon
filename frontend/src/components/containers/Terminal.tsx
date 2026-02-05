import { useEffect, useRef, useState } from 'react'
import { Terminal as XTerm } from 'xterm'
import { FitAddon } from 'xterm-addon-fit'
import 'xterm/css/xterm.css'
import { Button, Card, Spinner } from '../ui'
import { Maximize2, Minimize2, Power, RefreshCw, Terminal as TerminalIcon } from 'lucide-react'
import { clsx } from 'clsx'

interface TerminalProps {
    containerId: string
}

export default function Terminal({ containerId }: TerminalProps) {
    const terminalRef = useRef<HTMLDivElement>(null)
    const xtermRef = useRef<XTerm | null>(null)
    const fitAddonRef = useRef<FitAddon | null>(null)
    const socketRef = useRef<WebSocket | null>(null)
    const [isConnected, setIsConnected] = useState(false)
    const [isConnecting, setIsConnecting] = useState(false)
    const [isFullscreen, setIsFullscreen] = useState(false)

    const connect = () => {
        if (isConnecting || isConnected) return

        setIsConnecting(true)
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const host = window.location.host === 'localhost:5173' ? 'localhost:8000' : window.location.host
        const wsUrl = `${protocol}//${host}/api/v1/containers/${containerId}/shell`

        const socket = new WebSocket(wsUrl)
        socketRef.current = socket

        socket.onopen = () => {
            setIsConnected(true)
            setIsConnecting(false)
            xtermRef.current?.focus()
            xtermRef.current?.writeln('\x1b[1;32mconnected to container shell\x1b[0m')
        }

        socket.onmessage = (event) => {
            xtermRef.current?.write(event.data)
        }

        socket.onclose = () => {
            setIsConnected(false)
            setIsConnecting(false)
            xtermRef.current?.writeln('\x1b[1;31mdisconnected from container shell\x1b[0m')
        }

        socket.onerror = () => {
            setIsConnecting(false)
            xtermRef.current?.writeln('\x1b[1;31mconnection error\x1b[0m')
        }
    }

    const disconnect = () => {
        socketRef.current?.close()
        setIsConnected(false)
    }

    useEffect(() => {
        if (!terminalRef.current) return

        const xterm = new XTerm({
            cursorBlink: true,
            fontSize: 14,
            fontFamily: 'Menlo, Monaco, "Courier New", monospace',
            theme: {
                background: '#0a0a0a',
                foreground: '#d4d4d4',
                cursor: '#f8f8f2',
                selectionBackground: '#44475a',
            },
            allowProposedApi: true,
        })

        const fitAddon = new FitAddon()
        xterm.loadAddon(fitAddon)
        xterm.open(terminalRef.current)
        fitAddon.fit()

        xterm.onData((data) => {
            if (socketRef.current?.readyState === WebSocket.OPEN) {
                socketRef.current.send(data)
            }
        })

        xtermRef.current = xterm
        fitAddonRef.current = fitAddon

        const handleResize = () => {
            fitAddon.fit()
        }
        window.addEventListener('resize', handleResize)

        return () => {
            window.removeEventListener('resize', handleResize)
            xterm.dispose()
            socketRef.current?.close()
        }
    }, [])

    useEffect(() => {
        if (isFullscreen) {
            setTimeout(() => fitAddonRef.current?.fit(), 100)
        } else {
            setTimeout(() => fitAddonRef.current?.fit(), 100)
        }
    }, [isFullscreen])

    return (
        <div className={clsx(
            "flex flex-col transition-all duration-300 overflow-hidden",
            isFullscreen ? "fixed inset-0 z-50 bg-canvas-base" : "h-[600px] bg-canvas-card border border-border-subtle rounded-2xl shadow-premium"
        )}>
            <div className="flex items-center justify-between bg-canvas-card px-4 py-3 border-b border-border-subtle">
                <div className="flex items-center space-x-3">
                    <TerminalIcon className="h-4 w-4 text-text-body" />
                    <h3 className="text-sm font-bold text-text-title">Terminal — {containerId?.slice(0, 12)}</h3>
                    <div className="flex items-center space-x-2 px-2.5 py-1 bg-canvas-base rounded-full border border-border-subtle">
                        <div className={clsx(
                            "h-2 w-2 rounded-full shadow-[0_0_8px_rgba(0,0,0,0.1)]",
                            isConnected ? "bg-green-500 animate-pulse" : isConnecting ? "bg-yellow-500 animate-bounce" : "bg-red-500"
                        )} />
                        <span className="text-[10px] font-bold text-text-body uppercase tracking-widest">
                            {isConnected ? 'Connected' : isConnecting ? 'Connecting' : 'Disconnected'}
                        </span>
                    </div>
                </div>
                <div className="flex items-center space-x-2">
                    {!isConnected && !isConnecting ? (
                        <Button
                            size="sm"
                            variant="primary"
                            onClick={connect}
                            leftIcon={<Power className="h-3.5 w-3.5" />}
                        >
                            Connect
                        </Button>
                    ) : (
                        <Button
                            size="sm"
                            variant="danger"
                            onClick={disconnect}
                            leftIcon={<Power className="h-3.5 w-3.5" />}
                        >
                            Disconnect
                        </Button>
                    )}
                    <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => setIsFullscreen(!isFullscreen)}
                        className="w-9 px-0"
                    >
                        {isFullscreen ? <Minimize2 className="h-3.5 w-3.5" /> : <Maximize2 className="h-3.5 w-3.5" />}
                    </Button>
                </div>
            </div>

            <div
                ref={terminalRef}
                className="flex-1 min-h-0 bg-[#0a0a0a] overflow-hidden"
            />

            {!isConnected && !isConnecting && (
                <div className="absolute inset-x-0 bottom-6 flex justify-center pointer-events-none">
                    <div className="bg-canvas-card/90 backdrop-blur-md border border-border-subtle px-5 py-2.5 rounded-full text-xs text-text-body shadow-premium pointer-events-auto flex items-center gap-2">
                        <TerminalIcon className="h-3.5 w-3.5 text-text-body/60" />
                        <span>Terminal disconnected.</span>
                        <Button variant="link" size="sm" onClick={connect} className="h-auto font-bold text-primary-600 px-0">
                            Click here to connect
                        </Button>
                    </div>
                </div>
            )}
        </div>
    )
}
