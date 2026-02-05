"""Updated schemas __init__.py with all schemas."""

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserPasswordUpdate,
    UserResponse,
    UserListResponse,
    UserLogin,
    TokenPayload,
    RefreshTokenRequest,
    LoginResponse,
    LogoutResponse,
    TokenRefreshResponse,
    CurrentUserResponse,
)

from app.schemas.response import (
    BaseResponse,
    DataResponse,
    PaginatedResponse,
    ResponseModel,
    TokenResponse,
    ErrorResponse,
    PaginationParams,
    ContainerStatus,
    OperationStatus,
    create_paginated_response,
)

from app.schemas.container import (
    ContainerBase,
    ContainerCreate,
    ContainerUpdate,
    ContainerResponse,
    ContainerDetailResponse,
    ContainerStatsResponse,
    ContainerLogsResponse,
    ContainerActionRequest,
    ContainerActionResponse,
    ContainerListResponse,
    ContainerGroupBase,
    ContainerGroupCreate,
    ContainerGroupUpdate,
    ContainerGroupResponse,
    ContainerGroupListResponse,
)

from app.schemas.stats import (
    SystemStatsResponse,
    SystemStatsHistoryResponse,
    DashboardStatsResponse,
    ContainerStatsHistoryResponse,
    ResourceUsageResponse,
)

from app.schemas.docker_compose import (
    DockerComposeProjectResponse,
    DockerComposePullResponse,
    DockerComposeServiceResponse,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserPasswordUpdate",
    "UserResponse",
    "UserListResponse",
    "UserLogin",
    "TokenPayload",
    "RefreshTokenRequest",
    "LoginResponse",
    "LogoutResponse",
    "TokenRefreshResponse",
    "CurrentUserResponse",
    # Response schemas
    "BaseResponse",
    "DataResponse",
    "PaginatedResponse",
    "ResponseModel",
    "TokenResponse",
    "ErrorResponse",
    "PaginationParams",
    "ContainerStatus",
    "OperationStatus",
    "create_paginated_response",
    # Container schemas
    "ContainerBase",
    "ContainerCreate",
    "ContainerUpdate",
    "ContainerResponse",
    "ContainerDetailResponse",
    "ContainerStatsResponse",
    "ContainerLogsResponse",
    "ContainerActionRequest",
    "ContainerActionResponse",
    "ContainerListResponse",
    "ContainerGroupBase",
    "ContainerGroupCreate",
    "ContainerGroupUpdate",
    "ContainerGroupResponse",
    "ContainerGroupListResponse",
    # Stats schemas
    "SystemStatsResponse",
    "SystemStatsHistoryResponse",
    "DashboardStatsResponse",
    "ContainerStatsHistoryResponse",
    "ResourceUsageResponse",
    # Docker Compose schemas
    "DockerComposeProjectResponse",
    "DockerComposePullResponse",
    "DockerComposeServiceResponse",
]
