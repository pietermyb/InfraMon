"""API v1 router with all endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas import (
    UserResponse, UserCreate, UserUpdate, Token, LoginRequest,
    ContainerResponse, ContainerDetailResponse, ContainerGroupResponse,
    ContainerGroupCreate, ContainerGroupUpdate, ContainerStatsResponse,
    SystemStatsResponse, ActionResponse, ContainerLogsRequest,
    DockerComposePullRequest, ContainerRenameRequest, MessageResponse,
    DockerComposeProjectResponse,
)
from app.services.docker_service import DockerService
from app.services.container_service import ContainerService
from app.services.stats_service import StatsService
from app.services.auth_service import AuthService

api_router = APIRouter()


@api_router.post("/auth/login", response_model=Token)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.login(request.username, request.password)


@api_router.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.register(user_data)


@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@api_router.get("/containers", response_model=List[ContainerResponse])
async def list_containers(
    all_containers: bool = Query(False, description="Include stopped containers"),
    group_id: Optional[int] = Query(None, description="Filter by group"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    container_service = ContainerService(db)
    return await container_service.list_containers(all_containers, group_id)


@api_router.get("/containers/{container_id}", response_model=ContainerDetailResponse)
async def get_container(
    container_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    docker_service = DockerService(db)
    return await docker_service.inspect_container(container_id)


@api_router.post("/containers/{container_id}/start", response_model=ActionResponse)
async def start_container(
    container_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    docker_service = DockerService(db)
    success = await docker_service.start_container(container_id)
    return ActionResponse(success=success, message="Container started successfully" if success else "Failed to start container")


@api_router.post("/containers/{container_id}/stop", response_model=ActionResponse)
async def stop_container(
    container_id: str,
    timeout: int = Query(10, description="Timeout in seconds"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    docker_service = DockerService(db)
    success = await docker_service.stop_container(container_id, timeout)
    return ActionResponse(success=success, message="Container stopped successfully" if success else "Failed to stop container")


@api_router.post("/containers/{container_id}/restart", response_model=ActionResponse)
async def restart_container(
    container_id: str,
    timeout: int = Query(10, description="Timeout in seconds"),
    force: bool = Query(False, description="Force restart"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    docker_service = DockerService(db)
    success = await docker_service.restart_container(container_id, timeout, force)
    return ActionResponse(success=success, message="Container restarted successfully" if success else "Failed to restart container")


@api_router.delete("/containers/{container_id}", response_model=ActionResponse)
async def remove_container(
    container_id: str,
    force: bool = Query(False, description="Force remove"),
    volumes: bool = Query(False, description="Remove volumes"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    docker_service = DockerService(db)
    success = await docker_service.remove_container(container_id, force, volumes)
    return ActionResponse(success=success, message="Container removed successfully" if success else "Failed to remove container")


@api_router.get("/containers/{container_id}/logs")
async def get_container_logs(
    container_id: str,
    request: ContainerLogsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    docker_service = DockerService(db)
    return await docker_service.get_logs(container_id, request)


@api_router.get("/containers/{container_id}/stats")
async def get_container_stats(
    container_id: str,
    stream: bool = Query(False, description="Stream stats"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    docker_service = DockerService(db)
    return await docker_service.get_container_stats(container_id, stream)


@api_router.get("/containers/{container_id}/inspect")
async def inspect_container(
    container_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    docker_service = DockerService(db)
    return await docker_service.get_full_inspection(container_id)


@api_router.get("/containers/{container_id}/compose")
async def get_container_compose(
    container_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    docker_service = DockerService(db)
    return await docker_service.get_compose_info(container_id)


@api_router.post("/containers/{container_id}/compose/pull", response_model=ActionResponse)
async def pull_container_image(
    container_id: str,
    request: DockerComposePullRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    docker_service = DockerService(db)
    success = await docker_service.pull_image(container_id, request.no_cache)
    return ActionResponse(success=success, message="Image pulled successfully" if success else "Failed to pull image")


@api_router.get("/groups", response_model=List[ContainerGroupResponse])
async def list_groups(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    container_service = ContainerService(db)
    return await container_service.list_groups()


@api_router.post("/groups", response_model=ContainerGroupResponse)
async def create_group(
    group: ContainerGroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    container_service = ContainerService(db)
    return await container_service.create_group(group)


@api_router.get("/stats/system")
async def get_system_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stats_service = StatsService(db)
    return await stats_service.get_current_system_stats()


@api_router.get("/stats/dashboard")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stats_service = StatsService(db)
    return await stats_service.get_dashboard_summary()


@api_router.get("/compose/projects", response_model=List[DockerComposeProjectResponse])
async def list_compose_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    docker_service = DockerService(db)
    return await docker_service.list_compose_projects()
