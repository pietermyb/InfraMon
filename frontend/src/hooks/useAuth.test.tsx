import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { useAuth, AuthProvider } from '../hooks/useAuth'

const renderAuthHook = () => {
  return renderHook(() => useAuth(), {
    wrapper: ({ children }) => (
      <MemoryRouter>
        <AuthProvider>{children}</AuthProvider>
      </MemoryRouter>
    ),
  })
}

describe('useAuth Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    sessionStorage.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('provides auth context with required properties', () => {
    const { result } = renderAuthHook()

    expect(result.current).toHaveProperty('isAuthenticated')
    expect(result.current).toHaveProperty('isLoading')
    expect(result.current).toHaveProperty('user')
    expect(result.current).toHaveProperty('login')
    expect(result.current).toHaveProperty('logout')
  })

  it('has login function', () => {
    const { result } = renderAuthHook()

    expect(typeof result.current.login).toBe('function')
  })

  it('has logout function', () => {
    const { result } = renderAuthHook()

    expect(typeof result.current.logout).toBe('function')
  })

  it('has refreshToken function', () => {
    const { result } = renderAuthHook()

    expect(typeof result.current.refreshToken).toBe('function')
  })

  it('has updateUser function', () => {
    const { result } = renderAuthHook()

    expect(typeof result.current.updateUser).toBe('function')
  })

  it('sessionTimeRemaining is a number', () => {
    const { result } = renderAuthHook()

    expect(typeof result.current.sessionTimeRemaining).toBe('number')
  })

  it('isAuthenticated is a boolean', () => {
    const { result } = renderAuthHook()

    expect(typeof result.current.isAuthenticated).toBe('boolean')
  })

  it('isLoading is a boolean', () => {
    const { result } = renderAuthHook()

    expect(typeof result.current.isLoading).toBe('boolean')
  })
})
