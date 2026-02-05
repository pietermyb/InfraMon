import { clsx } from 'clsx'
import { Button } from '../ui'
import {
  ArrowPathIcon,
  CogIcon,
  BellIcon,
  QuestionMarkCircleIcon,
} from '@heroicons/react/24/outline'

interface QuickActionsToolbarProps {
  onRefresh?: () => void
  onSettings?: () => void
  onNotifications?: () => void
  showRefresh?: boolean
  showSettings?: boolean
  showNotifications?: boolean
  isRefreshing?: boolean
}

export function QuickActionsToolbar({
  onRefresh,
  onSettings,
  onNotifications,
  showRefresh = true,
  showSettings = true,
  showNotifications = true,
  isRefreshing = false,
}: QuickActionsToolbarProps) {
  return (
    <div className="flex items-center gap-2">
      {showRefresh && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onRefresh}
          disabled={isRefreshing}
          className={clsx(isRefreshing && 'animate-spin')}
        >
          <ArrowPathIcon className="h-4 w-4" />
        </Button>
      )}
      {showNotifications && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onNotifications}
        >
          <BellIcon className="h-4 w-4" />
        </Button>
      )}
      {showSettings && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onSettings}
        >
          <CogIcon className="h-4 w-4" />
        </Button>
      )}
      <div className="h-6 w-px bg-gray-200 dark:bg-gray-700 mx-2" />
      <Button variant="ghost" size="sm">
        <QuestionMarkCircleIcon className="h-4 w-4" />
      </Button>
    </div>
  )
}
