"""Container schemas for API requests and responses."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ContainerBase(BaseModel):
    """Base container model."""
    
    name: str
    image: str
    status: str = "unknown"
    group_id: Optional[int] = None


class ContainerCreate(ContainerBase):
    """Container creation model (for tracking existing containers)."""
    
    container_id: str = Field(..., description="Docker container ID")


class ContainerUpdate(BaseModel):
    """Container update model."""
    
    group_id: Optional[int] = None
    name: Optional[str] = None


class ContainerUpdateRequest(BaseModel):
    """Container resource update request model."""
    
    memory_limit: Optional[int] = Field(None, ge=0, description="Memory limit in bytes")
    cpu_shares: Optional[int] = Field(None, ge=0, le=1024, description="CPU shares")


class ContainerRenameRequest(BaseModel):
    """Container rename request model."""
    
    new_name: str = Field(..., min_length=1, max_length=128, pattern="^[a-zA-Z0-9][a-zA-Z0-9_.-]*$")


class ContainerExecRequest(BaseModel):
    """Container exec request model."""
    
    cmd: List[str] = Field(..., min_length=1, description="Command to execute")
    working_dir: Optional[str] = None
    user: Optional[str] = None
    environment: Optional[Dict[str, str]] = None


class ContainerExecResponse(BaseModel):
    """Container exec response model."""
    
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None


class ContainerShellInitResponse(BaseModel):
    """Container shell initialization response model."""
    
    success: bool
    exec_id: Optional[str] = None
    error: Optional[str] = None


class ContainerResizeRequest(BaseModel):
    """Container terminal resize request model."""
    
    height: int = Field(24, ge=1, le=200)
    width: int = Field(80, ge=1, le=500)


class ContainerDiffItem(BaseModel):
    """Container diff item model."""
    
    path: str
    kind: str
    change: Optional[str] = None


class ContainerDiffResponse(BaseModel):
    """Container diff response model."""
    
    container_id: str
    changes: List[ContainerDiffItem]


class ContainerPruneResponse(BaseModel):
    """Container prune response model."""
    
    success: bool
    deleted_containers: List[str]
    space_reclaimed: int


class ContainerLogsStreamResponse(BaseModel):
    """Container logs streaming response model."""
    
    container_id: str
    log_line: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ContainerStatsStreamResponse(BaseModel):
    """Container stats streaming response model."""
    
    container_id: str
    cpu_usage: float
    memory_usage: float
    memory_percent: float
    network_rx: float
    network_tx: float
    pids: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ContainerResponse(BaseModel):
    """Container response model."""
    
    id: int
    container_id: str
    name: str
    image: str
    status: str
    group_id: Optional[int] = None
    docker_compose_path: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class ContainerDetailResponse(ContainerResponse):
    """Detailed container response model."""
    
    ports: Optional[Dict[str, Any]] = None
    volumes: Optional[List[Dict[str, Any]]] = None
    environment: Optional[List[Dict[str, str]]] = None
    networks: Optional[List[str]] = None
    labels: Optional[Dict[str, Any]] = None
    command: Optional[List[str]] = None
    created: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    restart_policy: Optional[Dict[str, Any]] = None
    healthcheck: Optional[Dict[str, Any]] = None
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    gateway: Optional[str] = None
    mac_address: Optional[str] = None
    memory_limit: Optional[int] = None
    memory_swap: Optional[int] = None
    cpu_shares: Optional[int] = None
    cpu_period: Optional[int] = None
    cpu_quota: Optional[int] = None
    working_dir: Optional[str] = None
    entrypoint: Optional[List[str]] = None
    user: Optional[str] = None
    tty: Optional[bool] = None
    open_stdin: Optional[bool] = None
    restart_count: Optional[int] = None
    OOMKilled: Optional[bool] = None
    exit_code: Optional[int] = None


class ContainerStatsResponse(BaseModel):
    """Container stats response model."""
    
    id: int
    container_id: int
    cpu_usage: float
    memory_usage: float
    memory_limit: float
    network_rx: float
    network_tx: float
    block_read: float
    block_write: float
    pids: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


class ContainerLogsResponse(BaseModel):
    """Container logs response model."""
    
    container_id: str
    logs: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ContainerActionRequest(BaseModel):
    """Container action request model."""
    
    timeout: int = Field(10, ge=1, le=300, description="Timeout in seconds")
    force: bool = False
    no_cache: bool = False
    parallel: bool = True


class ContainerActionResponse(BaseModel):
    """Container action response model."""
    
    success: bool
    message: str
    container_id: str
    details: Optional[Dict[str, Any]] = None


class ContainerListResponse(BaseModel):
    """Container list response with pagination."""
    
    containers: List[ContainerResponse]
    total: int
    running: int
    stopped: int


class ContainerGroupBase(BaseModel):
    """Base container group model."""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: str = "#3B82F6"


class ContainerGroupCreate(ContainerGroupBase):
    """Container group creation model."""
    pass


class ContainerGroupUpdate(BaseModel):
    """Container group update model."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = None


class ContainerGroupResponse(ContainerGroupBase):
    """Container group response model."""
    
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ContainerGroupDetailResponse(ContainerGroupResponse):
    """Container group with containers response model."""
    
    containers: List[ContainerResponse] = []


class ContainerGroupListResponse(BaseModel):
    """Container group list response."""
    
    groups: List[ContainerGroupResponse]
    total: int


class ContainerBulkActionRequest(BaseModel):
    """Bulk container action request model."""
    
    container_ids: List[str]
    action: str = Field(..., pattern="^(start|stop|restart|pause|unpause|remove)$")
    timeout: int = Field(10, ge=1, le=300)
    force: bool = False
    volumes: bool = False


class ContainerBulkActionResponse(BaseModel):
    """Bulk container action response model."""
    
    success: bool
    message: str
    total: int
    succeeded: int
    failed: int
    results: List[ContainerActionResponse]
