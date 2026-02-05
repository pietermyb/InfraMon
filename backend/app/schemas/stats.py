"""Statistics schemas for API requests and responses."""

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class SystemStatsResponse(BaseModel):
    """System statistics response model."""
    
    id: int
    cpu_usage: float = Field(0.0, ge=0, le=100, description="CPU usage percentage")
    memory_usage: float = Field(0.0, ge=0, le=100, description="Memory usage percentage")
    memory_total: float = Field(0.0, description="Total memory in bytes")
    disk_usage: float = Field(0.0, ge=0, le=100, description="Disk usage percentage")
    disk_total: float = Field(0.0, description="Total disk space in bytes")
    network_rx: float = Field(0.0, description="Network receive bytes")
    network_tx: float = Field(0.0, description="Network transmit bytes")
    load_avg_1m: float = Field(0.0, description="Load average (1 minute)")
    load_avg_5m: float = Field(0.0, description="Load average (5 minutes)")
    load_avg_15m: float = Field(0.0, description="Load average (15 minutes)")
    uptime: float = Field(0.0, description="System uptime in seconds")
    timestamp: datetime
    
    class Config:
        from_attributes = True


class SystemStatsHistoryResponse(BaseModel):
    """System stats history response model."""
    
    stats: List[SystemStatsResponse]
    period: str
    start_time: datetime
    end_time: datetime


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics summary."""
    
    system: SystemStatsResponse
    containers: Dict[str, int] = Field(
        default_factory=lambda: {"total": 0, "running": 0, "stopped": 0, "paused": 0}
    )
    resources: Dict[str, float] = Field(
        default_factory=lambda: {"cpu_cores": 0, "total_memory": 0, "total_disk": 0}
    )
    uptime: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ContainerStatsHistoryResponse(BaseModel):
    """Container stats history response model."""
    
    container_id: str
    container_name: str
    stats: List[ContainerStatsResponse]
    period: str
    start_time: datetime
    end_time: datetime


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
    
    by_cpu: List[Dict[str, Any]] = []
    by_memory: List[Dict[str, Any]] = []
    by_disk: List[Dict[str, Any]] = []
    by_network: List[Dict[str, Any]] = []


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
