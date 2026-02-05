"""Docker Compose schemas for API requests and responses."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DockerComposeServiceResponse(BaseModel):
    """Docker Compose service response model."""

    name: str
    image: str
    replicas: int = 1
    ports: List[str] = []
    volumes: List[str] = []
    networks: List[str] = []
    status: str = "unknown"


class DockerComposeProjectResponse(BaseModel):
    """Docker Compose project response model."""

    id: int
    project_name: str
    compose_file_path: str
    services: Optional[List[DockerComposeServiceResponse]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DockerComposePullResponse(BaseModel):
    """Docker Compose pull response model."""

    success: bool
    message: str
    project_name: str
    images_updated: List[str] = []
    images_skipped: List[str] = []
    errors: List[str] = []


class DockerComposePullRequest(BaseModel):
    """Docker Compose pull request model."""

    no_cache: bool = False
    parallel: bool = True


class DockerComposeUpResponse(BaseModel):
    """Docker Compose up response model."""

    success: bool
    message: str
    project_name: str
    services_started: List[str] = []
    services_recreated: List[str] = []
    errors: List[str] = []


class DockerComposeUpRequest(BaseModel):
    """Docker Compose up request model."""

    detach: bool = True
    rebuild: bool = False
    remove_orphans: bool = False


class DockerComposeDownResponse(BaseModel):
    """Docker Compose down response model."""

    success: bool
    message: str
    project_name: str
    services_removed: List[str] = []


class DockerComposeLogsResponse(BaseModel):
    """Docker Compose logs response model."""

    project_name: str
    logs: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DockerComposeValidationResponse(BaseModel):
    """Docker Compose validation response model."""

    valid: bool
    errors: List[str] = []
    warnings: List[str] = []


class DockerComposeFileContent(BaseModel):
    """Docker Compose file content response model."""

    path: str
    content: str
    services: List[str] = []
    networks: List[str] = []
    volumes: List[str] = []


class DockerComposeRestartRequest(BaseModel):
    """Docker Compose restart request model."""

    timeout: int = Field(10, ge=1, le=300)


class DockerComposeRestartResponse(BaseModel):
    """Docker Compose restart response model."""

    success: bool
    message: str
    project_name: str
    services_restarted: List[str] = []
    errors: List[str] = []
