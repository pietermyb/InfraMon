import { useMemo } from 'react'
import { Card, Badge, Spinner, Button } from '../ui'
import api from '../../api/client'
import { ContainerResponse } from '../../types'
import { Folder, FolderPlus, MoreHorizontal, ChevronRight, LayoutGrid, List } from 'lucide-react'
import { clsx } from 'clsx'

interface ContainerGroupsProps {
    containers: ContainerResponse[]
    selectedGroupName: string | null
    onSelectGroup: (groupName: string | null) => void
}

export default function ContainerGroups({ containers, selectedGroupName, onSelectGroup }: ContainerGroupsProps) {
    const groups = useMemo(() => {
        const map = new Map<string, { name: string, count: number, color: string }>();

        // Colors for detected groups
        const colors = [
            '#3B82F6', '#10B981', '#F59E0B', '#EF4444',
            '#8B5CF6', '#EC4899', '#06B6D4', '#6366F1'
        ];

        containers.forEach((container, idx) => {
            const name = container.name.replace(/^\//, '');
            // 1. Docker Compose Project Label (Standard)
            // 2. Fallback to prefix matching
            const labels = (container as any).labels || {};
            let groupName = labels['com.docker.compose.project'] ||
                labels['com.docker.stack.namespace'];

            if (!groupName) {
                const parts = name.split(/[-_]/);
                groupName = parts.length > 1 ? parts[0] : 'Independent';
            }

            if (!map.has(groupName)) {
                const colorIdx = map.size % colors.length;
                map.set(groupName, { name: groupName, count: 0, color: colors[colorIdx] });
            }
            map.get(groupName)!.count++;
        });

        return Array.from(map.values()).sort((a, b) => a.name.localeCompare(b.name));
    }, [containers]);

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
                        selectedGroupName === null
                            ? "bg-canvas-selected text-primary-700 dark:text-primary-400 border-l-4 border-primary-600 shadow-sm"
                            : "text-text-body hover:bg-canvas-hover dark:hover:bg-gray-800/50 hover:text-text-title border-l-4 border-transparent"
                    )}
                >
                    <div className="flex items-center">
                        All Projects
                    </div>
                    <Badge variant={selectedGroupName === null ? 'info' : 'default'} size="sm">
                        {containers.length}
                    </Badge>
                </button>

                {groups.map((group) => (
                    <button
                        key={group.name}
                        onClick={() => onSelectGroup(group.name)}
                        className={clsx(
                            "w-full flex items-center justify-between px-3 py-2 text-sm font-medium rounded-md transition-all group",
                            selectedGroupName === group.name
                                ? "bg-canvas-selected text-primary-700 dark:text-primary-400 border-l-4 border-primary-600 shadow-sm"
                                : "text-text-body hover:bg-canvas-hover dark:hover:bg-gray-800/50 hover:text-text-title border-l-4 border-transparent"
                        )}
                    >
                        <div className="flex items-center">
                            <Folder className={clsx(
                                "mr-3 h-4 w-4",
                                selectedGroupName === group.name ? "text-primary-500" : "text-gray-400 group-hover:text-gray-500"
                            )} style={{ color: selectedGroupName === group.name ? undefined : group.color }} />
                            {group.name}
                        </div>
                        <div className="flex items-center space-x-2">
                            <span className="text-[10px] text-gray-400 font-bold">{group.count}</span>
                            <ChevronRight className={clsx(
                                "h-3.5 w-3.5 transition-transform",
                                selectedGroupName === group.name ? "rotate-90 text-primary-500" : "text-gray-300 opacity-0 group-hover:opacity-100"
                            )} />
                        </div>
                    </button>
                ))}
            </nav>

            {groups.length === 0 && (
                <div className="px-3 py-4 text-center">
                    <Folder className="h-8 w-8 text-gray-300 mx-auto mb-2 opacity-50" />
                    <p className="text-[10px] text-gray-400 italic">No custom groups defined.</p>
                </div>
            )}
        </div>
    )
}
