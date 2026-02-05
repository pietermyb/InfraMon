"""Docker integration service."""

import docker
from docker.errors import DockerException
import asyncio
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import AsyncGenerator, Dict, Any, Optional
import json

from app.core.config import settings
from app.models.container import Container
from app.models.docker_compose_project import DockerComposeProject
from app.schemas import (
    ContainerDetailResponse, ContainerLogsRequest,
    DockerComposeProjectResponse,
)
from app.services.container_service import ContainerService


class DockerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            self._client = docker.DockerClient(
                base_url=f"unix://{settings.DOCKER_SOCKET_PATH}",
                version=settings.DOCKER_API_VERSION,
            )
        return self._client
    
    async def list_all_containers(self) -> list:
        loop = asyncio.get_event_loop()
        containers = await loop.run_in_executor(
            None, 
            lambda: self.client.containers.list(all=True)
        )
        
        result = []
        for container in containers:
            compose_file = await self.find_compose_file(container)
            result.append({
                "id": container.id,
                "name": container.name,
                "image": container.image.tags[0] if container.image.tags else container.image.id,
                "status": container.status,
                "compose_file": compose_file,
            })
        
        return result
    
    async def find_compose_file(self, container) -> Optional[str]:
        container_attrs = container.attrs
        mounts = container_attrs.get("Mounts", [])
        
        for mount in mounts:
            if mount.get("Type") == "bind":
                source_path = mount.get("Source")
                if source_path:
                    compose_path = await self.search_compose_file(source_path)
                    if compose_path:
                        return compose_path
        
        container_short_id = container.short_id
        mounts_path = Path("/var/lib/docker/containers") / container.attrs.get("Id", "") / "mounts"
        
        if mounts_path.exists():
            for compose_file in mounts_path.rglob("docker-compose*.yml"):
                return str(compose_file)
        
        return None
    
    async def search_compose_file(self, start_path: str, max_depth: int = 5) -> Optional[str]:
        start = Path(start_path)
        if not start.exists():
            return None
        
        for depth in range(max_depth + 1):
            for pattern in ["docker-compose.yml", "docker-compose.yaml"]:
                compose_file = start / pattern
                if compose_file.exists():
                    return str(compose_file)
            
            if depth < max_depth:
                start = start.parent
        
        return None
    
    async def inspect_container(self, container_id: str) -> ContainerDetailResponse:
        loop = asyncio.get_event_loop()
        container = await loop.run_in_executor(
            None,
            lambda: self.client.containers.get(container_id)
        )
        
        attrs = container.attrs
        
        response = {
            "id": 0,
            "container_id": container.id,
            "name": container.name,
            "image": container.image.tags[0] if container.image.tags else container.image.id,
            "status": container.status,
            "group_id": None,
            "docker_compose_path": None,
            "created_at": container.attrs.get("Created", ""),
            "updated_at": "",
            "ports": container.ports,
            "volumes": container.volumes,
            "environment": [{"name": k, "value": v} for k, v in container.env.items()] if container.env else [],
            "networks": list(container.networks.keys()) if container.networks else [],
            "labels": container.labels,
            "command": container.attrs.get("Config", {}).get("Cmd"),
            "started_at": container.attrs.get("State", {}).get("StartedAt"),
            "finished_at": container.attrs.get("State", {}).get("FinishedAt"),
            "restart_policy": container.attrs.get("HostConfig", {}).get("RestartPolicy"),
            "healthcheck": container.attrs.get("Config", {}).get("Healthcheck"),
        }
        
        return ContainerDetailResponse(**response)
    
    async def start_container(self, container_id: str) -> bool:
        try:
            loop = asyncio.get_event_loop()
            container = await loop.run_in_executor(
                None,
                lambda: self.client.containers.get(container_id)
            )
            await loop.run_in_executor(None, container.start)
            return True
        except DockerException:
            return False
    
    async def stop_container(self, container_id: str, timeout: int = 10) -> bool:
        try:
            loop = asyncio.get_event_loop()
            container = await loop.run_in_executor(
                None,
                lambda: self.client.containers.get(container_id)
            )
            await loop.run_in_executor(None, lambda: container.stop(timeout=timeout))
            return True
        except DockerException:
            return False
    
    async def restart_container(self, container_id: str, timeout: int = 10, force: bool = False) -> bool:
        try:
            loop = asyncio.get_event_loop()
            container = await loop.run_in_executor(
                None,
                lambda: self.client.containers.get(container_id)
            )
            await loop.run_in_executor(None, lambda: container.restart(timeout=timeout))
            return True
        except DockerException:
            return False
    
    async def remove_container(self, container_id: str, force: bool = False, volumes: bool = False) -> bool:
        try:
            loop = asyncio.get_event_loop()
            container = await loop.run_in_executor(
                None,
                lambda: self.client.containers.get(container_id)
            )
            await loop.run_in_executor(None, lambda: container.remove(force=force, volumes=volumes))
            return True
        except DockerException:
            return False
    
    async def get_logs(self, container_id: str, request: ContainerLogsRequest) -> Dict[str, Any]:
        try:
            loop = asyncio.get_event_loop()
            container = await loop.run_in_executor(
                None,
                lambda: self.client.containers.get(container_id)
            )
            logs = await loop.run_in_executor(
                None,
                lambda: container.logs(
                    stdout=request.stdout,
                    stderr=request.stderr,
                    timestamps=request.timestamps,
                    since=request.since,
                    until=request.until,
                    tail=request.tail,
                )
            )
            
            return {
                "logs": logs.decode("utf-8", errors="replace"),
                "container_id": container_id,
            }
        except DockerException as e:
            return {"logs": f"Error fetching logs: {str(e)}", "container_id": container_id}
    
    async def get_container_stats(self, container_id: str, stream: bool = False) -> Dict[str, Any]:
        try:
            loop = asyncio.get_event_loop()
            container = await loop.run_in_executor(
                None,
                lambda: self.client.containers.get(container_id)
            )
            stats = await loop.run_in_executor(
                None,
                lambda: container.stats(stream=stream)
            )
            return stats
        except DockerException as e:
            return {"error": str(e)}
    
    async def get_full_inspection(self, container_id: str) -> Dict[str, Any]:
        try:
            loop = asyncio.get_event_loop()
            container = await loop.run_in_executor(
                None,
                lambda: self.client.containers.get(container_id)
            )
            return container.attrs
        except DockerException as e:
            return {"error": str(e)}
    
    async def get_compose_info(self, container_id: str) -> Dict[str, Any]:
        try:
            loop = asyncio.get_event_loop()
            container = await loop.run_in_executor(
                None,
                lambda: self.client.containers.get(container_id)
            )
            compose_path = await self.find_compose_file(container)
            
            return {
                "container_id": container_id,
                "compose_file_path": compose_path,
                "project_name": None,
                "services": None,
            }
        except DockerException as e:
            return {"error": str(e)}
    
    async def pull_image(self, container_id: str, no_cache: bool = False) -> bool:
        try:
            loop = asyncio.get_event_loop()
            container = await loop.run_in_executor(
                None,
                lambda: self.client.containers.get(container_id)
            )
            image_name = container.image.tags[0] if container.image.tags else None
            
            if image_name:
                await loop.run_in_executor(
                    None,
                    lambda: self.client.images.pull(image_name, no_cache=no_cache)
                )
                return True
            return False
        except DockerException:
            return False
    
    async def list_compose_projects(self) -> list:
        loop = asyncio.get_event_loop()
        containers = await loop.run_in_executor(
            None,
            lambda: self.client.containers.list(all=True)
        )
        
        projects = {}
        for container in containers:
            compose_path = await self.find_compose_file(container)
            if compose_path:
                project_name = container.labels.get("com.docker.compose.project", "unknown")
                if project_name not in projects:
                    projects[project_name] = {
                        "project_name": project_name,
                        "compose_file_path": compose_path,
                        "services": [],
                    }
                projects[project_name]["services"].append(container.name)
        
        return list(projects.values())
