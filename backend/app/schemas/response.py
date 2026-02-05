"""API response models and utilities."""

from datetime import datetime
from enum import Enum
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class BaseResponse(BaseModel):
    """Base API response model."""

    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DataResponse(BaseResponse):
    """Response with data payload."""

    data: Any = None


class PaginatedResponse(BaseResponse):
    """Paginated response model."""

    data: List[Any] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        return self.page > 1


T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """Generic response model."""

    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    errors: Optional[List[str]] = None
    metadata: Optional[dict] = None


class TokenResponse(BaseModel):
    """Token response model."""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = 1800
    user: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Error response model."""

    success: bool = False
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class PaginationParams:
    """Pagination parameters."""

    def __init__(
        self,
        page: int = Field(1, ge=1),
        page_size: int = Field(20, ge=1, le=100),
        order_by: Optional[str] = None,
        order: str = Field("desc", pattern="^(asc|desc)$"),
    ):
        self.page = page
        self.page_size = page_size
        self.order_by = order_by
        self.order = order

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


def create_paginated_response(
    data: List[Any],
    total: int,
    page: int,
    page_size: int,
    message: Optional[str] = None,
) -> PaginatedResponse:
    """Create a paginated response."""
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedResponse(
        data=data,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        message=message,
    )


class ContainerStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    CREATED = "created"
    RESTARTING = "restarting"
    REMOVING = "removing"
    UNKNOWN = "unknown"


class OperationStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
