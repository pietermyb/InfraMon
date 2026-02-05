export interface User {
  id: number
  username: string
  email: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at?: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token?: string
  token_type: string
  user: User
}

export interface ContainerResponse {
  id: number
  container_id: string
  name: string
  image: string
  status: string
  group_id: number | null
  docker_compose_path?: string
  ports?: Record<string, any>
  labels?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface ContainerDetailResponse extends ContainerResponse {
  ports?: Record<string, unknown>
  volumes?: Array<Record<string, unknown>>
  environment?: Array<{ name: string; value: string }>
  networks?: string[]
  labels?: Record<string, unknown>
  command?: string[]
  started_at?: string
  finished_at?: string
  restart_policy?: Record<string, unknown>
  healthcheck?: Record<string, unknown>
  hostname?: string
  ip_address?: string
  gateway?: string
  mac_address?: string
  memory_limit?: number
  cpu_shares?: number
}

export interface ContainerListResponse {
  containers: ContainerResponse[]
  total: number
  running: number
  stopped: number
}

export interface ContainerActionResponse {
  success: boolean
  message: string
  container_id: string
  details?: Record<string, unknown>
}

export interface ContainerLogsResponse {
  container_id: string
  logs: string
  timestamp: string
}

export interface ContainerStatsResponse {
  id: number
  container_id: number
  cpu_usage: number
  memory_usage: number
  memory_limit: number
  network_rx: number
  network_tx: number
  block_read: number
  block_write: number
  pids: number
  timestamp: string
}

export interface FormattedStats {
  container_id: string
  cpu_usage: number
  memory_usage: number
  memory_limit: number
  memory_percent: number
  network_rx: number
  network_tx: number
  block_read: number
  block_write: number
  pids: number
}

export interface ContainerDiffResponse {
  container_id: string
  changes: Array<{
    path: string
    kind: string
    change: string
  }>
}

export interface ProcessResponse {
  pid: number
  name: string
  username?: string
  cmdline?: string
  cpu_percent: number
  memory_percent: number
}

export interface FilesystemResponse {
  mount_point: string
  source?: string
  type?: string
  total?: number
  used?: number
  free?: number
  percent?: number
}

export interface ComposeInfo {
  container_id: string
  compose_file_path?: string
  project_name?: string
  services?: string[]
}

export interface ExecResponse {
  success: boolean
  output?: string
  error?: string
}

export interface ShellInitResponse {
  success: boolean
  exec_id?: string
  error?: string
}

export interface LogsParams {
  stdout?: boolean
  stderr?: boolean
  timestamps?: boolean
  tail?: string
  since?: string
  until?: string
}

export interface ContainerGroupResponse {
  id: number
  name: string
  description?: string
  color: string
  created_at: string
  updated_at: string
}

export interface ContainerGroupDetailResponse extends ContainerGroupResponse {
  containers: ContainerResponse[]
}

export interface SystemStatsResponse {
  id: number
  cpu_usage: number
  cpu_cores: number
  cpu_frequency: number
  memory_usage: number
  memory_total: number
  memory_used: number
  memory_available: number
  swap_usage: number
  swap_total: number
  disk_usage: number
  disk_total: number
  disk_used: number
  disk_free: number
  disk_read_bytes: number
  disk_write_bytes: number
  network_rx: number
  network_tx: number
  network_interfaces: NetworkInterface[]
  load_avg_1m: number
  load_avg_5m: number
  load_avg_15m: number
  load_percent: number
  uptime: number
  boot_time?: string
  temperatures: Record<string, number>
  timestamp: string
}

export interface NetworkInterface {
  interface: string
  bytes_sent: number
  bytes_recv: number
  packets_sent: number
  packets_recv: number
  errin: number
  errout: number
  dropin: number
  dropout: number
}

export interface SystemInfoResponse {
  hostname: string
  system: string
  release: string
  version: string
  machine: string
  boot_time: string
  uptime: number
  cpu_architecture: string
  kernel_version: string
  connected_users: Array<{
    name: string
    terminal: string
    host: string
    started: string
  }>
  python_version: string
}

export interface DiskPartition {
  device: string
  mountpoint: string
  fstype: string
  opts: string
  total: number
  used: number
  free: number
  percent: number
}

export interface NetworkConnection {
  fd: number
  family: string
  type: string
  local_address?: string
  remote_address?: string
  status: string
  pid?: number
}

export interface DashboardResponse {
  system: SystemStatsResponse
  containers: {
    total_containers: number
    running: number
    stopped: number
    paused: number
    total_cpu_cores: number
    total_memory_bytes: number
    total_disk_bytes: number
  }
  resources: {
    cpu_cores: number
    total_memory: number
    total_disk: number
  }
  uptime: number
  timestamp: string
}

export interface SystemStatsHistoryResponse {
  stats: SystemStatsResponse[]
  period: string
  start_time: string
  end_time: string
  aggregate: boolean
}

export interface ContainerStatsHistoryResponse {
  container_id: string
  container_name?: string
  stats: ContainerStatsResponse[]
  period: string
  start_time: string
  end_time: string
  aggregate: boolean
}

export interface TopConsumersResponse {
  consumers: Array<{
    container_id: string
    name: string
    image: string
    avg_cpu: number
    max_cpu: number
    avg_memory: number
    max_memory: number
    total_network: number
    status: string
  }>
  metric: string
  limit: number
}

export interface CompareResponse {
  container_ids: string[]
  period: string
  metric: string
  data: Record<string, unknown>
  timestamp: string
}

export interface TrendsResponse {
  metric: string
  period: string
  trend: string
  change_percent: number
  data: Array<Record<string, unknown>>
  min_value?: Record<string, unknown>
  max_value?: Record<string, unknown>
}

export interface GroupStatsResponse {
  group_id: number
  group_name: string
  total_containers: number
  running_containers: number
  stopped_containers: number
  total_cpu_usage: number
  total_memory_usage: number
  containers: Array<{
    id: string
    name: string
    status: string
  }>
}

export interface PruneResponse {
  system_stats_deleted: number
  container_stats_deleted: number
  retention_days: number
}

export interface ExportResponse {
  format: string
  stats_type: string
  period: string
  exported_at: string
  data: unknown
  csv?: string
}

export interface DockerInfo {
  Version: string
  OperatingSystem: string
  OSType: string
  Architecture: string
  NCPU: number
  MemTotal: number
  Containers: number
  ContainersRunning: number
  ContainersPaused: number
  ContainersStopped: number
  Images: number
}

export interface DockerVersion {
  Version: string
  ApiVersion: string
  GoVersion: string
  GitCommit: string
  BuiltTime: string
}

export interface ComposeProject {
  project_name: string
  compose_file_path: string
  services: string[]
  status: string
}

export interface ComposeFileResponse {
  path: string
  content: string
  services: string[]
  networks: string[]
  volumes: string[]
}

export interface ComposeValidationResponse {
  valid: boolean
  errors: string[]
  warnings: string[]
}

export interface CreateGroupRequest {
  name: string
  description?: string
  color?: string
}

export interface UpdateGroupRequest {
  name?: string
  description?: string
  color?: string
}

export interface CreateUserRequest {
  username: string
  email: string
  password: string
  is_superuser?: boolean
}

export interface UpdateUserRequest {
  username?: string
  email?: string
  is_active?: boolean
  is_superuser?: boolean
}

export interface ChangePasswordRequest {
  current_password: string
  new_password: string
  new_password_confirm: string
}

export interface UserListResponse {
  users: User[]
  total: number
  page: number
  page_size: number
}

export interface UserDetailResponse extends User {
  last_login?: string
}

export interface Toast {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  duration?: number
}

export interface ApiError {
  detail?: string
  error?: string
  code?: string
}
