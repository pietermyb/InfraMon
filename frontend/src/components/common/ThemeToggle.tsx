import { SunIcon, MoonIcon } from '@heroicons/react/24/outline'
import { useTheme } from '../../hooks/useTheme'
import { clsx } from 'clsx'

interface ThemeToggleProps {
    className?: string
}

export function ThemeToggle({ className }: ThemeToggleProps) {
    const { theme, toggleTheme } = useTheme()

    return (
        <button
            onClick={toggleTheme}
            className={clsx(
                'p-2 rounded-xl transition-all duration-300',
                'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700',
                'text-gray-500 hover:text-primary-600 dark:text-gray-400 dark:hover:text-primary-400',
                'hover:shadow-md hover:border-primary-200 dark:hover:border-primary-800',
                'active:scale-95',
                className
            )}
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        >
            <div className="relative w-6 h-6">
                <SunIcon
                    className={clsx(
                        'absolute inset-0 w-6 h-6 transition-all duration-500 transform',
                        theme === 'light' ? 'rotate-0 scale-100 opacity-100' : 'rotate-90 scale-0 opacity-0'
                    )}
                />
                <MoonIcon
                    className={clsx(
                        'absolute inset-0 w-6 h-6 transition-all duration-500 transform',
                        theme === 'dark' ? 'rotate-0 scale-100 opacity-100' : '-rotate-90 scale-0 opacity-0'
                    )}
                />
            </div>
        </button>
    )
}
