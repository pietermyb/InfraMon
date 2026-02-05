"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    is_superuser: bool = False


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class ContainerGroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: str = "#3B82F6"


class ContainerGroupCreate(ContainerGroupBase):
    pass


class ContainerGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None


class ContainerGroupResponse(ContainerGroupBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ContainerBase(BaseModel):
    name: str
    image: str
    status: str = "unknown"
    group_id: Optional[int] = None


class ContainerResponse(ContainerBase):
    id: int
    container_id: str
    docker_compose_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    group: Optional[ContainerGroupResponse] = None
    
    class Config:
        from_attributes = True


class ContainerDetailResponse(ContainerResponse):
    ports: Optional[List[dict]] = None
    volumes: Optional[List[dict]] = None
    environment: Optional[List[dict]] = None
    networks: Optional[List[dict]] = None
    labels: Optional[dict] = None
    command: Optional[str] = None
    created: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    restart_policy: Optional[dict] = None
    healthcheck: Optional[dict] = None


class ContainerStatsResponse(BaseModel):
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


class SystemStatsResponse(BaseModel):
    id: int
    cpu_usage: float
    memory_usage: float
    memory_total: float
    disk_usage: float
    disk_total: float
    network_rx: float
    network_tx: float
    load_avg_1m: float
    load_avg_5m: float
    load_avg_15m: float
    uptime: float
    timestamp: datetime
    
    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    id: int
    container_id: Optional[int] = None
    user_id: Optional[int] = None
    operation: str
    details: Optional[Any] = None
    ip_address: Optional[str] = None
    success: int
    error_message: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


class DockerComposeProjectResponse(BaseModel):
    id: int
    project_name: str
    compose_file_path: str
    services: Optional[Any] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ActionResponse(BaseModel):
    success: bool
    message: str
    details: Optional[dict] = None


class ContainerActionRequest(BaseModel):
    timeout: int = 10
    force: bool = False


class ContainerLogsRequest(BaseModel):
    stdout: bool = True
    stderr: bool = True
    timestamps: bool = True
    since: Optional[str] = None
    until: Optional[str] = None
    tail: Optional[str] = "100"


class DockerComposePullRequest(BaseModel):
    no_cache: bool = False
    parallel: bool = True


class ContainerRenameRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class MessageResponse(BaseModel):
    message: str
