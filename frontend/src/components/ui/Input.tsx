import { forwardRef, InputHTMLAttributes } from 'react'
import { clsx } from 'clsx'

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
    label?: string
    error?: string
    helperText?: string
    leftIcon?: React.ReactNode
    rightIcon?: React.ReactNode
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
    ({ className, label, error, helperText, leftIcon, rightIcon, id, ...props }, ref) => {
        return (
            <div className="space-y-1.5 min-w-0 w-full">
                {label && (
                    <label
                        htmlFor={id}
                        className="block text-sm font-medium text-gray-700 dark:text-gray-300 ml-1"
                    >
                        {label}
                    </label>
                )}
                <div className="relative group">
                    {leftIcon && (
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400 group-focus-within:text-primary-500 transition-colors">
                            {leftIcon}
                        </div>
                    )}
                    <input
                        id={id}
                        ref={ref}
                        className={clsx(
                            'block w-full rounded-xl transition-all duration-200 sm:text-sm',
                            'bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700',
                            'text-gray-900 dark:text-white placeholder:text-gray-400',
                            'focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 focus:bg-white dark:focus:bg-gray-800',
                            error ? 'border-red-500 focus:ring-red-500/20 focus:border-red-500' : 'hover:border-gray-300 dark:hover:border-gray-600',
                            leftIcon && 'pl-10',
                            rightIcon && 'pr-10',
                            className
                        )}
                        {...props}
                    />
                    {rightIcon && (
                        <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-gray-400">
                            {rightIcon}
                        </div>
                    )}
                </div>
                {error && <p className="text-xs text-red-500 mt-1 ml-1">{error}</p>}
                {helperText && !error && <p className="text-xs text-gray-500 mt-1 ml-1">{helperText}</p>}
            </div>
        )
    }
)

Input.displayName = 'Input'
