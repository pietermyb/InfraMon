import { ButtonHTMLAttributes, forwardRef } from 'react'
import { clsx } from 'clsx'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'link' | 'outline'
    size?: 'xs' | 'sm' | 'md' | 'lg'
    isLoading?: boolean
    leftIcon?: React.ReactNode
    rightIcon?: React.ReactNode
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
    ({
        className,
        variant = 'primary',
        size = 'md',
        isLoading,
        leftIcon,
        rightIcon,
        children,
        disabled,
        ...props
    }, ref) => {
        const baseStyles = 'inline-flex items-center justify-center font-medium rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]'

        const variants = {
            primary: 'bg-primary-600 text-white hover:bg-primary-700 hover:shadow-lg hover:shadow-primary-600/20 focus:ring-primary-500 border border-primary-600',
            secondary: 'bg-canvas-card text-text-body hover:bg-gray-50 dark:hover:bg-gray-800 border border-border-medium hover:border-gray-400 dark:hover:border-gray-500 focus:ring-gray-400',
            outline: 'bg-transparent text-primary-600 border border-primary-300 hover:bg-primary-50 hover:border-primary-400 dark:text-primary-400 dark:border-primary-800 dark:hover:bg-primary-900/20 dark:hover:border-primary-700 focus:ring-primary-500',
            danger: 'bg-red-600 text-white hover:bg-red-700 hover:shadow-lg hover:shadow-red-600/20 focus:ring-red-500 border border-red-600',
            ghost: 'bg-transparent text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800 focus:ring-gray-400',
            link: 'bg-transparent text-primary-600 hover:text-primary-500 underline-offset-4 hover:underline p-0 h-auto focus:ring-0',
        }

        const sizes = {
            xs: 'px-2.5 py-1.5 text-xs',
            sm: 'px-3.5 py-2 text-sm',
            md: 'px-5 py-2.5 text-sm',
            lg: 'px-6 py-3 text-base',
        }

        return (
            <button
                ref={ref}
                className={clsx(baseStyles, variants[variant], sizes[size], className)}
                disabled={disabled || isLoading}
                {...props}
            >
                {isLoading && (
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                )}
                {!isLoading && leftIcon && <span className="mr-2">{leftIcon}</span>}
                <span className="truncate">{children}</span>
                {!isLoading && rightIcon && <span className="ml-2">{rightIcon}</span>}
            </button>
        )
    }
)

Button.displayName = 'Button'
