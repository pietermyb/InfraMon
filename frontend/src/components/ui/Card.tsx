import { clsx } from 'clsx'

export interface CardProps {
    children: React.ReactNode
    className?: string
    padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl'
    hover?: boolean
}

export function Card({ children, className, padding = 'md', hover = false }: CardProps) {
    const paddings = {
        none: '',
        sm: 'p-4',
        md: 'p-6',
        lg: 'p-8',
        xl: 'p-10',
    }

    return (
        <div
            className={clsx(
                'bg-canvas-card rounded-2xl border border-border-subtle shadow-sm transition-all duration-300',
                hover && 'hover:shadow-xl hover:shadow-gray-200/50 dark:hover:shadow-black/50 hover:border-primary-100 dark:hover:border-primary-900/50 hover:-translate-y-1',
                paddings[padding],
                className
            )}
        >
            {children}
        </div>
    )
}
