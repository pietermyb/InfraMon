import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook } from '@testing-library/react'
import { useTheme, ThemeProvider } from '../hooks/useTheme'

const renderThemeHook = () => {
  return renderHook(() => useTheme(), {
    wrapper: ({ children }) => <ThemeProvider>{children}</ThemeProvider>,
  })
}

describe('useTheme Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    document.documentElement.classList.remove('dark', 'light')
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('has theme state', () => {
    const { result } = renderThemeHook()
    expect(result.current).toHaveProperty('theme')
    expect(result.current).toHaveProperty('toggleTheme')
    expect(result.current.theme).toBeDefined()
  })

  it('has toggleTheme function', () => {
    const { result } = renderThemeHook()
    expect(typeof result.current.toggleTheme).toBe('function')
  })

  it('initializes with a theme value', () => {
    const { result } = renderThemeHook()
    expect(result.current.theme).toBeDefined()
    expect(['light', 'dark']).toContain(result.current.theme)
  })

  it('theme is either light or dark', () => {
    const { result } = renderThemeHook()
    expect(['light', 'dark']).toContain(result.current.theme)
  })
})
