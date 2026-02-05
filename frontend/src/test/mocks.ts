import { vi } from 'vitest'
import axios from 'axios'

export const mockUser = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  is_active: true,
  is_superuser: false,
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
}

export const mockToken = 'mock-jwt-token'
export const mockRefreshToken = 'mock-refresh-token'

export const mockApiResponse = {
  data: {
    access_token: mockToken,
    refresh_token: mockRefreshToken,
    user: mockUser,
  },
}

export const mockContainers = [
  {
    id: 0,
    container_id: 'abc123def456',
    name: 'web-server',
    image: 'nginx:latest',
    status: 'running',
    compose_file: '/opt/docker-compose.yml',
    labels: { app: 'web' },
    ports: { '80/tcp': { HostIp: '0.0.0.0', HostPort: '8080' } },
  },
  {
    id: 1,
    container_id: 'xyz789abc012',
    name: 'redis',
    image: 'redis:alpine',
    status: 'running',
    compose_file: null,
    labels: {},
    ports: { '6379/tcp': { HostIp: '0.0.0.0', HostPort: '6379' } },
  },
]

export const mockSystemStats = {
  cpu_usage: 25.5,
  memory_usage: 50.0,
  memory_total: 17179869184,
  memory_used: 8589934592,
  memory_available: 8589934592,
  disk_usage: 45.0,
  disk_total: 512000000000,
  disk_used: 256000000000,
  disk_free: 256000000000,
  network_bytes_sent: 1024,
  network_bytes_recv: 2048,
  load_average: [1.0, 1.5, 2.0],
  boot_time: 1672531200,
}

export const createMockApi = () => {
  return {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  }
}

export const mockAxios = {
  create: vi.fn(() => createMockApi()),
  defaults: {
    headers: {
      common: {},
    },
  },
  interceptors: {
    request: {
      use: vi.fn(),
    },
    response: {
      use: vi.fn(),
    },
  },
}

export const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}

export const mockWindowLocation = {
  href: 'http://localhost:3000',
  pathname: '/dashboard',
  search: '',
  hash: '',
  assign: vi.fn(),
  replace: vi.fn(),
  reload: vi.fn(),
}

export const mockNavigate = vi.fn()
export const mockLocation = {
  pathname: '/dashboard',
  search: '',
  hash: '',
}

export const setupAuthMocks = (isAuthenticated = true) => {
  if (isAuthenticated) {
    localStorage.setItem('token', mockToken)
    localStorage.setItem('refresh_token', mockRefreshToken)
    localStorage.setItem('user', JSON.stringify(mockUser))
  } else {
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }
}

export const cleanupAuthMocks = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
}

export const waitFor = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

export const asyncTimeout = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))
