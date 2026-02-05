"""Statistics schemas for API requests and responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SystemStatsResponse(BaseModel):
    """System statistics response model."""

    id: int
    cpu_usage: float = Field(0.0, ge=0, le=100, description="CPU usage percentage")
    cpu_cores: int = 0
    cpu_frequency: float = 0.0
    memory_usage: float = Field(0.0, ge=0, le=100, description="Memory usage percentage")
    memory_total: float = Field(0.0, description="Total memory in bytes")
    memory_used: float = Field(0.0, description="Used memory in bytes")
    memory_available: float = Field(0.0, description="Available memory in bytes")
    swap_usage: float = Field(0.0, description="Swap usage in bytes")
    swap_total: float = Field(0.0, description="Total swap in bytes")
    disk_usage: float = Field(0.0, ge=0, le=100, description="Disk usage percentage")
    disk_total: float = Field(0.0, description="Total disk space in bytes")
    disk_used: float = Field(0.0, description="Used disk space in bytes")
    disk_free: float = Field(0.0, description="Free disk space in bytes")
    disk_read_bytes: float = Field(0.0, description="Disk read bytes")
    disk_write_bytes: float = Field(0.0, description="Disk write bytes")
    network_rx: float = Field(0.0, description="Network receive bytes")
    network_tx: float = Field(0.0, description="Network transmit bytes")
    network_interfaces: List[Dict[str, Any]] = Field(default_factory=list)
    load_avg_1m: float = Field(0.0, description="Load average (1 minute)")
    load_avg_5m: float = Field(0.0, description="Load average (5 minutes)")
    load_avg_15m: float = Field(0.0, description="Load average (15 minutes)")
    load_percent: float = Field(0.0, description="Load percentage")
    uptime: float = Field(0.0, description="System uptime in seconds")
    boot_time: Optional[str] = None
    temperatures: Dict[str, float] = Field(default_factory=dict)
    timestamp: datetime

    class Config:
        from_attributes = True


class SystemInfoResponse(BaseModel):
    """System information response model."""

    hostname: str
    system: str
    release: str
    version: str
    machine: str
    boot_time: str
    uptime: float
    cpu_architecture: str
    kernel_version: str
    connected_users: List[Dict[str, Any]] = Field(default_factory=list)
    python_version: str


class DiskPartitionResponse(BaseModel):
    """Disk partition response model."""

    device: str
    mountpoint: str
    fstype: str
    opts: str
    total: float
    used: float
    free: float
    percent: float


class NetworkInterfaceResponse(BaseModel):
    """Network interface response model."""

    interface: str
    bytes_sent: float
    bytes_recv: float
    packets_sent: int
    packets_recv: int
    errin: int
    errout: int
    dropin: int
    dropout: int


class NetworkConnectionResponse(BaseModel):
    """Network connection response model."""

    fd: int
    family: str
    type: str
    local_address: Optional[str] = None
    remote_address: Optional[str] = None
    status: str
    pid: Optional[int] = None


class ProcessResponse(BaseModel):
    """Process response model."""

    pid: int
    name: str
    username: Optional[str] = None
    cmdline: Optional[str] = None
    cpu_percent: float = 0.0
    memory_percent: float = 0.0


class ContainerProcessResponse(BaseModel):
    """Container process response model."""

    processes: List[Dict[str, Any]] = Field(default_factory=list)
    container_id: str


class ContainerFilesystemResponse(BaseModel):
    """Container filesystem usage response model."""

    mount_point: str
    source: Optional[str] = None
    type: Optional[str] = None
    total: Optional[float] = None
    used: Optional[float] = None
    free: Optional[float] = None
    percent: Optional[float] = None


class SystemStatsHistoryResponse(BaseModel):
    """System stats history response model."""

    stats: List[Dict[str, Any]]
    period: str
    start_time: datetime
    end_time: datetime
    aggregate: bool = False


class ContainerStatsHistoryResponse(BaseModel):
    """Container stats history response model."""

    container_id: str
    container_name: Optional[str] = None
    stats: List[Dict[str, Any]]
    period: str
    start_time: datetime
    end_time: datetime
    aggregate: bool = False


class AggregatedStatsResponse(BaseModel):
    """Aggregated stats response model."""

    timestamp: datetime
    cpu_usage_avg: float
    cpu_usage_max: float
    cpu_usage_min: float
    memory_usage_avg: float
    memory_usage_max: float
    memory_usage_min: float
    network_rx: float
    network_tx: float
    disk_usage: float = 0.0
    load_avg_1m: float = 0.0


class ResourceUsageResponse(BaseModel):
    """Resource usage summary."""

    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_rx: float = 0.0
    network_tx: float = 0.0
    container_count: int = 0
    running_containers: int = 0
    stopped_containers: int = 0


class TopConsumersResponse(BaseModel):
    """Top resource consumers response model."""

    consumers: List[Dict[str, Any]] = Field(default_factory=list)
    metric: str
    limit: int


class ContainerComparisonResponse(BaseModel):
    """Container comparison response model."""

    container_ids: List[str]
    period: str
    metric: str
    data: Dict[str, Any]
    timestamp: datetime


class ResourceTrendsResponse(BaseModel):
    """Resource trends response model."""

    metric: str
    period: str
    trend: str
    change_percent: float
    data: List[Dict[str, Any]]
    min_value: Optional[Dict[str, Any]] = None
    max_value: Optional[Dict[str, Any]] = None


class PruneStatsResponse(BaseModel):
    """Prune stats response model."""

    system_stats_deleted: int
    container_stats_deleted: int
    retention_days: int


class ExportStatsResponse(BaseModel):
    """Export stats response model."""

    format: str
    stats_type: str
    period: str
    exported_at: datetime
    data: Any
    csv: Optional[str] = None


class ContainerGroupStatsResponse(BaseModel):
    """Container group stats response model."""

    group_id: int
    group_name: str
    total_containers: int
    running_containers: int
    stopped_containers: int
    total_cpu_usage: float
    total_memory_usage: float
    containers: List[Dict[str, Any]]


class StatsQueryParams(BaseModel):
    """Stats query parameters."""

    period: str = Field("1h", pattern="^(1h|6h|24h|7d|30d)$")
    interval: str = Field("1m", pattern="^(1m|5m|15m|30m|1h)$")
    aggregate: bool = False
    container_id: Optional[str] = None


class ResourceComparisonResponse(BaseModel):
    """Resource comparison between containers."""

    containers: List[Dict[str, Any]]
    metrics: List[str]
    timestamp: datetime


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics summary."""

    system: SystemStatsResponse
    containers: Dict[str, Any] = Field(
        default_factory=lambda: {
            "total_containers": 0,
            "running": 0,
            "stopped": 0,
            "paused": 0,
            "total_cpu_cores": 0,
            "total_memory_bytes": 0,
            "total_disk_bytes": 0,
        }
    )
    resources: Dict[str, float] = Field(
        default_factory=lambda: {"cpu_cores": 0, "total_memory": 0, "total_disk": 0}
    )
    uptime: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
