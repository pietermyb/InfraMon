import { useState, useRef, useEffect } from 'react'
import { clsx } from 'clsx'

export interface DropdownItem {
    label: string
    onClick?: () => void
    icon?: React.ReactNode
    variant?: 'default' | 'danger'
    disabled?: boolean
}

export interface DropdownProps {
    trigger: React.ReactNode
    items: DropdownItem[]
    align?: 'left' | 'right'
    className?: string
}

export function Dropdown({ trigger, items, align = 'right', className }: DropdownProps) {
    const [isOpen, setIsOpen] = useState(false)
    const dropdownRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false)
            }
        }
        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    return (
        <div className={clsx('relative inline-block text-left', className)} ref={dropdownRef}>
            <div onClick={() => setIsOpen(!isOpen)} className="cursor-pointer">
                {trigger}
            </div>

            {isOpen && (
                <div className={clsx(
                    'absolute z-50 mt-2 w-56 origin-top-right rounded-2xl bg-white dark:bg-gray-800 shadow-2xl ring-1 ring-black ring-opacity-5 focus:outline-none overflow-hidden animate-scale-in',
                    align === 'right' ? 'right-0' : 'left-0'
                )}>
                    <div className="py-1">
                        {items.map((item, index) => (
                            <button
                                key={index}
                                onClick={() => {
                                    item.onClick?.()
                                    setIsOpen(false)
                                }}
                                disabled={item.disabled}
                                className={clsx(
                                    'flex items-center w-full px-4 py-2.5 text-sm transition-colors',
                                    item.variant === 'danger'
                                        ? 'text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20'
                                        : 'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700',
                                    item.disabled && 'opacity-50 cursor-not-allowed'
                                )}
                            >
                                {item.icon && <span className="mr-3 h-5 w-5 text-gray-400 group-hover:text-gray-500">{item.icon}</span>}
                                {item.label}
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}
