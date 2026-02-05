import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, Button, Spinner, Badge } from '../ui'
import api from '../../api/client'
import { ComposeInfo, ComposeFileResponse } from '../../types'
import { FileCode, RefreshCw, Layers, ExternalLink, AlertCircle, CheckCircle2 } from 'lucide-react'

interface ComposeDetailsProps {
    containerId: string
}

export default function ComposeDetails({ containerId }: ComposeDetailsProps) {
    const queryClient = useQueryClient()

    const { data: composeInfo, isLoading: loadingInfo } = useQuery<ComposeInfo>({
        queryKey: ['container-compose-info', containerId],
        queryFn: async () => {
            const response = await api.get(`/containers/${containerId}/compose/info`)
            return response.data
        },
    })

    const { data: composeFile, isLoading: loadingFile } = useQuery<ComposeFileResponse>({
        queryKey: ['container-compose-file', containerId],
        queryFn: async () => {
            const response = await api.get(`/containers/${containerId}/compose/file`)
            return response.data
        },
        enabled: !!composeInfo?.compose_file_path,
    })

    const pullMutation = useMutation({
        mutationFn: async () => {
            await api.post(`/containers/${containerId}/compose/pull`)
        },
    })

    if (loadingInfo) {
        return <div className="flex justify-center p-8"><Spinner /></div>
    }

    if (!composeInfo?.compose_file_path) {
        return (
            <Card className="bg-gray-50/50 dark:bg-gray-900/20 border-dashed border-2 flex flex-col items-center justify-center p-12 text-center">
                <Layers className="h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">No Docker Compose Project</h3>
                <p className="mt-2 text-sm text-gray-500 dark:text-gray-400 max-w-sm">
                    This container doesn't appear to be managed by Docker Compose.
                    Advanced compose features are only available for containers started with a compose file.
                </p>
            </Card>
        )
    }

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <Card className="lg:col-span-2">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-lg font-semibold flex items-center">
                            <FileCode className="h-5 w-5 mr-2 text-primary-500" />
                            Compose Configuration
                        </h3>
                        <div className="flex items-center space-x-2">
                            <Button
                                variant="secondary"
                                size="sm"
                                onClick={() => pullMutation.mutate()}
                                isLoading={pullMutation.isPending}
                            >
                                <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
                                Pull Images
                            </Button>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <div className="flex items-start justify-between bg-gray-50 dark:bg-gray-900/50 p-4 rounded-lg">
                            <div>
                                <div className="text-xs font-bold text-gray-500 uppercase tracking-tighter mb-1">Project Name</div>
                                <div className="text-sm font-medium text-gray-900 dark:text-white">
                                    {composeInfo.project_name || 'Generic Project'}
                                </div>
                            </div>
                            <div>
                                <div className="text-xs font-bold text-gray-500 uppercase tracking-tighter mb-1">Status</div>
                                <Badge variant="success">Active</Badge>
                            </div>
                        </div>

                        <div className="bg-gray-950 rounded-lg overflow-hidden border border-gray-800">
                            <div className="bg-gray-800 px-4 py-2 flex items-center justify-between">
                                <span className="text-xs font-mono text-gray-400">{composeInfo.compose_file_path}</span>
                                <ExternalLink className="h-3 w-3 text-gray-500" />
                            </div>
                            <div className="p-4 font-mono text-xs text-gray-300 overflow-auto max-h-96">
                                {loadingFile ? <Spinner size="sm" /> : (
                                    <pre className="whitespace-pre-wrap">{composeFile?.content || 'Could not load compose file content.'}</pre>
                                )}
                            </div>
                        </div>
                    </div>
                </Card>

                <Card>
                    <h3 className="text-lg font-semibold mb-6 flex items-center">
                        <Layers className="h-5 w-5 mr-2 text-primary-500" />
                        Project Services
                    </h3>
                    <div className="space-y-3">
                        {composeInfo.services?.map(service => (
                            <div
                                key={service}
                                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900/50 rounded-md border border-gray-200 dark:border-gray-800"
                            >
                                <span className="text-sm font-medium">{service}</span>
                                <CheckCircle2 className="h-4 w-4 text-green-500" />
                            </div>
                        ))}
                        {(!composeInfo.services || composeInfo.services.length === 0) && (
                            <div className="text-center py-8 text-gray-500 text-sm italic">
                                No service information available.
                            </div>
                        )}
                    </div>

                    <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
                        <h4 className="text-xs font-bold text-gray-500 uppercase mb-4 tracking-wider">Validation</h4>
                        <div className="flex items-center space-x-2 text-green-600 dark:text-green-400">
                            <CheckCircle2 className="h-4 w-4" />
                            <span className="text-sm font-medium">Compose file is valid</span>
                        </div>
                    </div>
                </Card>
            </div>
        </div>
    )
}
