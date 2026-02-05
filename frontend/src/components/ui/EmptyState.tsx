import { clsx } from 'clsx'
import { Card } from './Card'

export interface EmptyStateProps {
    icon?: React.ReactNode
    title: string
    description?: string
    action?: React.ReactNode
    className?: string
}

export function EmptyState({ icon, title, description, action, className }: EmptyStateProps) {
    return (
        <Card className={clsx('flex flex-col items-center justify-center py-16 text-center shadow-none border-dashed border-2', className)}>
            {icon && (
                <div className="mb-6 p-4 rounded-full bg-gray-50 dark:bg-gray-900 text-gray-400">
                    {icon}
                </div>
            )}
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">{title}</h3>
            {description && (
                <p className="max-w-xs mx-auto text-gray-500 dark:text-gray-400 mb-8">
                    {description}
                </p>
            )}
            {action && <div>{action}</div>}
        </Card>
    )
}
