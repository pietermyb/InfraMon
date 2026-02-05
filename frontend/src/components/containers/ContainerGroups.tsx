import { useQuery } from '@tanstack/react-query'
import { Card, Badge, Spinner, Button } from '../ui'
import api from '../../api/client'
import { ContainerGroupResponse } from '../../types'
import { Folder, FolderPlus, MoreHorizontal, ChevronRight, LayoutGrid, List } from 'lucide-react'
import { clsx } from 'clsx'

interface ContainerGroupsProps {
    selectedGroupId: number | null
    onSelectGroup: (groupId: number | null) => void
}

export default function ContainerGroups({ selectedGroupId, onSelectGroup }: ContainerGroupsProps) {
    const { data: groups, isLoading } = useQuery<ContainerGroupResponse[]>({
        queryKey: ['container-groups'],
        queryFn: async () => {
            const response = await api.get('/containers/groups')
            return response.data
        }
    })

    if (isLoading) {
        return <div className="flex justify-center p-4"><Spinner size="sm" /></div>
    }

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between px-2">
                <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest">Groups</h3>
                <Button variant="ghost" size="sm" className="h-6 w-6 p-0 rounded-full">
                    <FolderPlus className="h-3.5 w-3.5" />
                </Button>
            </div>

            <nav className="space-y-1">
                <button
                    onClick={() => onSelectGroup(null)}
                    className={clsx(
                        "w-full flex items-center justify-between px-3 py-2 text-sm font-medium rounded-md transition-all group",
                        selectedGroupId === null
                            ? "bg-primary-50 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400 border-l-4 border-primary-600"
                            : "text-gray-600 hover:bg-gray-50 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-800/50 dark:hover:text-gray-200 border-l-4 border-transparent"
                    )}
                >
                    <div className="flex items-center">
                        <LayoutGrid className={clsx(
                            "mr-3 h-4 w-4",
                            selectedGroupId === null ? "text-primary-500" : "text-gray-400 group-hover:text-gray-500"
                        )} />
                        All Containers
                    </div>
                    <Badge variant={selectedGroupId === null ? 'info' : 'default'} size="sm">
                        ALL
                    </Badge>
                </button>

                {groups?.map((group) => (
                    <button
                        key={group.id}
                        onClick={() => onSelectGroup(group.id)}
                        className={clsx(
                            "w-full flex items-center justify-between px-3 py-2 text-sm font-medium rounded-md transition-all group",
                            selectedGroupId === group.id
                                ? "bg-primary-50 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400 border-l-4 border-primary-600"
                                : "text-gray-600 hover:bg-gray-50 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-800/50 dark:hover:text-gray-200 border-l-4 border-transparent"
                        )}
                    >
                        <div className="flex items-center">
                            <Folder className={clsx(
                                "mr-3 h-4 w-4",
                                selectedGroupId === group.id ? "text-primary-500" : "text-gray-400 group-hover:text-gray-500"
                            )} style={{ color: selectedGroupId === group.id ? undefined : group.color }} />
                            {group.name}
                        </div>
                        <ChevronRight className={clsx(
                            "h-3.5 w-3.5 transition-transform",
                            selectedGroupId === group.id ? "rotate-90 text-primary-500" : "text-gray-300 opacity-0 group-hover:opacity-100"
                        )} />
                    </button>
                ))}
            </nav>

            {(!groups || groups.length === 0) && !isLoading && (
                <div className="px-3 py-4 text-center">
                    <Folder className="h-8 w-8 text-gray-300 mx-auto mb-2 opacity-50" />
                    <p className="text-[10px] text-gray-400 italic">No custom groups defined.</p>
                </div>
            )}
        </div>
    )
}
