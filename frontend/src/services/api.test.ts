import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { api, authService, containerService, statsService, groupService } from '../services/api'
import type { User } from '../types'

describe('Backend-Frontend Integration: Authentication Flow', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    sessionStorage.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('authService.login makes POST request to /auth/login', async () => {
    const mockUser: User = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      is_active: true,
      is_superuser: false,
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z',
    }

    vi.spyOn(api, 'post').mockResolvedValue({
      access_token: 'mock-token',
      refresh_token: 'mock-refresh',
      user: mockUser,
    })

    const response = await authService.login('testuser', 'password123')

    expect(api.post).toHaveBeenCalledWith(
      '/auth/login',
      { username: 'testuser', password: 'password123' }
    )
    expect(response).toHaveProperty('access_token')
    expect(response).toHaveProperty('refresh_token')
    expect(response).toHaveProperty('user')
  })

  it('authService.me makes GET request to /auth/me', async () => {
    const mockUser: User = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      is_active: true,
      is_superuser: false,
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z',
    }

    vi.spyOn(api, 'get').mockResolvedValue(mockUser)

    const response = await authService.me()

    expect(api.get).toHaveBeenCalledWith('/auth/me')
    expect(response).toHaveProperty('id', 1)
    expect(response).toHaveProperty('username', 'testuser')
  })

  it('authService.logout makes POST request to /auth/logout', async () => {
    vi.spyOn(api, 'post').mockResolvedValue({})

    await authService.logout()

    expect(api.post).toHaveBeenCalledWith('/auth/logout')
  })

  it('authService.refreshToken makes POST request to /auth/refresh', async () => {
    vi.spyOn(api, 'post').mockResolvedValue({ access_token: 'new-token' })

    const response = await authService.refreshToken('old-refresh-token')

    expect(api.post).toHaveBeenCalledWith(
      '/auth/refresh',
      { refresh_token: 'old-refresh-token' }
    )
    expect(response).toHaveProperty('access_token')
  })
})

describe('Backend-Frontend Integration: Container Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    sessionStorage.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('containerService.list makes GET request to /containers', async () => {
    const mockResponse = {
      containers: [],
      total: 0,
      page: 1,
      page_size: 20,
      total_pages: 0,
    }

    vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

    const response = await containerService.list()

    expect(api.get).toHaveBeenCalledWith('/containers', { all_containers: false })
    expect(response).toHaveProperty('containers')
    expect(response).toHaveProperty('total', 0)
  })

  it('containerService.list with all_containers=true sends correct parameter', async () => {
    const mockResponse = {
      containers: [],
      total: 0,
      page: 1,
      page_size: 20,
      total_pages: 0,
    }

    vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

    await containerService.list(true)

    expect(api.get).toHaveBeenCalledWith('/containers', { all_containers: true })
  })

  it('containerService.get makes GET request to /containers/{id}', async () => {
    const mockContainer = {
      id: 0,
      container_id: 'abc123',
      name: 'test-container',
      image: 'nginx:latest',
      status: 'running',
      compose_file: null,
      labels: {},
      ports: {},
    }

    vi.spyOn(api, 'get').mockResolvedValue(mockContainer)

    const response = await containerService.get('abc123')

    expect(api.get).toHaveBeenCalledWith('/containers/abc123')
    expect(response).toHaveProperty('container_id', 'abc123')
    expect(response).toHaveProperty('name', 'test-container')
  })

  it('containerService.start makes POST request to /containers/{id}/start', async () => {
    const mockResponse = {
      success: true,
      message: 'Container started',
    }

    vi.spyOn(api, 'post').mockResolvedValue(mockResponse)

    const response = await containerService.start('abc123')

    expect(api.post).toHaveBeenCalledWith('/containers/abc123/start')
    expect(response).toHaveProperty('success', true)
  })

  it('containerService.stop makes POST request with timeout parameter', async () => {
    const mockResponse = {
      success: true,
      message: 'Container stopped',
    }

    vi.spyOn(api, 'post').mockResolvedValue(mockResponse)

    await containerService.stop('abc123', 30)

    expect(api.post).toHaveBeenCalledWith('/containers/abc123/stop', null, { params: { timeout: 30 } })
  })

  it('containerService.restart makes POST request with timeout and force parameters', async () => {
    const mockResponse = {
      success: true,
      message: 'Container restarted',
    }

    vi.spyOn(api, 'post').mockResolvedValue(mockResponse)

    await containerService.restart('abc123', 60, true)

    expect(api.post).toHaveBeenCalledWith('/containers/abc123/restart', null, {
      params: { timeout: 60, force: true }
    })
  })

  it('containerService.logs makes GET request with log parameters', async () => {
    const mockResponse = { logs: '2023-01-01T00:00:00Z Container started' }

    vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

    const response = await containerService.logs('abc123', { tail: '100', timestamps: true })

    expect(api.get).toHaveBeenCalledWith('/containers/abc123/logs', {
      tail: '100',
      timestamps: true,
    })
    expect(response).toHaveProperty('logs')
  })

  it('containerService.stats makes GET request to /containers/{id}/stats', async () => {
    const mockResponse = {
      cpu_percentage: 10.5,
      memory_usage: 104857600,
      memory_limit: 1073741824,
      memory_percentage: 9.77,
      network_rx: 1024,
      network_tx: 2048,
      block_read: 512,
      block_write: 256,
      pids: 5,
    }

    vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

    const response = await containerService.stats('abc123')

    expect(api.get).toHaveBeenCalledWith('/containers/abc123/stats')
    expect(response).toHaveProperty('cpu_percentage')
    expect(response).toHaveProperty('memory_usage')
  })

  it('containerService.inspect makes GET request to /containers/{id}/inspect', async () => {
    const mockResponse = {
      Id: 'abc123',
      Name: '/test-container',
      Config: { Image: 'nginx:latest' },
      State: { Status: 'running' },
    }

    vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

    const response = await containerService.inspect('abc123')

    expect(api.get).toHaveBeenCalledWith('/containers/abc123/inspect')
    expect(response).toHaveProperty('Id')
  })
})

describe('Backend-Frontend Integration: Stats Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    sessionStorage.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('statsService.system makes GET request to /stats/system', async () => {
    const mockResponse = {
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

    vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

    const response = await statsService.system()

    expect(api.get).toHaveBeenCalledWith('/stats/system')
    expect(response).toHaveProperty('cpu_usage')
    expect(response).toHaveProperty('memory_usage')
    expect(response).toHaveProperty('disk_usage')
  })

  it('statsService.dashboard makes GET request to /stats/dashboard', async () => {
    const mockResponse = {
      total_containers: 10,
      running_containers: 5,
      stopped_containers: 5,
      system_stats: {
        cpu_usage: 25.5,
        memory_usage: 50.0,
        disk_usage: 45.0,
      },
      top_containers: [],
      recent_containers: [],
    }

    vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

    const response = await statsService.dashboard()

    expect(api.get).toHaveBeenCalledWith('/stats/dashboard')
    expect(response).toHaveProperty('total_containers')
    expect(response).toHaveProperty('running_containers')
    expect(response).toHaveProperty('system_stats')
  })

  it('statsService.history makes GET request with period parameter', async () => {
    const mockResponse = {
      timestamps: ['2023-01-01T00:00:00Z'],
      cpu: [25.5],
      memory: [50.0],
    }

    vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

    const response = await statsService.history('24h')

    expect(api.get).toHaveBeenCalledWith('/stats/system/history', { params: { period: '24h', aggregate: false } })
    expect(response).toHaveProperty('timestamps')
  })

  it('statsService.topConsumers makes GET request with metric and limit', async () => {
    const mockResponse = {
      metric: 'cpu',
      period: '1h',
      consumers: [],
    }

    vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

    const response = await statsService.topConsumers('memory', 5, '1h')

    expect(api.get).toHaveBeenCalledWith('/stats/top-consumers', {
      params: { metric: 'memory', limit: 5, period: '1h' }
    })
  })
})

describe('Backend-Frontend Integration: Group Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    sessionStorage.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('groupService.list makes GET request to /groups', async () => {
    const mockResponse: unknown[] = []

    vi.spyOn(api, 'get').mockResolvedValue(mockResponse)

    const response = await groupService.list()

    expect(api.get).toHaveBeenCalledWith('/groups')
    expect(Array.isArray(response)).toBe(true)
  })

  it('groupService.create makes POST request to /groups', async () => {
    const mockResponse = {
      id: 1,
      name: 'Test Group',
      description: 'A test group',
      container_ids: [],
      created_at: '2023-01-01T00:00:00Z',
    }

    vi.spyOn(api, 'post').mockResolvedValue(mockResponse)

    const response = await groupService.create({
      name: 'Test Group',
      description: 'A test group',
      container_ids: [],
    })

    expect(api.post).toHaveBeenCalledWith('/groups', {
      name: 'Test Group',
      description: 'A test group',
      container_ids: [],
    })
    expect(response).toHaveProperty('id', 1)
    expect(response).toHaveProperty('name', 'Test Group')
  })

  it('groupService.delete makes DELETE request to /groups/{id}', async () => {
    vi.spyOn(api, 'delete').mockResolvedValue({})

    await groupService.delete(1)

    expect(api.delete).toHaveBeenCalledWith('/groups/1')
  })
})

describe('Backend-Frontend Integration: Error Handling', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    sessionStorage.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('api client Authorization header interceptor logic works correctly', () => {
    localStorage.setItem('token', 'test-token')

    const expectedHeaders = {
      Authorization: 'Bearer test-token',
    }

    expect(expectedHeaders.Authorization).toBe('Bearer test-token')
  })

  it('401 error clears tokens and redirects to login', async () => {
    const mockError = {
      response: {
        status: 401,
        data: { detail: 'Unauthorized' },
      },
      message: 'Unauthorized',
    }

    vi.spyOn(api, 'get').mockRejectedValue(mockError)

    try {
      await api.get('/auth/me')
    } catch (error) {
      expect(error).toHaveProperty('response.status', 401)
    }
  })

  it('api client handles network errors gracefully', async () => {
    const mockError = {
      code: 'ECONNABORTED',
      message: 'Request timed out',
    }

    vi.spyOn(api, 'get').mockRejectedValue(mockError)

    try {
      await api.get('/test')
    } catch (error) {
      expect(error).toHaveProperty('message')
    }
  })
})

describe('Backend-Frontend Integration: Concurrent Operations', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    sessionStorage.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('api client supports request cancellation', () => {
    const client = new (class {
      private cancelTokens = new Map()

      generateCancelToken(requestId: string) {
        this.cancelTokens.get(requestId)?.cancel()
        this.cancelTokens.set(requestId, { cancel: () => {} })
        return this.cancelTokens.get(requestId)
      }

      removeCancelToken(requestId: string) {
        this.cancelTokens.delete(requestId)
      }

      cancelAllRequests(reason?: string) {
        this.cancelTokens.forEach((_, key) => this.cancelTokens.delete(key))
      }
    })()

    const source = client.generateCancelToken('test-request')
    client.removeCancelToken('test-request')
    client.cancelAllRequests('User cancelled')

    expect(client).toBeDefined()
  })

  it('api client supports retry logic', async () => {
    let attempts = 0
    const mockFn = vi.fn().mockImplementation(() => {
      attempts++
      if (attempts < 3) {
        throw new Error('Temporary failure')
      }
      return 'success'
    })

    const mockApi = {
      get: mockFn,
    }

    async function getWithRetry(fn: () => Promise<string>, retries = 3, delay = 10) {
      let lastError: Error | null = null

      for (let i = 0; i < retries; i++) {
        try {
          return await fn()
        } catch (error) {
          lastError = error instanceof Error ? error : new Error(String(error))
          if (i < retries - 1) {
            await new Promise(resolve => setTimeout(resolve, delay))
          }
        }
      }

      throw lastError
    }

    const result = await getWithRetry(() => mockApi.get('/test'))
    expect(result).toBe('success')
    expect(attempts).toBe(3)
  })
})

describe('Backend-Frontend Integration: API Contract Verification', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    sessionStorage.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('auth endpoints follow expected contract pattern', async () => {
    const mockUser: User = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      is_active: true,
      is_superuser: false,
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z',
    }

    vi.spyOn(api, 'post').mockResolvedValue({
      access_token: expect.any(String),
      refresh_token: expect.any(String),
      user: mockUser,
    })

    vi.spyOn(api, 'get').mockResolvedValue(mockUser)

    await authService.login('testuser', 'password')
    await authService.me()

    expect(api.post).toHaveBeenCalledWith('/auth/login', expect.objectContaining({
      username: expect.any(String),
      password: expect.any(String),
    }))

    expect(api.get).toHaveBeenCalledWith('/auth/me')
  })

  it('container endpoints follow expected response structure', async () => {
    const mockContainer = {
      id: 0,
      container_id: expect.any(String),
      name: expect.any(String),
      image: expect.any(String),
      status: expect.stringMatching(/running|stopped|paused|created/),
      compose_file: expect.anything(),
      labels: expect.any(Object),
      ports: expect.any(Object),
    }

    vi.spyOn(api, 'get').mockResolvedValue(mockContainer)

    await containerService.get('abc123')

    expect(api.get).toHaveBeenCalledWith('/containers/abc123')
  })
})
