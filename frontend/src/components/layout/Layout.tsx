import { useState } from 'react'
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { ThemeToggle } from '../common/ThemeToggle'
import { useTheme } from '../../hooks/useTheme'
import { Button, Modal } from '../../components/ui'
import { Breadcrumbs } from './Breadcrumbs'
import { QuickActionsToolbar } from './QuickActionsToolbar'
import {
  HomeIcon,
  CubeIcon,
  Cog6ToothIcon,
  ArrowLeftOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  UserCircleIcon,
} from '@heroicons/react/24/outline'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Containers', href: '/containers', icon: CubeIcon },
  { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
]

export default function Layout() {
  const { user, logout, sessionTimeRemaining } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [showLogoutModal, setShowLogoutModal] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)

  const formatSessionTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const handleLogout = () => {
    logout()
    setShowLogoutModal(false)
  }

  const handleRefresh = () => {
    setIsRefreshing(true)
    setTimeout(() => setIsRefreshing(false), 1000)
  }

  const currentPageName = location.pathname.split('/').pop() || 'Dashboard'

  return (
    <div className="min-h-screen bg-canvas-base font-sans text-text-body transition-colors duration-300">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:z-[100] focus:px-4 focus:py-2 focus:bg-primary-600 focus:text-white focus:rounded-b-lg focus:left-1/2 focus:-translate-x-1/2"
      >
        Skip to main content
      </a>

      <div className="hidden md:fixed md:inset-y-0 md:flex md:w-64 md:flex-col" role="navigation" aria-label="Sidebar Navigation">
        <div className="flex flex-col flex-grow bg-canvas-sidebar border-r border-border-subtle shadow-sm">
          <div className="flex items-center h-16 px-6 border-b border-border-subtle">
            <CubeIcon className="h-8 w-8 text-primary-600" aria-hidden="true" />
            <span className="ml-2 text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-600 to-primary-400">InfraMon</span>
          </div>

          <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href ||
                (item.href !== '/dashboard' && location.pathname.startsWith(item.href))
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={`flex items-center px-3 py-2.5 text-sm font-semibold rounded-xl transition-all duration-200 ${isActive
                    ? 'bg-primary-50 dark:bg-primary-900/40 text-primary-600 dark:text-primary-400 shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-200'
                    }`}
                >
                  <item.icon className={`h-5 w-5 mr-3 transition-colors ${isActive ? 'text-primary-600' : 'text-gray-400 group-hover:text-gray-500'}`} />
                  {item.name}
                </NavLink>
              )
            })}
          </nav>

          <div className="p-4 border-t border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/50">
            <div className="flex items-center gap-3 mb-4 p-2 rounded-xl bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 shadow-sm">
              <UserCircleIcon className="h-10 w-10 text-gray-400" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold text-gray-900 dark:text-white truncate uppercase tracking-tight">
                  {user?.username}
                </p>
                <p className="text-[10px] text-gray-500 dark:text-gray-400 truncate font-mono">
                  {user?.email}
                </p>
              </div>
            </div>
            <div className="flex items-center justify-between px-1">
              <ThemeToggle />
              <button
                onClick={() => setShowLogoutModal(true)}
                className="p-2.5 rounded-xl text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                title="Logout"
              >
                <ArrowLeftOnRectangleIcon className="h-5 w-5" />
              </button>
            </div>
            {sessionTimeRemaining > 0 && sessionTimeRemaining < 300 && (
              <div className="mt-3 px-2 py-1.5 rounded-lg bg-orange-50 dark:bg-orange-900/20 text-[10px] font-bold text-orange-600 dark:text-orange-400 text-center animate-pulse">
                SESSION EXPIRES IN {formatSessionTime(sessionTimeRemaining)}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="md:pl-64">
        <div className="sticky top-0 z-40 flex flex-col sm:flex-row h-auto sm:h-16 bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between flex-1 px-4 py-3 sm:py-0">
            <div className="flex items-center gap-4">
              <button
                type="button"
                className="px-4 text-gray-500 md:hidden"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                {mobileMenuOpen ? <XMarkIcon className="h-6 w-6" /> : <Bars3Icon className="h-6 w-6" />}
              </button>
              <div className="hidden sm:block">
                <h1 className="text-lg font-semibold text-gray-900 dark:text-white capitalize">
                  {currentPageName}
                </h1>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <QuickActionsToolbar
                onRefresh={handleRefresh}
                onNotifications={() => { }}
                onSettings={() => navigate('/settings')}
                isRefreshing={isRefreshing}
              />

              <div className="relative ml-2">
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <UserCircleIcon className="h-8 w-8 text-gray-400" />
                </button>

                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-50">
                    <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-700">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">{user?.username}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{user?.email}</p>
                    </div>
                    <button
                      onClick={() => {
                        setShowUserMenu(false)
                        setShowLogoutModal(true)
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                    >
                      Sign out
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {mobileMenuOpen && (
          <div className="md:hidden fixed inset-0 z-50 bg-gray-900/50" onClick={() => setMobileMenuOpen(false)}>
            <div className="fixed inset-y-0 left-0 w-64 bg-white dark:bg-gray-800 shadow-xl" onClick={(e) => e.stopPropagation()}>
              <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-2">
                  <CubeIcon className="h-8 w-8 text-primary-600" />
                  <span className="text-xl font-bold text-gray-900 dark:text-white">InfraMon</span>
                </div>
                <button onClick={() => setMobileMenuOpen(false)}>
                  <XMarkIcon className="h-6 w-6 text-gray-500" />
                </button>
              </div>
              <nav className="p-4 space-y-1">
                {navigation.map((item) => {
                  const isActive = location.pathname === item.href
                  return (
                    <NavLink
                      key={item.name}
                      to={item.href}
                      onClick={() => setMobileMenuOpen(false)}
                      className={`flex items-center px-3 py-2.5 text-sm font-medium rounded-lg ${isActive
                        ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-600'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50'
                        }`}
                    >
                      <item.icon className={`h-5 w-5 mr-3 ${isActive ? 'text-primary-600' : 'text-gray-400'}`} />
                      {item.name}
                    </NavLink>
                  )
                })}
              </nav>
            </div>
          </div>
        )}

        <main id="main-content" role="main" className="py-6 px-4 sm:px-6 lg:px-8 focus:outline-none" tabIndex={-1}>
          <div className="mb-6 hidden sm:block">
            <Breadcrumbs />
          </div>
          <Outlet />
        </main>

        <div className="px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
            <span>InfraMon v1.0.0</span>
            <div className="flex items-center gap-4">
              <span>Connected to Docker</span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-green-500" />
                Online
              </span>
            </div>
          </div>
        </div>
      </div>

      <Modal
        isOpen={showLogoutModal}
        onClose={() => setShowLogoutModal(false)}
        title="Sign out"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-gray-600 dark:text-gray-400">
            Are you sure you want to sign out of your account?
          </p>
          <div className="flex justify-end gap-3">
            <Button variant="secondary" onClick={() => setShowLogoutModal(false)}>
              Cancel
            </Button>
            <Button variant="danger" onClick={handleLogout}>
              Sign out
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
