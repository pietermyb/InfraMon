"""API router with all endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
import asyncio
import json
import base64
from datetime import datetime, timedelta

from app.db.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserLogin, UserPasswordUpdate
from app.schemas.response import DataResponse
from app.schemas.container import (
    ContainerResponse, ContainerDetailResponse, ContainerLogsResponse,
    ContainerActionRequest, ContainerActionResponse, ContainerListResponse,
    ContainerGroupResponse, ContainerGroupCreate, ContainerGroupUpdate,
    ContainerBulkActionRequest, ContainerBulkActionResponse,
    ContainerUpdateRequest, ContainerRenameRequest, ContainerExecRequest,
    ContainerExecResponse, ContainerShellInitResponse, ContainerResizeRequest,
    ContainerDiffResponse, ContainerPruneResponse,
)
from app.schemas.stats import (
    SystemStatsResponse, DashboardStatsResponse, SystemInfoResponse,
    DiskPartitionResponse, NetworkInterfaceResponse, NetworkConnectionResponse,
    ProcessResponse, ContainerFilesystemResponse, SystemStatsHistoryResponse,
    ContainerStatsHistoryResponse, AggregatedStatsResponse, ResourceUsageResponse,
    TopConsumersResponse, ContainerComparisonResponse, ResourceTrendsResponse,
    PruneStatsResponse, ExportStatsResponse, ContainerGroupStatsResponse,
)
from app.schemas.docker_compose import (
    DockerComposeFileContent, DockerComposeValidationResponse,
)
from app.services.docker_service import DockerService
from app.services.container_service import ContainerService
from app.services.stats_service import StatsService

api_router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
    
    async def connect(self, websocket: WebSocket, key: str):
        await websocket.accept()
        self.active_connections[key] = websocket
    
    def disconnect(self, key: str):
        if key in self.active_connections:
            del self.active_connections[key]
    
    async def send_message(self, key: str, message: str):
        if key in self.active_connections:
            try:
                await self.active_connections[key].send_text(message)
            except Exception:
                self.disconnect(key)
    
    async def send_bytes(self, key: str, data: bytes):
        if key in self.active_connections:
            try:
                await self.active_connections[key].send_bytes(data)
            except Exception:
                self.disconnect(key)

manager = ConnectionManager()


@api_router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


@api_router.post("/auth/login", response_model=dict, tags=["Authentication"])
async def login(request: UserLogin, db: AsyncSession = Depends(get_db)):
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


@api_router.post("/auth/change-password", response_model=dict, tags=["Authentication"])
async def change_password(
    password_data: UserPasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change current user password."""
    from app.core.auth import verify_password, get_password_hash
    
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )
    
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    
    db.add(current_user)
    await db.commit()
    
    return {"message": "Password updated successfully"}


@api_router.get("/containers", response_model=DataResponse, tags=["Containers"])
async def list_containers(
    all_containers: bool = Query(False, description="Include stopped containers"),
    group_id: Optional[int] = Query(None, description="Filter by group"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all containers."""
    docker_service = DockerService(db)
    containers = await docker_service.list_all_containers(all_containers)
    
    running = sum(1 for c in containers if c.get("status") == "running")
    
    return DataResponse(
        success=True,
        data={
            "containers": containers,
            "total": len(containers),
            "running": running,
            "stopped": len(containers) - running,
        }
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


@api_router.get("/containers/{container_id}/compose/info", tags=["Containers", "Docker Compose"])
async def get_container_compose_info(
    container_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get docker-compose info for container."""
    docker_service = DockerService(db)
    return await docker_service.get_compose_info(container_id)


@api_router.get("/containers/{container_id}/compose/file", response_model=DockerComposeFileContent, tags=["Containers", "Docker Compose"])
async def get_container_compose_file(
    container_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get docker-compose file content for a container."""
    docker_service = DockerService(db)
    # First get the compose info to find the path
    info = await docker_service.get_compose_info(container_id)
    if not info.get("compose_file_path"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No compose file found for this container",
        )
    
    # Then get the content
    success, result = await docker_service.get_compose_file_content(info["compose_file_path"])
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result,
        )
    
    return result


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


@api_router.get("/stats/system/info", response_model=SystemInfoResponse, tags=["Statistics"])
async def get_system_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed system information."""
    stats_service = StatsService(db)
    return await stats_service.get_system_info()


@api_router.get("/stats/system/disk", response_model=list[DiskPartitionResponse], tags=["Statistics"])
async def get_disk_partitions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get disk partition information."""
    stats_service = StatsService(db)
    return await stats_service.get_disk_partitions()


@api_router.get("/stats/system/network", response_model=list[NetworkInterfaceResponse], tags=["Statistics"])
async def get_network_interfaces(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get network interface statistics."""
    stats_service = StatsService(db)
    stats = await stats_service.get_current_system_stats()
    return stats.get("network_interfaces", [])


@api_router.get("/stats/system/connections", response_model=list[NetworkConnectionResponse], tags=["Statistics"])
async def get_network_connections(
    kind: str = Query("inet", description="Connection type: inet, inet6, tcp, tcp4, udp, udp4, etc."),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get network connections."""
    stats_service = StatsService(db)
    return await stats_service.get_network_connections(kind)


@api_router.get("/stats/system/processes", response_model=list[ProcessResponse], tags=["Statistics"])
async def get_process_list(
    limit: int = Query(20, ge=1, le=100),
    order_by: str = Query("cpu", pattern="^(cpu|memory|pid)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get system process list."""
    stats_service = StatsService(db)
    return await stats_service.get_process_list(limit=limit, order_by=order_by)


@api_router.get("/stats/system/history", response_model=SystemStatsHistoryResponse, tags=["Statistics"])
async def get_system_stats_history(
    period: str = Query("1h", pattern="^(1h|6h|24h|7d|30d)$"),
    aggregate: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get historical system stats."""
    stats_service = StatsService(db)
    now = datetime.utcnow()
    
    periods = {"1h": timedelta(hours=1), "6h": timedelta(hours=6), "24h": timedelta(hours=24), "7d": timedelta(days=7), "30d": timedelta(days=30)}
    delta = periods.get(period, timedelta(hours=1))
    start_time = now - delta
    
    stats = await stats_service.get_system_stats_history(period=period, aggregate=aggregate)
    
    return {
        "stats": stats,
        "period": period,
        "start_time": start_time,
        "end_time": now,
        "aggregate": aggregate,
    }


@api_router.get("/stats/containers/{container_id}/processes", response_model=list[Dict[str, Any]], tags=["Statistics"])
async def get_container_processes(
    container_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get processes running inside a container."""
    stats_service = StatsService(db)
    return await stats_service.get_container_processes(container_id)


@api_router.get("/stats/containers/{container_id}/filesystem", response_model=list[ContainerFilesystemResponse], tags=["Statistics"])
async def get_container_filesystem_usage(
    container_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get filesystem usage for a container."""
    stats_service = StatsService(db)
    return await stats_service.get_container_filesystem_usage(container_id)


@api_router.get("/containers/{container_id}/stats/history", response_model=ContainerStatsHistoryResponse, tags=["Statistics"])
async def get_container_stats_history(
    container_id: str,
    period: str = Query("1h", pattern="^(1h|6h|24h|7d|30d)$"),
    aggregate: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get historical container stats."""
    stats_service = StatsService(db)
    now = datetime.utcnow()
    
    periods = {"1h": timedelta(hours=1), "6h": timedelta(hours=6), "24h": timedelta(hours=24), "7d": timedelta(days=7), "30d": timedelta(days=30)}
    delta = periods.get(period, timedelta(hours=1))
    start_time = now - delta
    
    stats = await stats_service.get_container_stats_history(container_id, period=period, aggregate=aggregate)
    
    return {
        "container_id": container_id,
        "container_name": None,
        "stats": stats,
        "period": period,
        "start_time": start_time,
        "end_time": now,
        "aggregate": aggregate,
    }


@api_router.get("/stats/top-consumers", response_model=TopConsumersResponse, tags=["Statistics"])
async def get_top_consumers(
    metric: str = Query("cpu", pattern="^(cpu|memory|network)$"),
    limit: int = Query(10, ge=1, le=50),
    period: str = Query("1h", pattern="^(1h|6h|24h|7d|30d)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get top resource consuming containers."""
    stats_service = StatsService(db)
    consumers = await stats_service.get_top_consumers(metric=metric, limit=limit, period=period)
    
    return {
        "consumers": consumers,
        "metric": metric,
        "limit": limit,
    }


@api_router.get("/stats/compare", response_model=ContainerComparisonResponse, tags=["Statistics"])
async def compare_containers(
    container_ids: List[str] = Query(..., description="Container IDs to compare"),
    metric: str = Query("cpu", pattern="^(cpu|memory|network)$"),
    period: str = Query("1h", pattern="^(1h|6h|24h|7d|30d)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Compare resource usage between containers."""
    stats_service = StatsService(db)
    return await stats_service.compare_containers(container_ids, metric=metric, period=period)


@api_router.get("/stats/trends", response_model=ResourceTrendsResponse, tags=["Statistics"])
async def get_resource_trends(
    metric: str = Query("cpu", pattern="^(cpu|memory|disk|network)$"),
    period: str = Query("7d", pattern="^(1h|6h|24h|7d|30d)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get resource usage trends."""
    stats_service = StatsService(db)
    return await stats_service.get_resource_trends(metric=metric, period=period)


@api_router.post("/stats/prune", response_model=PruneStatsResponse, tags=["Statistics"])
async def prune_stats(
    retention_days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove old statistics data."""
    stats_service = StatsService(db)
    return await stats_service.prune_old_stats(retention_days=retention_days)


@api_router.get("/stats/export", tags=["Statistics"])
async def export_stats(
    stats_type: str = Query("system", pattern="^(system|container)$"),
    period: str = Query("24h", pattern="^(1h|6h|24h|7d|30d)$"),
    format: str = Query("json", pattern="^(json|csv)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export statistics data."""
    stats_service = StatsService(db)
    return await stats_service.export_stats(stats_type=stats_type, period=period, format=format)


@api_router.get("/stats/groups/{group_id}", response_model=ContainerGroupStatsResponse, tags=["Statistics"])
async def get_group_stats(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get statistics for a container group."""
    stats_service = StatsService(db)
    return await stats_service.get_container_group_stats(group_id)


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
    docker_service = DockerService(db, user_id=current_user.id)
    results = []
    succeeded = 0
    failed = 0
    
    for container_id in request.container_ids:
        success = False
        message = ""
        if request.action == "start":
            success, message = await docker_service.start_container(container_id)
        elif request.action == "stop":
            success, message = await docker_service.stop_container(container_id, request.timeout)
        elif request.action == "restart":
            success, message = await docker_service.restart_container(container_id, request.timeout, request.force)
        elif request.action == "pause":
            success, message = await docker_service.pause_container(container_id)
        elif request.action == "unpause":
            success, message = await docker_service.unpause_container(container_id)
        elif request.action == "remove":
            success, message = await docker_service.remove_container(container_id, request.force, request.volumes)
        
        result = ContainerActionResponse(
            success=success,
            message=message or f"Container {request.action} successful" if success else f"Container {request.action} failed",
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


@api_router.post("/containers/{container_id}/pause", response_model=ContainerActionResponse, tags=["Containers"])
async def pause_container(
    container_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Pause a container."""
    docker_service = DockerService(db, user_id=current_user.id)
    success, message = await docker_service.pause_container(container_id)
    
    return ContainerActionResponse(
        success=success,
        message=message,
        container_id=container_id,
    )


@api_router.post("/containers/{container_id}/unpause", response_model=ContainerActionResponse, tags=["Containers"])
async def unpause_container(
    container_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Unpause a container."""
    docker_service = DockerService(db, user_id=current_user.id)
    success, message = await docker_service.unpause_container(container_id)
    
    return ContainerActionResponse(
        success=success,
        message=message,
        container_id=container_id,
    )


@api_router.post("/containers/{container_id}/kill", response_model=ContainerActionResponse, tags=["Containers"])
async def kill_container(
    container_id: str,
    signal: str = Query("SIGKILL", description="Signal to send to container"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Kill a container with a signal."""
    docker_service = DockerService(db, user_id=current_user.id)
    success, message = await docker_service.kill_container(container_id, signal)
    
    return ContainerActionResponse(
        success=success,
        message=message,
        container_id=container_id,
    )


@api_router.put("/containers/{container_id}/rename", response_model=ContainerActionResponse, tags=["Containers"])
async def rename_container(
    container_id: str,
    request: ContainerRenameRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Rename a container."""
    docker_service = DockerService(db, user_id=current_user.id)
    success, message = await docker_service.rename_container(container_id, request.new_name)
    
    return ContainerActionResponse(
        success=success,
        message=message,
        container_id=container_id,
    )


@api_router.patch("/containers/{container_id}", response_model=ContainerActionResponse, tags=["Containers"])
async def update_container(
    container_id: str,
    request: ContainerUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update container resource limits."""
    docker_service = DockerService(db, user_id=current_user.id)
    success, message = await docker_service.update_container(
        container_id,
        memory_limit=request.memory_limit,
        cpu_shares=request.cpu_shares,
    )
    
    return ContainerActionResponse(
        success=success,
        message=message,
        container_id=container_id,
    )


@api_router.get("/containers/{container_id}/diff", tags=["Containers"])
async def get_container_diff(
    container_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get container filesystem changes."""
    docker_service = DockerService(db)
    success, result = await docker_service.container_diff(container_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result,
        )
    
    changes = []
    for item in result:
        kind_map = {"A": "Added", "D": "Deleted", "C": "Changed"}
        changes.append({
            "path": item.get("Path", ""),
            "kind": item.get("Kind", 0),
            "change": kind_map.get(str(item.get("Kind", "")), "Unknown"),
        })
    
    return {"container_id": container_id, "changes": changes}


@api_router.delete("/containers", response_model=ContainerPruneResponse, tags=["Containers"])
async def prune_containers(
    filter_label: Optional[str] = Query(None, description="Label filter (e.g., 'app=web')"),
    filter_until: Optional[str] = Query(None, description="Until timestamp filter"),
    filter_name: Optional[str] = Query(None, description="Name filter"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove stopped containers."""
    docker_service = DockerService(db, user_id=current_user.id)
    
    filters = {}
    if filter_label:
        filters["label"] = filter_label
    if filter_until:
        filters["until"] = filter_until
    if filter_name:
        filters["name"] = filter_name
    
    success, result = await docker_service.prune_containers(filters=filters if filters else None)
    
    if not success:
        return ContainerPruneResponse(
            success=False,
            deleted_containers=[],
            space_reclaimed=0,
        )
    
    return ContainerPruneResponse(
        success=True,
        deleted_containers=result.get("ContainersDeleted", []),
        space_reclaimed=result.get("SpaceReclaimed", 0),
    )


@api_router.get("/containers/{container_id}/stats/formatted", tags=["Containers"])
async def get_container_stats_formatted(
    container_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get formatted container stats."""
    docker_service = DockerService(db)
    stats = await docker_service.get_container_stats_formatted(container_id)
    return stats


@api_router.post("/containers/{container_id}/exec", response_model=ContainerExecResponse, tags=["Containers"])
async def exec_in_container(
    container_id: str,
    request: ContainerExecRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Execute a command in a container."""
    docker_service = DockerService(db, user_id=current_user.id)
    success, output, error = await docker_service.exec_in_container(
        container_id,
        request.cmd,
        working_dir=request.working_dir,
        user=request.user,
        environment=request.environment,
    )
    
    return ContainerExecResponse(
        success=success,
        output=output,
        error=error,
    )


@api_router.post("/containers/{container_id}/shell", response_model=ContainerShellInitResponse, tags=["Containers"])
async def init_shell(
    container_id: str,
    shell: str = Query("/bin/sh", description="Shell to use"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Initialize a shell session in a container."""
    docker_service = DockerService(db, user_id=current_user.id)
    result = await docker_service.exec_attach(
        container_id,
        cmd=[shell],
        interactive=True,
        tty=True,
    )
    
    if "error" in result:
        return ContainerShellInitResponse(success=False, error=result["error"])
    
    return ContainerShellInitResponse(success=True, exec_id=result["exec_id"])


@api_router.websocket("/containers/{container_id}/shell/{exec_id}")
async def websocket_shell(
    websocket: WebSocket,
    container_id: str,
    exec_id: str,
):
    """WebSocket endpoint for interactive shell access."""
    
    session_key = f"{container_id}:{exec_id}"
    await manager.connect(websocket, session_key)
    
    docker_service = DockerService(None)
    
    try:
        async for chunk in docker_service.start_exec(exec_id, stream=True, socket=True):
            if isinstance(chunk, bytes):
                await websocket.send_bytes(chunk)
            else:
                await websocket.send_text(chunk)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")
    finally:
        manager.disconnect(session_key)


@api_router.post("/containers/{container_id}/resize", tags=["Containers"])
async def resize_terminal(
    container_id: str,
    exec_id: str,
    request: ContainerResizeRequest,
    current_user: User = Depends(get_current_user),
):
    """Resize the terminal for a shell session."""
    docker_service = DockerService(None)
    success, error = await docker_service.resize_exec(exec_id, request.height, request.width)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )
    
    return {"success": True}


@api_router.get("/docker/info", tags=["Docker"])
async def get_docker_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get Docker system information."""
    docker_service = DockerService(db)
    success, result = await docker_service.get_system_info()
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_BAD_REQUEST,
            detail=result.get("error", "Failed to get Docker info"),
        )
    
    return result


@api_router.get("/docker/version", tags=["Docker"])
async def get_docker_version(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get Docker version information."""
    docker_service = DockerService(db)
    success, result = await docker_service.get_docker_version()
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_BAD_REQUEST,
            detail=result.get("error", "Failed to get Docker version"),
        )
    
    return result


@api_router.get("/compose/file", response_model=DockerComposeFileContent, tags=["Docker Compose"])
async def get_compose_file(
    path: str = Query(..., description="Path to docker-compose.yaml file"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get docker-compose file content."""
    docker_service = DockerService(db)
    success, result = await docker_service.get_compose_file_content(path)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result,
        )
    
    return result


@api_router.get("/compose/validate", response_model=DockerComposeValidationResponse, tags=["Docker Compose"])
async def validate_compose_file(
    path: str = Query(..., description="Path to docker-compose.yaml file"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Validate a docker-compose file."""
    docker_service = DockerService(db)
    success, result = await docker_service.validate_compose_file(path)
    
    if not success:
        return DockerComposeValidationResponse(
            valid=False,
            errors=[result.get("error", "Unknown error")],
            warnings=[],
        )
    
    return DockerComposeValidationResponse(
        valid=True,
        errors=[],
        warnings=[],
    )


@api_router.post("/images/prune", tags=["Docker"])
async def prune_images(
    filter_dangling: bool = Query(False, description="Prune dangling images only"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove unused images."""
    docker_service = DockerService(db, user_id=current_user.id)
    success, result = await docker_service.prune_images(dangling=filter_dangling)
    
    if not success:
        return {"success": False, "error": result.get("error", "Unknown error")}
    
    return {
        "success": True,
        "images_deleted": result.get("ImagesDeleted", []),
        "space_reclaimed": result.get("SpaceReclaimed", 0),
    }


@api_router.post("/networks/prune", tags=["Docker"])
async def prune_networks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove unused networks."""
    docker_service = DockerService(db, user_id=current_user.id)
    success, result = await docker_service.prune_networks()
    
    if not success:
        return {"success": False, "error": result.get("error", "Unknown error")}
    
    return {
        "success": True,
        "networks_deleted": result.get("NetworksDeleted", []),
    }


@api_router.post("/volumes/prune", tags=["Docker"])
async def prune_volumes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove unused volumes."""
    docker_service = DockerService(db, user_id=current_user.id)
    success, result = await docker_service.prune_volumes()
    
    if not success:
        return {"success": False, "error": result.get("error", "Unknown error")}
    
    return {
        "success": True,
        "volumes_deleted": result.get("VolumesDeleted", []),
        "space_reclaimed": result.get("SpaceReclaimed", 0),
    }
