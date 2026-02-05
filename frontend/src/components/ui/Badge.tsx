import { clsx } from 'clsx'

export interface BadgeProps {
    children: React.ReactNode
    variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'primary'
    size?: 'sm' | 'md' | 'lg'
    className?: string
}

export function Badge({ children, variant = 'default', size = 'md', className }: BadgeProps) {
    const variants = {
        default: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300 border-gray-200 dark:border-gray-700',
        primary: 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400 border-primary-100 dark:border-primary-800/50',
        success: 'bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-400 border-green-100 dark:border-green-800/50',
        warning: 'bg-yellow-50 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400 border-yellow-100 dark:border-yellow-800/50',
        danger: 'bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400 border-red-100 dark:border-red-800/50',
        info: 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 border-blue-100 dark:border-blue-800/50',
    }

    const sizes = {
        sm: 'px-2 py-0.5 text-xs',
        md: 'px-2.5 py-0.5 text-sm',
        lg: 'px-3 py-1 text-base',
    }

    return (
        <span className={clsx(
            'inline-flex items-center font-semibold rounded-full border',
            variants[variant],
            sizes[size],
            className
        )}>
            {children}
        </span>
    )
}
