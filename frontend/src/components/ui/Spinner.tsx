import { clsx } from 'clsx'

export interface SpinnerProps {
    size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
    className?: string
    color?: 'primary' | 'current' | 'white'
}

export function Spinner({ size = 'md', className, color = 'primary' }: SpinnerProps) {
    const sizes = {
        xs: 'h-3 w-3',
        sm: 'h-5 w-5',
        md: 'h-8 w-8',
        lg: 'h-12 w-12',
        xl: 'h-16 w-16',
    }

    const colors = {
        primary: 'text-primary-600',
        current: 'text-current',
        white: 'text-white',
    }

    return (
        <div className={clsx('relative', sizes[size], className)}>
            <svg
                className={clsx('animate-spin', colors[color], 'w-full h-full')}
                fill="none"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
            >
                <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="3"
                />
                <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
            </svg>
        </div>
    )
}

export interface SkeletonProps {
    className?: string
    variant?: 'text' | 'circular' | 'rectangular'
    width?: string | number
    height?: string | number
}

export function Skeleton({ className, variant = 'rectangular', width, height }: SkeletonProps) {
    return (
        <div
            className={clsx(
                'animate-pulse bg-gray-200 dark:bg-gray-800',
                variant === 'circular' ? 'rounded-full' : 'rounded-lg',
                className
            )}
            style={{
                width: typeof width === 'number' ? `${width}px` : width,
                height: typeof height === 'number' ? `${height}px` : height,
            }}
        />
    )
}
