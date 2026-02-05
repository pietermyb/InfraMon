import { useState, useCallback, createContext, useContext, useEffect, useRef } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { User } from '../types'

const API_URL = import.meta.env.VITE_API_URL || '/api/v1'

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
  updateUser: (user: Partial<User>) => void
  sessionTimeRemaining: number
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const TOKEN_REFRESH_INTERVAL = 5 * 60 * 1000
const SESSION_TIMEOUT = 30 * 60 * 1000

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('user')
    return saved ? JSON.parse(saved) : null
  })
  const [isLoading, setIsLoading] = useState(false)
  const [sessionTimeRemaining, setSessionTimeRemaining] = useState(0)
  const refreshTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const sessionTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const lastActivityRef = useRef<number>(Date.now())
  const navigate = useNavigate()
  const location = useLocation()

  const setupAxiosInterceptors = useCallback((token: string) => {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

    axios.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        lastActivityRef.current = Date.now()
        return config
      },
      (error) => Promise.reject(error)
    )

    axios.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401 && !location.pathname.includes('/login')) {
          localStorage.removeItem('token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
          setUser(null)
          navigate('/login', { replace: true })
        }
        return Promise.reject(error)
      }
    )
  }, [location.pathname, navigate])

  const clearSessionTimers = useCallback(() => {
    if (refreshTimeoutRef.current) {
      clearTimeout(refreshTimeoutRef.current)
      refreshTimeoutRef.current = null
    }
    if (sessionTimeoutRef.current) {
      clearTimeout(sessionTimeoutRef.current)
      sessionTimeoutRef.current = null
    }
  }, [])

  const setupSessionTimers = useCallback((accessToken: string) => {
    clearSessionTimers()

    refreshTimeoutRef.current = setTimeout(async () => {
      await refreshToken()
    }, TOKEN_REFRESH_INTERVAL)

    sessionTimeoutRef.current = setTimeout(() => {
      logout()
    }, SESSION_TIMEOUT)

    lastActivityRef.current = Date.now()
  }, [clearSessionTimers])

  const refreshToken = useCallback(async () => {
    const refreshTokenValue = localStorage.getItem('refresh_token')
    if (!refreshTokenValue) {
      logout()
      return
    }

    try {
      const response = await axios.post(`${API_URL}/auth/refresh`, {
        refresh_token: refreshTokenValue
      })
      
      const { access_token } = response.data
      localStorage.setItem('token', access_token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      setupSessionTimers(access_token)
    } catch {
      logout()
    }
  }, [setupSessionTimers])

  const login = useCallback(async (username: string, password: string) => {
    setIsLoading(true)
    try {
      const response = await axios.post(`${API_URL}/auth/login`, { username, password })
      const { access_token, refresh_token, user: userData } = response.data
      
      localStorage.setItem('token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      localStorage.setItem('user', JSON.stringify(userData))
      
      setUser(userData)
      setupAxiosInterceptors(access_token)
      setupSessionTimers(access_token)
    } finally {
      setIsLoading(false)
    }
  }, [setupAxiosInterceptors, setupSessionTimers])

  const logout = useCallback(() => {
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    delete axios.defaults.headers.common['Authorization']
    
    clearSessionTimers()
    setUser(null)
    
    if (!location.pathname.includes('/login')) {
      navigate('/login', { replace: true })
    }
  }, [clearSessionTimers, location.pathname, navigate])

  const updateUser = useCallback((updates: Partial<User>) => {
    if (user) {
      const updatedUser = { ...user, ...updates }
      setUser(updatedUser)
      localStorage.setItem('user', JSON.stringify(updatedUser))
    }
  }, [user])

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token && user) {
      setupAxiosInterceptors(token)
      setupSessionTimers(token)
    }

    const handleActivity = () => {
      lastActivityRef.current = Date.now()
    }

    window.addEventListener('click', handleActivity)
    window.addEventListener('keypress', handleActivity)
    window.addEventListener('scroll', handleActivity)

    return () => {
      window.removeEventListener('click', handleActivity)
      window.removeEventListener('keypress', handleActivity)
      window.removeEventListener('scroll', handleActivity)
      clearSessionTimers()
    }
  }, [user, setupAxiosInterceptors, setupSessionTimers, clearSessionTimers])

  useEffect(() => {
    const checkSession = () => {
      const elapsed = Date.now() - lastActivityRef.current
      setSessionTimeRemaining(Math.max(0, SESSION_TIMEOUT - elapsed))
      
      if (elapsed >= SESSION_TIMEOUT) {
        logout()
      }
    }

    const interval = setInterval(checkSession, 1000)
    return () => clearInterval(interval)
  }, [logout])

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      logout,
      refreshToken,
      updateUser,
      sessionTimeRemaining,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
