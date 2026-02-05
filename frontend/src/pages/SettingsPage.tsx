import { useTheme } from '../hooks/useTheme'
import { Card, Button } from '../components/ui'
import { SunIcon, MoonIcon, ComputerDesktopIcon, CheckCircleIcon } from '@heroicons/react/24/outline'
import { clsx } from 'clsx'

export default function SettingsPage() {
  const { theme, toggleTheme } = useTheme()

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
    },
    {
      id: 'system',
      name: 'System Preference',
      description: 'Sync with your operating system',
      icon: ComputerDesktopIcon,
      active: false, // For now we only have toggle, but we can expand this
    }
  ]

  return (
    <div className="space-y-8 animate-fade-in">
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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {themeOptions.map((option) => (
            <button
              key={option.id}
              onClick={() => {
                if (option.id === 'system') {
                  // Logic for system handled by removing item or similar, 
                  // but for now let's just make the toggle more obvious
                  const systemIsDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                  if ((systemIsDark && theme !== 'dark') || (!systemIsDark && theme !== 'light')) {
                    toggleTheme();
                  }
                } else if ((option.id === 'light' && theme === 'dark') || (option.id === 'dark' && theme === 'light')) {
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

      <Card className="bg-gradient-to-br from-primary-600 to-primary-800 text-white border-none p-8">
        <h3 className="text-xl font-bold mb-2">More coming soon</h3>
        <p className="text-primary-100 mb-6 max-w-md">
          We're working on notification settings, language preferences, and custom dashboard layouts.
        </p>
        <Button variant="secondary" className="bg-white/10 hover:bg-white/20 border-white/20 text-white">
          View Roadmap
        </Button>
      </Card>
    </div>
  )
}
