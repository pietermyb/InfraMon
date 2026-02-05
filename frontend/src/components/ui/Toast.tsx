import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { clsx } from 'clsx'
import {
    CheckCircleIcon,
    ExclamationCircleIcon,
    InformationCircleIcon,
    XCircleIcon,
    XMarkIcon
} from '@heroicons/react/24/outline'
import { useToastStore, Toast as ToastType } from '../../store/useToastStore'

export function ToastContainer() {
    const { toasts, removeToast } = useToastStore()

    return createPortal(
        <div className="fixed bottom-0 right-0 p-6 z-[100] space-y-4 pointer-events-none">
            {toasts.map((toast) => (
                <ToastItem key={toast.id} toast={toast} onRemove={() => removeToast(toast.id)} />
            ))}
        </div>,
        document.body
    )
}

function ToastItem({ toast, onRemove }: { toast: ToastType; onRemove: () => void }) {
    const [isVisible, setIsVisible] = useState(false)

    useEffect(() => {
        setIsVisible(true)
    }, [])

    const icons = {
        success: <CheckCircleIcon className="h-6 w-6 text-green-500" />,
        error: <XCircleIcon className="h-6 w-6 text-red-500" />,
        warning: <ExclamationCircleIcon className="h-6 w-6 text-yellow-500" />,
        info: <InformationCircleIcon className="h-6 w-6 text-blue-500" />,
    }

    const variants = {
        success: 'border-green-100 bg-green-50 dark:bg-green-900/20 dark:border-green-900/50',
        error: 'border-red-100 bg-red-50 dark:bg-red-900/20 dark:border-red-900/50',
        warning: 'border-yellow-100 bg-yellow-50 dark:bg-yellow-900/20 dark:border-yellow-900/50',
        info: 'border-blue-100 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-900/50',
    }

    return (
        <div className={clsx(
            'pointer-events-auto flex items-center w-full max-w-sm p-4 rounded-2xl shadow-2xl border transition-all duration-300 transform',
            isVisible ? 'translate-x-0 opacity-100' : 'translate-x-12 opacity-0',
            variants[toast.type]
        )}>
            <div className="flex-shrink-0">
                {icons[toast.type]}
            </div>
            <div className="ml-3 text-sm font-medium text-gray-900 dark:text-white flex-1">
                {toast.message}
            </div>
            <button
                onClick={() => {
                    setIsVisible(false)
                    setTimeout(onRemove, 300)
                }}
                className="ml-4 flex-shrink-0 text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 transition-colors"
            >
                <XMarkIcon className="h-5 w-5" />
            </button>
        </div>
    )
}
