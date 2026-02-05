import { useState } from 'react'
import { AlertCircle, Trash2 } from 'lucide-react'
import { Button, Modal } from '../ui'

interface RemoveContainerModalProps {
    isOpen: boolean
    onClose: () => void
    onConfirm: (force: boolean, removeVolumes: boolean) => void
    containerName: string
    isPending?: boolean
}

export default function RemoveContainerModal({
    isOpen,
    onClose,
    onConfirm,
    containerName,
    isPending,
}: RemoveContainerModalProps) {
    const [force, setForce] = useState(false)
    const [removeVolumes, setRemoveVolumes] = useState(false)
    const [confirmName, setConfirmName] = useState('')

    const handleConfirm = () => {
        if (confirmName === containerName.replace(/^\//, '')) {
            onConfirm(force, removeVolumes)
        }
    }

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Remove Container" size="md">
            <div className="space-y-6">
                <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-100 dark:border-red-900/30 flex items-start space-x-3">
                    <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
                    <div>
                        <h4 className="text-sm font-bold text-red-800 dark:text-red-400">Warning: Dangerous Action</h4>
                        <p className="text-xs text-red-700 dark:text-red-400/80 mt-1 leading-relaxed">
                            You are about to remove the container <strong>{containerName.replace(/^\//, '')}</strong>.
                            This will stop the container if it's running and delete its ephemeral storage.
                        </p>
                    </div>
                </div>

                <div className="space-y-4">
                    <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-900/50 rounded-md">
                        <input
                            type="checkbox"
                            id="force-remove"
                            checked={force}
                            onChange={(e) => setForce(e.target.checked)}
                            className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
                        />
                        <label htmlFor="force-remove" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                            Force remove (kill the container if it won't stop)
                        </label>
                    </div>

                    <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-900/50 rounded-md">
                        <input
                            type="checkbox"
                            id="remove-volumes"
                            checked={removeVolumes}
                            onChange={(e) => setRemoveVolumes(e.target.checked)}
                            className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
                        />
                        <label htmlFor="remove-volumes" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                            Remove volumes associated with the container
                        </label>
                    </div>
                </div>

                <div className="space-y-2">
                    <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                        Type container name to confirm: <span className="text-red-500 font-mono">{containerName.replace(/^\//, '')}</span>
                    </label>
                    <input
                        type="text"
                        className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-red-500 focus:border-red-500 sm:text-sm dark:bg-gray-700 dark:text-white"
                        value={confirmName}
                        onChange={(e) => setConfirmName(e.target.value)}
                        placeholder="Enter container name..."
                    />
                </div>

                <div className="flex items-center justify-end space-x-3 pt-2">
                    <Button variant="secondary" onClick={onClose}>Cancel</Button>
                    <Button
                        variant="danger"
                        onClick={handleConfirm}
                        isLoading={isPending}
                        disabled={confirmName !== containerName.replace(/^\//, '')}
                    >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Remove Forever
                    </Button>
                </div>
            </div>
        </Modal>
    )
}
