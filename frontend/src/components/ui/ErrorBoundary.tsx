import { Component, ErrorInfo, ReactNode } from 'react'
import { Button } from './Button'
import { Card } from './Card'
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline'

interface Props {
    children?: ReactNode
    fallback?: ReactNode
}

interface State {
    hasError: boolean
    error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false
    }

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error }
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Uncaught error:', error, errorInfo)
    }

    public render() {
        if (this.state.hasError) {
            if (this.fallback) return this.fallback

            return (
                <div className="flex flex-col items-center justify-center min-h-[400px] p-6 text-center">
                    <Card className="max-w-md w-full border-red-100 dark:border-red-900/30">
                        <div className="flex justify-center mb-6">
                            <div className="p-4 rounded-full bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400">
                                <ExclamationTriangleIcon className="h-12 w-12" />
                            </div>
                        </div>
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Something went wrong</h2>
                        <p className="text-gray-500 dark:text-gray-400 mb-8">
                            An unexpected error occurred. You can try refreshing the page or contact support if the problem persists.
                        </p>
                        {this.state.error && (
                            <pre className="text-left text-xs bg-gray-50 dark:bg-gray-900 p-4 rounded-xl overflow-auto max-h-32 mb-8 border border-gray-100 dark:border-gray-800 text-gray-400">
                                {this.state.error.message}
                            </pre>
                        )}
                        <div className="flex gap-4 justify-center">
                            <Button
                                variant="secondary"
                                onClick={() => window.location.reload()}
                            >
                                Refresh Page
                            </Button>
                            <Button
                                onClick={() => this.setState({ hasError: false })}
                            >
                                Try Again
                            </Button>
                        </div>
                    </Card>
                </div>
            )
        }

        return this.children
    }

    private get children() {
        return this.props.children
    }

    private get fallback() {
        return this.props.fallback
    }
}
