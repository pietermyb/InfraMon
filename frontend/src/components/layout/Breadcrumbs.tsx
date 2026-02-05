import { Link, useLocation } from 'react-router-dom'
import { ChevronRightIcon, HomeIcon } from '@heroicons/react/24/outline'

interface BreadcrumbItem {
  name: string
  href?: string
}

export function Breadcrumbs() {
  const location = useLocation()
  const pathnames = location.pathname.split('/').filter(Boolean)

  const getPageName = (path: string) => {
    const nameMap: Record<string, string> = {
      dashboard: 'Dashboard',
      containers: 'Containers',
      settings: 'Settings',
    }
    return nameMap[path] || path
  }

  if (pathnames.length === 0) {
    return (
      <nav className="flex" aria-label="Breadcrumb">
        <ol className="flex items-center space-x-2">
          <li>
            <span className="text-gray-400 dark:text-gray-500">Dashboard</span>
          </li>
        </ol>
      </nav>
    )
  }

  const items: BreadcrumbItem[] = pathnames.map((path, index) => {
    const href = `/${pathnames.slice(0, index + 1).join('/')}`
    const isLast = index === pathnames.length - 1
    return {
      name: getPageName(path),
      href: isLast ? undefined : href,
    }
  })

  return (
    <nav className="flex" aria-label="Breadcrumb">
      <ol className="flex items-center space-x-2">
        <li>
          <Link
            to="/dashboard"
            className="text-gray-400 hover:text-gray-500 dark:text-gray-500 dark:hover:text-gray-400"
          >
            <HomeIcon className="h-5 w-5" />
          </Link>
        </li>
        {items.map((item, index) => (
          <li key={index} className="flex items-center">
            <ChevronRightIcon
              className="h-4 w-4 text-gray-300 dark:text-gray-600 flex-shrink-0"
              aria-hidden="true"
            />
            {item.href ? (
              <Link
                to={item.href}
                className="ml-2 text-sm font-medium text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
              >
                {item.name}
              </Link>
            ) : (
              <span className="ml-2 text-sm font-medium text-gray-900 dark:text-white">
                {item.name}
              </span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  )
}
