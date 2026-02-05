import { useState } from 'react'
import { useTheme } from '../hooks/useTheme'
import { Card, Button } from '../components/ui'
import { SunIcon, MoonIcon, CheckCircleIcon, KeyIcon } from '@heroicons/react/24/outline'
import { clsx } from 'clsx'
import api from '../api/client'
import { ChangePasswordRequest } from '../types'

export default function SettingsPage() {
  const { theme, toggleTheme } = useTheme()
  const [formData, setFormData] = useState<ChangePasswordRequest>({
    current_password: '',
    new_password: '',
    new_password_confirm: ''
  })
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  const themeOptions = [
    {
      id: 'light',
      name: 'Light Mode',
      description: 'Clean and bright appearance',
      icon: SunIcon,
      active: theme === 'light',
    },
    {
      id: 'dark',
      name: 'Dark Mode',
      description: 'Easy on the eyes in low light',
      icon: MoonIcon,
      active: theme === 'dark',
    }
  ]

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setMessage(null)

    if (formData.new_password !== formData.new_password_confirm) {
      setMessage({ type: 'error', text: 'New passwords do not match' })
      setLoading(false)
      return
    }

    try {
      await api.post('/auth/change-password', formData)
      setMessage({ type: 'success', text: 'Password updated successfully' })
      setFormData({
        current_password: '',
        new_password: '',
        new_password_confirm: ''
      })
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Failed to update password'
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8 animate-fade-in max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-text-title">Settings</h1>
        <p className="mt-1 text-text-body">
          Manage your interface preferences and application configuration.
        </p>
      </div>

      <section className="space-y-4">
        <h3 className="text-lg font-semibold text-text-title flex items-center gap-2">
          Appearance
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {themeOptions.map((option) => (
            <button
              key={option.id}
              onClick={() => {
                if ((option.id === 'light' && theme === 'dark') || (option.id === 'dark' && theme === 'light')) {
                  toggleTheme();
                }
              }}
              className={clsx(
                'relative flex flex-col items-start p-5 rounded-2xl border-2 text-left transition-all duration-200 group',
                option.active
                  ? 'border-primary-500 bg-canvas-selected'
                  : 'border-border-subtle hover:border-border-medium bg-canvas-card'
              )}
            >
              <div className={clsx(
                'p-2 rounded-xl mb-4 transition-colors',
                option.active ? 'bg-primary-500 text-white' : 'bg-canvas-hover text-text-body group-hover:bg-gray-200 dark:group-hover:bg-gray-700'
              )}>
                <option.icon className="h-6 w-6" />
              </div>
              <div className="flex-1">
                <h4 className="font-bold text-text-title">{option.name}</h4>
                <p className="text-sm text-text-body">{option.description}</p>
              </div>
              {option.active && (
                <div className="absolute top-4 right-4 text-primary-500">
                  <CheckCircleIcon className="h-6 w-6" />
                </div>
              )}
            </button>
          ))}
        </div>
      </section>

      <section className="space-y-4">
        <h3 className="text-lg font-semibold text-text-title flex items-center gap-2">
          <KeyIcon className="h-5 w-5" />
          Security
        </h3>
        <Card className="p-6 bg-canvas-card border-border-subtle">
          <form onSubmit={handleChangePassword} className="space-y-4 max-w-md">
            <h4 className="font-medium text-text-title">Change Password</h4>

            {message && (
              <div className={clsx(
                "p-3 rounded-md text-sm",
                message.type === 'success' ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
              )}>
                {message.text}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-text-body mb-1">Current Password</label>
              <input
                type="password"
                required
                value={formData.current_password}
                onChange={e => setFormData({ ...formData, current_password: e.target.value })}
                className="w-full px-3 py-2 bg-canvas-base border border-border-subtle rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 text-text-title"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-body mb-1">New Password</label>
              <input
                type="password"
                required
                minLength={8}
                value={formData.new_password}
                onChange={e => setFormData({ ...formData, new_password: e.target.value })}
                className="w-full px-3 py-2 bg-canvas-base border border-border-subtle rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 text-text-title"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-body mb-1">Confirm New Password</label>
              <input
                type="password"
                required
                minLength={8}
                value={formData.new_password_confirm}
                onChange={e => setFormData({ ...formData, new_password_confirm: e.target.value })}
                className="w-full px-3 py-2 bg-canvas-base border border-border-subtle rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 text-text-title"
              />
            </div>

            <div className="pt-2">
              <Button type="submit" variant="primary" isLoading={loading}>
                Update Password
              </Button>
            </div>
          </form>
        </Card>
      </section>
    </div>
  )
}
