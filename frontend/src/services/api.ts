import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig, CancelTokenSource } from 'axios'
import type {
  User,
  LoginRequest,
  LoginResponse,
  ContainerResponse,
  ContainerDetailResponse,
  ContainerListResponse,
  ContainerActionResponse,
  ContainerLogsResponse,
  ContainerStatsResponse,
  FormattedStats,
  ContainerDiffResponse,
  ProcessResponse,
  FilesystemResponse,
  ComposeInfo,
  ExecResponse,
  ShellInitResponse,
  LogsParams,
  ContainerGroupResponse,
  ContainerGroupDetailResponse,
  SystemStatsResponse,
  SystemInfoResponse,
  DiskPartition,
  NetworkInterface,
  NetworkConnection,
  DashboardResponse,
  SystemStatsHistoryResponse,
  ContainerStatsHistoryResponse,
  TopConsumersResponse,
  CompareResponse,
  TrendsResponse,
  GroupStatsResponse,
  PruneResponse,
  ExportResponse,
  CreateGroupRequest,
  UpdateGroupRequest,
  CreateUserRequest,
  UpdateUserRequest,
  ChangePasswordRequest,
  UserListResponse,
  UserDetailResponse,
  DockerInfo,
  DockerVersion,
  ComposeProject,
  ComposeFileResponse,
  ComposeValidationResponse,
} from '../types'

interface LogsParamsInternal extends LogsParams {
  stdout?: boolean
  stderr?: boolean
  timestamps?: boolean
  tail?: string
  since?: string
  until?: string
}

const API_URL = import.meta.env.VITE_API_URL || '/api/v1'

class ApiClient {
  private client: AxiosInstance
  private cancelTokens: Map<string, CancelTokenSource>

  constructor() {
    this.cancelTokens = new Map()
    
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    })

    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = localStorage.getItem('token')
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`
        }
        
        config.withCredentials = true
        return config
      },
      (error) => Promise.reject(error)
    )

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
          
          if (!window.location.pathname.includes('/login')) {
            window.location.href = '/login'
          }
        }
        
        const message = this.getErrorMessage(error)
        error.message = message
        
        return Promise.reject(error)
      }
    )
  }

  private getErrorMessage(error: AxiosError): string {
    if (error.response?.data && typeof error.response.data === 'object' && 'detail' in error.response.data) {
      return String(error.response.data.detail)
    }
    if (error.response?.status === 401) {
      return 'Authentication required. Please log in again.'
    }
    if (error.response?.status === 403) {
      return 'You do not have permission to perform this action.'
    }
    if (error.response?.status === 404) {
      return 'The requested resource was not found.'
    }
    if (error.response?.status === 422) {
      return 'Validation error. Please check your input.'
    }
    if (error.response?.status === 429) {
      return 'Too many requests. Please try again later.'
    }
    if (error.code === 'ECONNABORTED') {
      return 'Request timed out. Please try again.'
    }
    if (!window.navigator.onLine) {
      return 'You are offline. Please check your internet connection.'
    }
    return error.message || 'An unexpected error occurred.'
  }

  generateCancelToken(requestId: string): CancelTokenSource {
    this.cancelTokens.get(requestId)?.cancel('Request cancelled by user')
    const source = axios.CancelToken.source()
    this.cancelTokens.set(requestId, source)
    return source
  }

  removeCancelToken(requestId: string): void {
    this.cancelTokens.delete(requestId)
  }

  cancelAllRequests(reason?: string): void {
    this.cancelTokens.forEach((source) => source.cancel(reason || 'All requests cancelled'))
    this.cancelTokens.clear()
  }

  async get<T>(url: string, params?: Record<string, unknown> | undefined, requestId?: string): Promise<T> {
    const config = requestId ? { params, cancelToken: this.generateCancelToken(requestId).token } : { params }
    const response = await this.client.get<T>(url, config)
    return response.data
  }

  async post<T>(url: string, data?: unknown, options?: { requestId?: string; params?: Record<string, unknown> }): Promise<T> {
    const config: Record<string, unknown> = {}
    if (options?.requestId) {
      config.cancelToken = this.generateCancelToken(options.requestId).token
    }
    if (options?.params) {
      config.params = options.params
    }
    const response = await this.client.post<T>(url, data, config)
    return response.data
  }

  async put<T>(url: string, data?: unknown): Promise<T> {
    const response = await this.client.put<T>(url, data)
    return response.data
  }

  async patch<T>(url: string, data?: unknown): Promise<T> {
    const response = await this.client.patch<T>(url, data)
    return response.data
  }

  async delete<T>(url: string, params?: Record<string, unknown>): Promise<T> {
    const response = await this.client.delete<T>(url, { params })
    return response.data
  }

  async getWithRetry<T>(
    url: string,
    params?: Record<string, unknown>,
    retries = 3,
    delay = 1000
  ): Promise<T> {
    let lastError: Error | null = null
    
    for (let i = 0; i < retries; i++) {
      try {
        return await this.get<T>(url, params)
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error))
        
        if (axios.isCancel(error)) {
          throw error
        }
        
        if (i < retries - 1) {
          await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)))
        }
      }
    }
    
    throw lastError
  }
}

export const api = new ApiClient()

export const authService = {
  login: (username: string, password: string) =>
    api.post<{ access_token: string; refresh_token: string; user: User }>('/auth/login', { username, password }),
  logout: () => api.post('/auth/logout'),
  me: () => api.get<User>('/auth/me'),
  refreshToken: (refreshToken: string) =>
    api.post<{ access_token: string }>('/auth/refresh', { refresh_token: refreshToken }),
}

export const containerService = {
  list: (allContainers = false) =>
    api.get<ContainerListResponse>('/containers', { all_containers: allContainers }),
  get: (id: string) => api.get<ContainerDetailResponse>(`/containers/${id}`),
  start: (id: string) => api.post<ContainerActionResponse>(`/containers/${id}/start`),
  stop: (id: string, timeout = 10) =>
    api.post<ContainerActionResponse>(`/containers/${id}/stop`, null, { params: { timeout } }),
  restart: (id: string, timeout = 10, force = false) =>
    api.post<ContainerActionResponse>(`/containers/${id}/restart`, null, { params: { timeout, force } }),
  pause: (id: string) => api.post<ContainerActionResponse>(`/containers/${id}/pause`),
  unpause: (id: string) => api.post<ContainerActionResponse>(`/containers/${id}/unpause`),
  kill: (id: string, signal = 'SIGKILL') =>
    api.post<ContainerActionResponse>(`/containers/${id}/kill`, null, { params: { signal } }),
  remove: (id: string, force = false, volumes = false) =>
    api.delete<ContainerActionResponse>(`/containers/${id}`, { params: { force, volumes } }),
  rename: (id: string, newName: string) =>
    api.put<ContainerActionResponse>(`/containers/${id}/rename`, { new_name: newName }),
  update: (id: string, memoryLimit?: number, cpuShares?: number) =>
    api.patch<ContainerActionResponse>(`/containers/${id}`, { memory_limit: memoryLimit, cpu_shares: cpuShares }),
  logs: (id: string, params?: LogsParams) => api.get<{ logs: string }>(`/containers/${id}/logs`, params as Record<string, unknown>),
  stats: (id: string) => api.get<ContainerStatsResponse>(`/containers/${id}/stats`),
  statsFormatted: (id: string) => api.get<FormattedStats>(`/containers/${id}/stats/formatted`),
  inspect: (id: string) => api.get<Record<string, unknown>>(`/containers/${id}/inspect`),
  diff: (id: string) => api.get<ContainerDiffResponse>(`/containers/${id}/diff`),
  processes: (id: string) => api.get<ProcessResponse[]>(`/containers/${id}/processes`),
  filesystem: (id: string) => api.get<FilesystemResponse[]>(`/containers/${id}/filesystem`),
  composeInfo: (id: string) => api.get<ComposeInfo>(`/containers/${id}/compose`),
  pullImage: (id: string, noCache = false) =>
    api.post<ContainerActionResponse>(`/containers/${id}/compose/pull`, null, { params: { no_cache: noCache } }),
  exec: (id: string, cmd: string[]) => api.post<ExecResponse>(`/containers/${id}/exec`, { cmd }),
  initShell: (id: string, shell = '/bin/sh') =>
    api.post<ShellInitResponse>(`/containers/${id}/shell`, null, { params: { shell } }),
}

export const statsService = {
  system: () => api.get<SystemStatsResponse>('/stats/system'),
  systemInfo: () => api.get<SystemInfoResponse>('/stats/system/info'),
  disk: () => api.get<DiskPartition[]>('/stats/system/disk'),
  network: () => api.get<NetworkInterface[]>('/stats/system/network'),
  connections: (kind = 'inet') => api.get<NetworkConnection[]>(`/stats/system/connections`, { params: { kind } }),
  processes: (limit = 20, orderBy = 'cpu') =>
    api.get<ProcessResponse[]>('/stats/system/processes', { params: { limit, order_by: orderBy } }),
  history: (period = '1h', aggregate = false) =>
    api.get<SystemStatsHistoryResponse>('/stats/system/history', { params: { period, aggregate } }),
  containerHistory: (id: string, period = '1h', aggregate = false) =>
    api.get<ContainerStatsHistoryResponse>(`/stats/containers/${id}/history`, { params: { period, aggregate } }),
  dashboard: () => api.get<DashboardResponse>('/stats/dashboard'),
  topConsumers: (metric = 'cpu', limit = 10, period = '1h') =>
    api.get<TopConsumersResponse>('/stats/top-consumers', { params: { metric, limit, period } }),
  compare: (ids: string[], metric = 'cpu', period = '1h') =>
    api.get<CompareResponse>('/stats/compare', { params: { container_ids: ids, metric, period } }),
  trends: (metric = 'cpu', period = '7d') =>
    api.get<TrendsResponse>('/stats/trends', { params: { metric, period } }),
  groupStats: (groupId: number) => api.get<GroupStatsResponse>(`/stats/groups/${groupId}`),
  prune: (retentionDays = 30) => api.post<PruneResponse>('/stats/prune', null, { params: { retention_days: retentionDays } }),
  export: (type = 'system', period = '24h', format = 'json') =>
    api.get<ExportResponse>('/stats/export', { params: { stats_type: type, period, format } }),
}

export const groupService = {
  list: () => api.get<ContainerGroupResponse[]>('/groups'),
  get: (id: number) => api.get<ContainerGroupDetailResponse>(`/groups/${id}`),
  create: (data: CreateGroupRequest) => api.post<ContainerGroupResponse>('/groups', data),
  update: (id: number, data: UpdateGroupRequest) => api.put<ContainerGroupResponse>(`/groups/${id}`, data),
  delete: (id: number) => api.delete(`/groups/${id}`),
}

export const composeService = {
  projects: () => api.get<ComposeProject[]>('/compose/projects'),
  fileContent: (path: string) => api.get<ComposeFileResponse>('/compose/file', { params: { path } }),
  validate: (path: string) => api.get<ComposeValidationResponse>('/compose/validate', { params: { path } }),
}

export const dockerService = {
  info: () => api.get<DockerInfo>('/docker/info'),
  version: () => api.get<DockerVersion>('/docker/version'),
  pruneImages: (dangling = false) => api.post('/images/prune', null, { params: { filter_dangling: dangling } }),
  pruneNetworks: () => api.post('/networks/prune'),
  pruneVolumes: () => api.post('/volumes/prune'),
}

export const userService = {
  list: (page = 1, pageSize = 20) =>
    api.get<UserListResponse>('/users', { params: { page, page_size: pageSize } }),
  get: (id: number) => api.get<UserDetailResponse>(`/users/${id}`),
  create: (data: CreateUserRequest) => api.post<User>('/users', data),
  update: (id: number, data: UpdateUserRequest) => api.put<UserDetailResponse>(`/users/${id}`, data),
  delete: (id: number) => api.delete(`/users/${id}`),
  changePassword: (id: number, data: ChangePasswordRequest) =>
    api.post(`/users/${id}/change-password`, data),
}
