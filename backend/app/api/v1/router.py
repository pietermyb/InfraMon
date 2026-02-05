"""API router with all endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import asyncio
import json

from app.db.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, LoginRequest
from app.schemas.container import (
    ContainerResponse, ContainerDetailResponse, ContainerLogsResponse,
    ContainerActionRequest, ContainerActionResponse, ContainerListResponse,
    ContainerGroupResponse, ContainerGroupCreate, ContainerGroupUpdate,
    ContainerBulkActionRequest, ContainerBulkActionResponse,
)
from app.schemas.stats import (
    SystemStatsResponse, DashboardStatsResponse,
)
from app.services.docker_service import DockerService
from app.services.container_service import ContainerService
from app.services.stats_service import StatsService

api_router = APIRouter()


@api_router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


@api_router.post("/auth/login", response_model=dict, tags=["Authentication"])
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """User login endpoint."""
    from app.core.auth import verify_password, create_access_token, create_refresh_token
    from sqlalchemy import select
    
    result = await db.execute(
        select(User).where(User.username == request.username)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive",
        )
    
    access_token = create_access_token(data={"sub": user.username, "user_id": user.id})
    refresh_token = create_refresh_token(data={"sub": user.username, "user_id": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user).model_dump(),
    }


@api_router.get("/auth/me", response_model=UserResponse, tags=["Authentication"])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user."""
    return UserResponse.model_validate(current_user)


@api_router.get("/containers", response_model=ContainerListResponse, tags=["Containers"])
async def list_containers(
    all_containers: bool = Query(False, description="Include stopped containers"),
    group_id: Optional[int] = Query(None, description="Filter by group"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all containers."""
    docker_service = DockerService(db)
    containers = await docker_service.list_containers(all_containers)
    
    running = sum(1 for c in containers if c.get("status") == "running")
    
    return ContainerListResponse(
        containers=containers,
        total=len(containers),
        running=running,
        stopped=len(containers) - running,
    )


@api_router.get("/containers/{container_id}", response_model=ContainerDetailResponse, tags=["Containers"])
async def get_container(
    container_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get container details."""
    docker_service = DockerService(db)
    container = await docker_service.inspect_container(container_id)
    
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container '{container_id}' not found",
        )
    
    return container


@api_router.post("/containers/{container_id}/start", response_model=ContainerActionResponse, tags=["Containers"])
async def start_container(
    container_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start a container."""
    docker_service = DockerService(db)
    success = await docker_service.start_container(container_id)
    
    return ContainerActionResponse(
        success=success,
        message="Container started successfully" if success else "Failed to start container",
        container_id=container_id,
    )


@api_router.post("/containers/{container_id}/stop", response_model=ContainerActionResponse, tags=["Containers"])
async def stop_container(
    container_id: str,
    timeout: int = Query(10, ge=1, le=300),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Stop a container."""
    docker_service = DockerService(db)
    success = await docker_service.stop_container(container_id, timeout)
    
    return ContainerActionResponse(
        success=success,
        message="Container stopped successfully" if success else "Failed to stop container",
        container_id=container_id,
    )


@api_router.post("/containers/{container_id}/restart", response_model=ContainerActionResponse, tags=["Containers"])
async def restart_container(
    container_id: str,
    timeout: int = Query(10, ge=1, le=300),
    force: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Restart a container."""
    docker_service = DockerService(db)
    success = await docker_service.restart_container(container_id, timeout, force)
    
    return ContainerActionResponse(
        success=success,
        message="Container restarted successfully" if success else "Failed to restart container",
        container_id=container_id,
    )


@api_router.delete("/containers/{container_id}", response_model=ContainerActionResponse, tags=["Containers"])
async def remove_container(
    container_id: str,
    force: bool = Query(False),
    volumes: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a container."""
    docker_service = DockerService(db)
    success = await docker_service.remove_container(container_id, force, volumes)
    
    return ContainerActionResponse(
        success=success,
        message="Container removed successfully" if success else "Failed to remove container",
        container_id=container_id,
    )


@api_router.get("/containers/{container_id}/logs", tags=["Containers"])
async def get_container_logs(
    container_id: str,
    stdout: bool = Query(True),
    stderr: bool = Query(True),
    timestamps: bool = Query(True),
    tail: str = Query("100"),
    since: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get container logs."""
    docker_service = DockerService(db)
    logs_data = await docker_service.get_logs(
        container_id,
        stdout=stdout,
        stderr=stderr,
        timestamps=timestamps,
        tail=tail,
        since=since,
    )
    
    return logs_data


@api_router.get("/containers/{container_id}/stats", tags=["Containers"])
async def get_container_stats(
    container_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get container stats."""
    docker_service = DockerService(db)
    stats = await docker_service.get_container_stats(container_id)
    return stats


@api_router.get("/containers/{container_id}/inspect", tags=["Containers"])
async def inspect_container(
    container_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get full container inspection."""
    docker_service = DockerService(db)
    return await docker_service.get_full_inspection(container_id)


@api_router.get("/containers/{container_id}/compose", tags=["Containers"])
async def get_container_compose(
    container_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get docker-compose info for container."""
    docker_service = DockerService(db)
    return await docker_service.get_compose_info(container_id)


@api_router.post("/containers/{container_id}/compose/pull", response_model=ContainerActionResponse, tags=["Containers"])
async def pull_container_image(
    container_id: str,
    no_cache: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Pull latest image for container."""
    docker_service = DockerService(db)
    success = await docker_service.pull_image(container_id, no_cache)
    
    return ContainerActionResponse(
        success=success,
        message="Image pulled successfully" if success else "Failed to pull image",
        container_id=container_id,
    )


@api_router.get("/groups", response_model=list[ContainerGroupResponse], tags=["Container Groups"])
async def list_groups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List container groups."""
    container_service = ContainerService(db)
    return await container_service.list_groups()


@api_router.post("/groups", response_model=ContainerGroupResponse, tags=["Container Groups"])
async def create_group(
    group: ContainerGroupCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create container group."""
    container_service = ContainerService(db)
    return await container_service.create_group(group)


@api_router.put("/groups/{group_id}", response_model=ContainerGroupResponse, tags=["Container Groups"])
async def update_group(
    group_id: int,
    group: ContainerGroupUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update container group."""
    container_service = ContainerService(db)
    result = await container_service.update_group(group_id, group)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found",
        )
    
    return result


@api_router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Container Groups"])
async def delete_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete container group."""
    container_service = ContainerService(db)
    success = await container_service.delete_group(group_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found",
        )


@api_router.get("/stats/system", response_model=SystemStatsResponse, tags=["Statistics"])
async def get_system_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current system stats."""
    stats_service = StatsService(db)
    return await stats_service.get_current_system_stats()


@api_router.get("/stats/dashboard", response_model=DashboardStatsResponse, tags=["Statistics"])
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard summary stats."""
    stats_service = StatsService(db)
    return await stats_service.get_dashboard_summary()


@api_router.get("/compose/projects", tags=["Docker Compose"])
async def list_compose_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List docker-compose projects."""
    docker_service = DockerService(db)
    return await docker_service.list_compose_projects()


@api_router.post("/containers/bulk-action", response_model=ContainerBulkActionResponse, tags=["Containers"])
async def bulk_container_action(
    request: ContainerBulkActionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Perform bulk action on containers."""
    docker_service = DockerService(db)
    results = []
    succeeded = 0
    failed = 0
    
    for container_id in request.container_ids:
        success = False
        if request.action == "start":
            success = await docker_service.start_container(container_id)
        elif request.action == "stop":
            success = await docker_service.stop_container(container_id, request.timeout)
        elif request.action == "restart":
            success = await docker_service.restart_container(container_id, request.timeout, request.force)
        elif request.action == "remove":
            success = await docker_service.remove_container(container_id, request.force, request.volumes)
        
        result = ContainerActionResponse(
            success=success,
            message=f"Container {request.action} successful" if success else f"Container {request.action} failed",
            container_id=container_id,
        )
        results.append(result)
        
        if success:
            succeeded += 1
        else:
            failed += 1
    
    return ContainerBulkActionResponse(
        success=failed == 0,
        message=f"Processed {len(request.container_ids)} containers",
        total=len(request.container_ids),
        succeeded=succeeded,
        failed=failed,
        results=results,
    )
