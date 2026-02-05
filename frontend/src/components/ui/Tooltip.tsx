import { clsx } from 'clsx'
import { useState } from 'react'

export interface TooltipProps {
    content: string | React.ReactNode
    children: React.ReactNode
    position?: 'top' | 'bottom' | 'left' | 'right'
    delay?: number
}

export function Tooltip({ content, children, position = 'top', delay = 0 }: TooltipProps) {
    const [isVisible, setIsVisible] = useState(false)
    const [timer, setTimer] = useState<NodeJS.Timeout | null>(null)

    const handleMouseEnter = () => {
        const t = setTimeout(() => setIsVisible(true), delay)
        setTimer(t)
    }

    const handleMouseLeave = () => {
        if (timer) clearTimeout(timer)
        setIsVisible(false)
    }

    const positions = {
        top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
        bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
        left: 'right-full top-1/2 -translate-y-1/2 mr-2',
        right: 'left-full top-1/2 -translate-y-1/2 ml-2',
    }

    const arrows = {
        top: 'top-full left-1/2 -translate-x-1/2 border-t-gray-900 dark:border-t-gray-700',
        bottom: 'bottom-full left-1/2 -translate-x-1/2 border-b-gray-900 dark:border-b-gray-700',
        left: 'left-full top-1/2 -translate-y-1/2 border-l-gray-900 dark:border-l-gray-700',
        right: 'right-full top-1/2 -translate-y-1/2 border-r-gray-900 dark:border-r-gray-700',
    }

    return (
        <div
            className="relative inline-block"
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
        >
            {children}
            {isVisible && (
                <div className={clsx(
                    'absolute z-[60] px-3 py-2 text-xs font-medium text-white bg-gray-900 dark:bg-gray-700 rounded-lg shadow-xl whitespace-nowrap animate-fade-in',
                    positions[position]
                )}>
                    {content}
                    <div className={clsx(
                        'absolute border-4 border-transparent',
                        arrows[position]
                    )} />
                </div>
            )}
        </div>
    )
}
