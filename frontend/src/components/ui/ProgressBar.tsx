import { clsx } from 'clsx'

export interface ProgressBarProps {
    value: number
    max?: number
    label?: string
    showPercentage?: boolean
    color?: 'primary' | 'success' | 'warning' | 'danger'
    size?: 'xs' | 'sm' | 'md' | 'lg'
    className?: string
}

export function ProgressBar({
    value,
    max = 100,
    label,
    showPercentage = false,
    color = 'primary',
    size = 'md',
    className
}: ProgressBarProps) {
    const percentage = Math.min(100, Math.max(0, (value / max) * 100))

    const colors = {
        primary: 'bg-primary-600 shadow-[0_0_10px_rgba(59,130,246,0.5)]',
        success: 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]',
        warning: 'bg-yellow-500 shadow-[0_0_10px_rgba(234,179,8,0.5)]',
        danger: 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]',
    }

    const sizes = {
        xs: 'h-1',
        sm: 'h-1.5',
        md: 'h-2.5',
        lg: 'h-4',
    }

    return (
        <div className={clsx('space-y-2 w-full', className)}>
            {(label || showPercentage) && (
                <div className="flex justify-between items-center text-xs font-semibold uppercase tracking-wider">
                    {label && <span className="text-gray-500 dark:text-gray-400">{label}</span>}
                    {showPercentage && <span className="text-gray-700 dark:text-gray-300">{percentage.toFixed(0)}%</span>}
                </div>
            )}
            <div className={clsx('w-full bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden border border-gray-200/50 dark:border-gray-700/50', sizes[size])}>
                <div
                    className={clsx(
                        colors[color],
                        'h-full rounded-full transition-all duration-500 ease-out'
                    )}
                    style={{ width: `${percentage}%` }}
                />
            </div>
        </div>
    )
}
