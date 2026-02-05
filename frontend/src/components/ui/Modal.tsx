import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { clsx } from 'clsx'
import { XMarkIcon } from '@heroicons/react/24/outline'

export interface ModalProps {
    isOpen: boolean
    onClose: () => void
    title?: string | React.ReactNode
    children: React.ReactNode
    size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full'
    showClose?: boolean
}

export function Modal({
    isOpen,
    onClose,
    title,
    children,
    size = 'md',
    showClose = true
}: ModalProps) {
    const [isMounted, setIsMounted] = useState(false)

    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden'
            setIsMounted(true)
        } else {
            const timer = setTimeout(() => {
                setIsMounted(false)
                document.body.style.overflow = 'unset'
            }, 300)
            return () => clearTimeout(timer)
        }
    }, [isOpen])

    if (!isMounted && !isOpen) return null

    const sizes = {
        sm: 'max-w-sm',
        md: 'max-w-lg',
        lg: 'max-w-2xl',
        xl: 'max-w-4xl',
        '2xl': 'max-w-6xl',
        'full': 'max-w-[95vw]',
    }

    return createPortal(
        <div className={clsx(
            'fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 transition-opacity duration-300',
            isOpen ? 'opacity-100' : 'opacity-0'
        )}>
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-gray-900/60 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal Content */}
            <div className={clsx(
                'relative w-full bg-white dark:bg-gray-800 rounded-3xl shadow-2xl overflow-hidden transform transition-all duration-300 ease-out',
                isOpen ? 'scale-100 translate-y-0' : 'scale-95 translate-y-4',
                sizes[size]
            )}>
                {title && (
                    <div className="px-6 py-5 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
                        <h3 className="text-xl font-bold text-gray-900 dark:text-white leading-none">
                            {title}
                        </h3>
                        {showClose && (
                            <button
                                onClick={onClose}
                                className="p-2 rounded-xl text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                                title="Close"
                            >
                                <XMarkIcon className="h-6 w-6" />
                            </button>
                        )}
                    </div>
                )}

                {!title && showClose && (
                    <button
                        onClick={onClose}
                        className="absolute top-4 right-4 z-10 p-2 rounded-xl text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        title="Close"
                    >
                        <XMarkIcon className="h-6 w-6" />
                    </button>
                )}

                <div className="px-6 py-6 overflow-y-auto max-h-[85vh] scrollbar-thin">
                    {children}
                </div>
            </div>
        </div>,
        document.body
    )
}
