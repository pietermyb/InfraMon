"""Docker/Podman/Colima integration service."""

import docker
from docker.errors import DockerException, APIError
import asyncio
import os
from datetime import datetime
import logging
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import AsyncGenerator, Dict, Any, Optional, List
import json
import time
from concurrent.futures import ThreadPoolExecutor

from app.core.config import settings
from app.models.container import Container
from app.models.docker_compose_project import DockerComposeProject
from app.models.audit_log import AuditLog
from app.schemas import (
    ContainerDetailResponse,
    DockerComposeProjectResponse,
)
from app.services.container_service import ContainerService

logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor(max_workers=10)


def _get_socket_path() -> str:
    """Auto-detect the best available container runtime socket."""
    runtime = settings.CONTAINER_RUNTIME.lower()

    if runtime == "docker":
        return settings.DOCKER_SOCKET_PATH
    elif runtime == "podman":
        return settings.PODMAN_SOCKET_PATH
    elif runtime == "colima":
        return settings.COLIMA_SOCKET_PATH

    # Auto-detect: check each socket in order of preference
    sockets_to_check = [
        settings.DOCKER_SOCKET_PATH,
        settings.COLIMA_SOCKET_PATH,
        settings.PODMAN_SOCKET_PATH,
    ]

    for socket_path in sockets_to_check:
        if os.path.exists(socket_path):
            logger.info(f"Auto-detected container runtime socket: {socket_path}")
            return socket_path

    # Fallback to Docker default
    logger.warning(f"No container runtime socket found, defaulting to Docker")
    return settings.DOCKER_SOCKET_PATH


def _get_runtime_name() -> str:
    """Get the name of the detected/configured runtime."""
    socket_path = _get_socket_path()

    if "podman" in socket_path:
        return "Podman"
    elif "colima" in socket_path:
        return "Colima"
    else:
        return "Docker"


class DockerService:
    def __init__(self, db: AsyncSession, user_id: Optional[int] = None):
        self.db = db
        self._client = None
        self._user_id = user_id
        self._timeout = settings.DOCKER_TIMEOUT if hasattr(settings, "DOCKER_TIMEOUT") else 30
        self._runtime_name = None

    @property
    def client(self):
        if self._client is None:
            try:
                socket_path = _get_socket_path()
                self._runtime_name = _get_runtime_name()

                self._client = docker.DockerClient(
                    base_url=f"unix://{socket_path}",
                    version=settings.DOCKER_API_VERSION,
                    timeout=self._timeout,
                )
                self._client.ping()
                logger.info(f"Successfully connected to {self._runtime_name} daemon")
            except DockerException as e:
                logger.error(f"Failed to connect to container runtime: {e}")
                raise
        return self._client

    @property
    def runtime_name(self) -> str:
        """Return the name of the container runtime being used."""
        if self._runtime_name is None:
            self._runtime_name = _get_runtime_name()
        return self._runtime_name

    def _run_in_executor(self, func, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(
            executor,
            lambda: func(*args, **kwargs),
        )

    async def _safe_docker_call(self, func, *args, **kwargs) -> tuple:
        try:
            result = await self._run_in_executor(func, *args, **kwargs)
            return True, result, None
        except DockerException as e:
            logger.error(f"Docker API error: {e}")
            return False, None, str(e)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False, None, str(e)

    async def _log_operation(
        self, container_id: str, operation: str, details: Dict[str, Any] = None
    ):
        if self._user_id:
            audit = AuditLog(
                container_id=container_id,
                user_id=self._user_id,
                operation=operation,
                details=json.dumps(details) if details else None,
            )
            self.db.add(audit)
            await self.db.commit()

    async def list_all_containers(self, all_containers: bool = False) -> list:
        success, containers, error = await self._safe_docker_call(
            self.client.containers.list, all=all_containers
        )

        if not success:
            logger.error(f"Failed to list containers: {error}")
            return []

        result = []
        for container in containers:
            try:
                compose_file = await self.find_compose_file(container)
                image_name = container.image.tags[0] if container.image.tags else container.image.id
                result.append(
                    {
                        "id": 0,  # Placeholder for database ID if not synced
                        "container_id": container.id,
                        "name": container.name,
                        "image": image_name,
                        "status": container.status,
                        "compose_file": compose_file,
                        "labels": container.labels,
                        "ports": container.ports,
                    }
                )
            except Exception as e:
                logger.warning(f"Error processing container {container.id}: {e}")
                continue

        return result

    async def sync_container(self, container_info: dict) -> Container:
        """Synchronize container info with database."""
        try:
            result = await self.db.execute(
                select(Container).where(Container.container_id == container_info["container_id"])
            )
            db_container = result.scalar_one_or_none()

            if db_container:
                # Update existing
                db_container.name = container_info["name"]
                db_container.image = container_info["image"]
                db_container.status = container_info["status"]
                db_container.docker_compose_path = container_info.get("compose_file")
                db_container.updated_at = datetime.utcnow()
            else:
                # Create new
                db_container = Container(
                    container_id=container_info["container_id"],
                    name=container_info["name"],
                    image=container_info["image"],
                    status=container_info["status"],
                    docker_compose_path=container_info.get("compose_file"),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                self.db.add(db_container)

            await self.db.commit()
            await self.db.refresh(db_container)
            return db_container

        except Exception as e:
            logger.error(f"Error syncing container {container_info.get('name')}: {e}")
            return None

    def _resolve_host_path(self, path_str: str) -> Path:
        """Resolve a host path to a local path, potentially attempting a hostfs mount."""
        path = Path(path_str)
        if path.exists():
            return path

        if settings.HOST_FS_ROOT:
            # Try prepending the host fs root
            # Handle absolute paths properly (strip leading /)
            clean_path = path_str.lstrip("/")
            host_path = Path(settings.HOST_FS_ROOT) / clean_path
            if host_path.exists():
                return host_path

        return path

    async def find_compose_file(self, container) -> Optional[str]:
        try:
            container_attrs = container.attrs

            # 1. Check Labels (Most common for containers started via Docker Compose)
            labels = container_attrs.get("Config", {}).get("Labels", {})

            # Prioritize 'com.docker.compose.project.config_files' as it points to exactly what we want
            config_files = labels.get("com.docker.compose.project.config_files")
            if config_files:
                # Can be a comma-separated list of absolute paths
                for config_path in config_files.split(","):
                    config_path = config_path.strip()
                    if config_path:
                        # Attempt to resolve potentially host-path to local container path
                        resolved_path = self._resolve_host_path(config_path)
                        if resolved_path.exists() and resolved_path.is_file():
                            return str(resolved_path)

            # Try working directory as a secondary source if we have a project name
            if labels.get("com.docker.compose.project"):
                working_dir = labels.get("com.docker.compose.project.working_dir")
                if working_dir:
                    compose_path = await self.search_compose_file(working_dir)
                    if compose_path:
                        return compose_path

            # 2. Check Mounts (For containers that might mount their own compose file)
            mounts = container_attrs.get("Mounts", [])
            for mount in mounts:
                if mount.get("Type") == "bind":
                    source_path = mount.get("Source")
                    if source_path:
                        compose_path = await self.search_compose_file(source_path)
                        if compose_path:
                            return compose_path

            return None
        except Exception as e:
            logger.warning(f"Error finding compose file: {e}")
            return None

    async def search_compose_file(self, start_path: str, max_depth: int = 5) -> Optional[str]:
        try:
            # Resolve the starting path using potential HOST_FS_ROOT
            start = self._resolve_host_path(start_path)

            if not start.exists():
                return None

            # If it's a file and looks like a compose file, we're done
            if start.is_file():
                if start.name in [
                    "docker-compose.yml",
                    "docker-compose.yaml",
                    "compose.yml",
                    "compose.yaml",
                ]:
                    return str(start)
                # If it's a file but not a compose file, use its parent as search starting point
                start = start.parent

            # Search current directory and climb upwards
            for depth in range(max_depth + 1):
                for pattern in [
                    "docker-compose.yml",
                    "docker-compose.yaml",
                    "compose.yml",
                    "compose.yaml",
                ]:
                    compose_file = start / pattern
                    if compose_file.exists() and compose_file.is_file():
                        return str(compose_file)

                # Prevent infinite loop at root
                if depth < max_depth and str(start.parent) != str(start):
                    start = start.parent
                else:
                    break

            return None
        except Exception:
            return None

    async def inspect_container(self, container_id: str) -> Optional[ContainerDetailResponse]:
        # First try to get container directly
        success, container, error = await self._safe_docker_call(
            self.client.containers.get, container_id
        )

        # If not found with short ID, try to find full ID from list
        if not success or not container:
            try:
                # List all containers to find matching short_id
                list_success, containers, list_error = await self._safe_docker_call(
                    self.client.containers.list, all=True
                )
                if list_success and containers:
                    for c in containers:
                        if c.id.startswith(container_id) or c.short_id == container_id:
                            container = c
                            success = True
                            break
            except Exception as e:
                logger.warning(f"Error finding container by short_id: {e}")

        if not success or not container:
            return None

        try:
            attrs = container.attrs
            config = attrs.get("Config", {})
            state = attrs.get("State", {})
            host_config = attrs.get("HostConfig", {})
            network_settings = attrs.get("NetworkSettings", {})

            env_vars = config.get("Env", [])
            environment = (
                [
                    {"name": e.split("=", 1)[0], "value": e.split("=", 1)[1] if "=" in e else ""}
                    for e in env_vars
                ]
                if env_vars
                else []
            )

            networks = network_settings.get("Networks", {})
            network_names = list(networks.keys()) if networks else []

            image_tags = (
                container.image.tags
                if hasattr(container.image, "tags") and container.image.tags
                else []
            )
            image_name = (
                image_tags[0] if image_tags else attrs.get("Config", {}).get("Image", "unknown")
            )

            # Ensure command is a list
            cmd = config.get("Cmd")
            if cmd is None:
                cmd = []
            elif isinstance(cmd, str):
                cmd = [cmd]

            response = {
                "id": 0,
                "container_id": container.id,
                "name": container.name,
                "image": image_name,
                "status": container.status,
                "group_id": None,
                "docker_compose_path": None,
                "created_at": attrs.get("Created", ""),
                "updated_at": "",
                "created": attrs.get("Created", ""),
                "ports": container.ports if hasattr(container, "ports") else {},
                "volumes": [],
                "environment": environment,
                "networks": network_names,
                "labels": config.get("Labels") or {},
                "command": cmd,
                "started_at": state.get("StartedAt"),
                "finished_at": state.get("FinishedAt"),
                "restart_policy": host_config.get("RestartPolicy") or {},
                "healthcheck": config.get("Healthcheck"),
                "hostname": network_settings.get("Hostname", ""),
                "ip_address": network_settings.get("IPAddress", ""),
                "gateway": network_settings.get("Gateway", ""),
                "mac_address": network_settings.get("MacAddress", ""),
                "memory_limit": host_config.get("Memory") or 0,
                "memory_swap": host_config.get("MemorySwap") or 0,
                "cpu_shares": host_config.get("CpuShares") or 0,
                "cpu_period": host_config.get("CpuPeriod") or 0,
                "cpu_quota": host_config.get("CpuQuota") or 0,
                "blkio_weight": host_config.get("BlkioWeight") or 0,
                "blkio_device_read_bps": host_config.get("BlkioDeviceReadBps") or [],
                "blkio_device_write_bps": host_config.get("BlkioDeviceWriteBps") or [],
                "mounts": attrs.get("Mounts") or [],
                "working_dir": config.get("WorkingDir", ""),
                "entrypoint": config.get("Entrypoint") or [],
                "user": config.get("User", ""),
                "tty": config.get("Tty", False),
                "open_stdin": config.get("OpenStdin", False),
                "restart_count": state.get("RestartCount") or 0,
                "OOMKilled": state.get("OOMKilled", False),
                "dead": state.get("Dead", False),
                "exit_code": state.get("ExitCode") or 0,
            }

            return ContainerDetailResponse(**response)
        except Exception as e:
            logger.error(f"Error parsing container inspection: {e}")
            return None

    async def start_container(self, container_id: str) -> tuple:
        success, container, error = await self._safe_docker_call(
            self.client.containers.get, container_id
        )

        if not success or not container:
            return False, f"Container not found: {error}"

        success, _, error = await self._safe_docker_call(container.start)

        if success:
            await self._log_operation(container_id, "start", {"timeout": 0})
            return True, "Container started successfully"
        else:
            return False, f"Failed to start container: {error}"

    async def stop_container(self, container_id: str, timeout: int = 10) -> tuple:
        success, container, error = await self._safe_docker_call(
            self.client.containers.get, container_id
        )

        if not success or not container:
            return False, f"Container not found: {error}"

        success, _, error = await self._safe_docker_call(container.stop, timeout=timeout)

        if success:
            await self._log_operation(container_id, "stop", {"timeout": timeout})
            return True, "Container stopped successfully"
        else:
            return False, f"Failed to stop container: {error}"

    async def restart_container(
        self, container_id: str, timeout: int = 10, force: bool = False
    ) -> tuple:
        success, container, error = await self._safe_docker_call(
            self.client.containers.get, container_id
        )

        if not success or not container:
            return False, f"Container not found: {error}"

        success, _, error = await self._safe_docker_call(container.restart, timeout=timeout)

        if success:
            await self._log_operation(container_id, "restart", {"timeout": timeout, "force": force})
            return True, "Container restarted successfully"
        else:
            return False, f"Failed to restart container: {error}"

    async def pause_container(self, container_id: str) -> tuple:
        success, container, error = await self._safe_docker_call(
            self.client.containers.get, container_id
        )

        if not success or not container:
            return False, f"Container not found: {error}"

        success, _, error = await self._safe_docker_call(container.pause)

        if success:
            await self._log_operation(container_id, "pause", {})
            return True, "Container paused successfully"
        else:
            return False, f"Failed to pause container: {error}"

    async def unpause_container(self, container_id: str) -> tuple:
        success, container, error = await self._safe_docker_call(
            self.client.containers.get, container_id
        )

        if not success or not container:
            return False, f"Container not found: {error}"

        success, _, error = await self._safe_docker_call(container.unpause)

        if success:
            await self._log_operation(container_id, "unpause", {})
            return True, "Container unpaused successfully"
        else:
            return False, f"Failed to unpause container: {error}"

    async def kill_container(self, container_id: str, signal: str = "SIGKILL") -> tuple:
        success, container, error = await self._safe_docker_call(
            self.client.containers.get, container_id
        )

        if not success or not container:
            return False, f"Container not found: {error}"

        success, _, error = await self._safe_docker_call(container.kill, signal=signal)

        if success:
            await self._log_operation(container_id, "kill", {"signal": signal})
            return True, f"Container killed with {signal}"
        else:
            return False, f"Failed to kill container: {error}"

    async def rename_container(self, container_id: str, new_name: str) -> tuple:
        success, container, error = await self._safe_docker_call(
            self.client.containers.get, container_id
        )

        if not success or not container:
            return False, f"Container not found: {error}"

        success, _, error = await self._safe_docker_call(container.rename, new_name)

        if success:
            await self._log_operation(
                container_id, "rename", {"old_name": container.name, "new_name": new_name}
            )
            return True, f"Container renamed to {new_name}"
        else:
            return False, f"Failed to rename container: {error}"

    async def update_container(
        self, container_id: str, memory_limit: int = None, cpu_shares: int = None
    ) -> tuple:
        success, container, error = await self._safe_docker_call(
            self.client.containers.get, container_id
        )

        if not success or not container:
            return False, f"Container not found: {error}"

        try:
            host_config = {}
            if memory_limit:
                host_config["memory"] = memory_limit
            if cpu_shares:
                host_config["cpu_shares"] = cpu_shares

            success, _, error = await self._safe_docker_call(
                container.update, host_config=host_config
            )

            if success:
                await self._log_operation(container_id, "update", host_config)
                return True, "Container updated successfully"
            else:
                return False, f"Failed to update container: {error}"
        except Exception as e:
            return False, f"Failed to update container: {str(e)}"

    async def remove_container(
        self, container_id: str, force: bool = False, volumes: bool = False
    ) -> tuple:
        success, container, error = await self._safe_docker_call(
            self.client.containers.get, container_id
        )

        if not success or not container:
            return False, f"Container not found: {error}"

        success, _, error = await self._safe_docker_call(
            container.remove, force=force, volumes=volumes
        )

        if success:
            await self._log_operation(container_id, "remove", {"force": force, "volumes": volumes})
            return True, "Container removed successfully"
        else:
            return False, f"Failed to remove container: {error}"

    async def prune_containers(self, filters: Dict[str, str] = None) -> tuple:
        try:
            success, result, error = await self._safe_docker_call(
                self.client.containers.prune, filters=filters
            )

            if success:
                await self._log_operation("all", "prune", {"filters": filters})
                return True, result
            else:
                return False, {"error": error}
        except Exception as e:
            return False, {"error": str(e)}

    async def container_diff(self, container_id: str) -> tuple:
        success, container, error = await self._safe_docker_call(
            self.client.containers.get, container_id
        )

        if not success or not container:
            return False, f"Container not found: {error}"

        success, result, error = await self._safe_docker_call(container.diff)

        if success:
            return True, result
        else:
            return False, f"Failed to get container diff: {error}"

    async def get_logs(
        self,
        container_id: str,
        stdout: bool = True,
        stderr: bool = True,
        timestamps: bool = True,
        tail: str = "100",
        since: str = None,
        until: str = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        success, container, error = await self._safe_docker_call(
            self.client.containers.get, container_id
        )

        if not success or not container:
            return {"logs": f"Error fetching logs: {error}", "container_id": container_id}

        try:
            logs = await self._run_in_executor(
                container.logs,
                stdout=stdout,
                stderr=stderr,
                timestamps=timestamps,
                since=since,
                until=until,
                tail=tail,
                stream=stream,
            )

            if stream:
                return {"logs": logs, "container_id": container_id}

            decoded_logs = logs.decode("utf-8", errors="replace")
            await self._log_operation(
                container_id, "logs", {"tail": tail, "timestamps": timestamps}
            )
            return {
                "logs": decoded_logs,
                "container_id": container_id,
                "container_name": container.name,
            }
        except Exception as e:
            return {"logs": f"Error fetching logs: {str(e)}", "container_id": container_id}

    async def get_logs_generator(
        self, container_id: str, stdout: bool = True, stderr: bool = True, timestamps: bool = True
    ) -> AsyncGenerator[str, None]:
        success, container, error = await self._safe_docker_call(
            self.client.containers.get, container_id
        )

        if not success or not container:
            yield f"Error: {error}"
            return

        try:
            log_stream = await self._run_in_executor(
                container.logs,
                stdout=stdout,
                stderr=stderr,
                timestamps=timestamps,
                stream=True,
            )

            for line in log_stream:
                yield line.decode("utf-8", errors="replace")
        except Exception as e:
            yield f"Error streaming logs: {str(e)}"

    async def get_container_stats(self, container_id: str, stream: bool = False) -> Dict[str, Any]:
        success, container, error = await self._safe_docker_call(
            self.client.containers.get, container_id
        )

        if not success or not container:
            return {"error": error}

        try:
            stats_data = await self._run_in_executor(container.stats, stream=stream)
            return stats_data
        except Exception as e:
            return {"error": str(e)}

    async def get_container_stats_formatted(self, container_id: str) -> Dict[str, Any]:
        stats_data = await self.get_container_stats(container_id, stream=False)

        if "error" in stats_data:
            return stats_data

        try:
            cpu_delta = (
                stats_data["cpu_stats"]["cpu_usage"]["total_usage"]
                - stats_data["precpu_stats"]["cpu_usage"]["total_usage"]
            )
            system_delta = (
                stats_data["cpu_stats"]["system_cpu_usage"]
                - stats_data["precpu_stats"]["system_cpu_usage"]
            )
            num_cpus = stats_data["cpu_stats"].get("online_cpus", 1)

            if system_delta > 0 and cpu_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * num_cpus * 100.0
            else:
                cpu_percent = 0.0

            memory_usage = stats_data["memory_stats"].get("usage", 0)
            memory_limit = stats_data["memory_stats"].get("limit", 1)
            memory_percent = (memory_usage / memory_limit) * 100.0

            networks = stats_data.get("networks", {})
            network_rx = sum(net.get("rx_bytes", 0) for net in networks.values())
            network_tx = sum(net.get("tx_bytes", 0) for net in networks.values())

            block_io = stats_data.get("blkio_stats", {})
            block_read = sum(bt.get("value", 0) for bt in block_io.get("read_ops", []))
            block_write = sum(bt.get("value", 0) for bt in block_io.get("write_ops", []))

            pids = stats_data.get("pids_stats", {}).get("current", 0)

            return {
                "container_id": container_id,
                "cpu_usage": round(cpu_percent, 2),
                "memory_usage": round(memory_usage, 2),
                "memory_limit": round(memory_limit, 2),
                "memory_percent": round(memory_percent, 2),
                "network_rx": network_rx,
                "network_tx": network_tx,
                "block_read": block_read,
                "block_write": block_write,
                "pids": pids,
            }
        except Exception as e:
            return {"error": f"Error parsing stats: {str(e)}"}

    async def get_container_stats_generator(
        self, container_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        success, container, error = await self._safe_docker_call(
            self.client.containers.get, container_id
        )

        if not success or not container:
            yield {"error": error}
            return

        try:
            stats_stream = await self._run_in_executor(container.stats, stream=True)

            async def read_stats():
                try:
                    for stats_data in stats_stream:
                        yield stats_data
                except Exception:
                    pass

            async for stats_data in read_stats():
                yield await self._parse_stream_stats(stats_data)
        except Exception as e:
            yield {"error": str(e)}

    async def _parse_stream_stats(self, stats_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            cpu_delta = (
                stats_data["cpu_stats"]["cpu_usage"]["total_usage"]
                - stats_data["precpu_stats"]["cpu_usage"]["total_usage"]
            )
            system_delta = (
                stats_data["cpu_stats"]["system_cpu_usage"]
                - stats_data["precpu_stats"]["system_cpu_usage"]
            )
            num_cpus = stats_data["cpu_stats"].get("online_cpus", 1)

            if system_delta > 0 and cpu_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * num_cpus * 100.0
            else:
                cpu_percent = 0.0

            memory_usage = stats_data["memory_stats"].get("usage", 0)
            memory_limit = stats_data["memory_stats"].get("limit", 1)
            memory_percent = (memory_usage / memory_limit) * 100.0

            networks = stats_data.get("networks", {})
            network_rx = sum(net.get("rx_bytes", 0) for net in networks.values())
            network_tx = sum(net.get("tx_bytes", 0) for net in networks.values())

            pids = stats_data.get("pids_stats", {}).get("current", 0)

            return {
                "cpu_usage": round(cpu_percent, 2),
                "memory_usage": round(memory_usage, 2),
                "memory_percent": round(memory_percent, 2),
                "network_rx": network_rx,
                "network_tx": network_tx,
                "pids": pids,
            }
        except Exception:
            return {"error": "Error parsing stats"}

    async def get_full_inspection(self, container_id: str) -> Dict[str, Any]:
        try:
            loop = asyncio.get_event_loop()
            container = await loop.run_in_executor(
                None, lambda: self.client.containers.get(container_id)
            )
            return container.attrs
        except DockerException as e:
            return {"error": str(e)}

    async def get_compose_info(self, container_id: str) -> Dict[str, Any]:
        try:
            loop = asyncio.get_event_loop()
            container = await loop.run_in_executor(
                None, lambda: self.client.containers.get(container_id)
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
                None, lambda: self.client.containers.get(container_id)
            )
            image_name = container.image.tags[0] if container.image.tags else None

            if image_name:
                await loop.run_in_executor(
                    None, lambda: self.client.images.pull(image_name, no_cache=no_cache)
                )
                return True
            return False
        except DockerException:
            return False

    async def list_compose_projects(self) -> list:
        success, containers, error = await self._safe_docker_call(
            self.client.containers.list, all=True
        )

        if not success:
            return []

        projects = {}
        for container in containers:
            try:
                compose_path = await self.find_compose_file(container)
                if compose_path:
                    labels = container.attrs.get("Config", {}).get("Labels", {})
                    project_name = labels.get("com.docker.compose.project", "unknown")
                    service_name = labels.get("com.docker.compose.service", container.name)

                    if project_name not in projects:
                        projects[project_name] = {
                            "project_name": project_name,
                            "compose_file_path": compose_path,
                            "services": [],
                            "status": container.status,
                        }
                    if service_name not in projects[project_name]["services"]:
                        projects[project_name]["services"].append(service_name)
            except Exception as e:
                logger.warning(f"Error processing container {container.id}: {e}")
                continue

        return list(projects.values())

    async def exec_in_container(
        self,
        container_id: str,
        cmd: List[str],
        working_dir: str = None,
        user: str = None,
        environment: Dict[str, str] = None,
    ) -> tuple:
        success, container, error = await self._safe_docker_call(
            self.client.containers.get, container_id
        )

        if not success or not container:
            return False, None, f"Container not found: {error}"

        try:
            exec_id = await self._run_in_executor(
                container.exec_run,
                cmd,
                detach=False,
                workdir=working_dir,
                user=user,
                environment=environment,
            )

            if exec_id.exit_code is not None:
                return True, exec_id.output.decode("utf-8", errors="replace"), None
            else:
                return False, None, "Exec command did not return output"
        except Exception as e:
            return False, None, str(e)

    async def exec_attach(
        self,
        container_id: str,
        cmd: List[str],
        interactive: bool = True,
        tty: bool = True,
        workdir: str = None,
        user: str = None,
    ) -> Dict[str, Any]:
        success, container, error = await self._safe_docker_call(
            self.client.containers.get, container_id
        )

        if not success or not container:
            return {"error": error}

        try:
            exec_id_resp = await self._run_in_executor(
                self.client.api.exec_create,
                container.id,
                cmd=cmd,
                stdin=interactive,
                tty=tty,
                workdir=workdir,
                user=user,
            )

            # exec_id_resp is a dictionary like {'Id': '...'}
            return {
                "exec_id": exec_id_resp.get("Id"),
                "container_id": container_id,
                "cmd": cmd,
            }
        except Exception as e:
            return {"error": str(e)}

    async def start_exec(
        self, exec_id: str, stream: bool = True, socket: bool = True
    ) -> AsyncGenerator[bytes, None]:
        try:
            exec_start = docker.types.ExecStartOutput(
                stream=stream,
                socket=socket,
            )

            async for chunk in self._run_exec_with_stream(exec_id, exec_start):
                yield chunk
        except Exception as e:
            yield f"Error: {str(e)}".encode("utf-8")

    async def _run_exec_with_stream(self, exec_id: str, exec_config) -> AsyncGenerator[bytes, None]:
        loop = asyncio.get_event_loop()

        def exec_generator():
            try:
                for chunk in self.client.api.exec_start(exec_id, stream=True, demux=False):
                    yield chunk
            except Exception as e:
                yield f"Error: {str(e)}".encode("utf-8")

        for chunk in exec_generator():
            yield chunk

    async def resize_exec(self, exec_id: str, height: int = 24, width: int = 80) -> tuple:
        try:
            await self._run_in_executor(
                self.client.api.exec_resize,
                exec_id,
                height=height,
                width=width,
            )
            return True, None
        except Exception as e:
            return False, str(e)

    async def pull_image(self, container_id: str, no_cache: bool = False) -> tuple:
        success, container, error = await self._safe_docker_call(
            self.client.containers.get, container_id
        )

        if not success or not container:
            return False, f"Container not found: {error}"

        try:
            image_name = (
                container.image.tags[0]
                if hasattr(container.image, "tags") and container.image.tags
                else None
            )

            if not image_name:
                return False, "No image tag found for container"

            success, _, error = await self._safe_docker_call(
                self.client.images.pull, image_name, no_cache=no_cache
            )

            if success:
                await self._log_operation(
                    container_id, "pull_image", {"image": image_name, "no_cache": no_cache}
                )
                return True, f"Image {image_name} pulled successfully"
            else:
                return False, f"Failed to pull image: {error}"
        except Exception as e:
            return False, str(e)

    async def get_compose_file_content(self, compose_path: str) -> tuple:
        try:
            path = Path(compose_path)
            if not path.exists():
                return False, f"Compose file not found: {compose_path}"

            content = await self._run_in_executor(lambda: path.read_text())

            import yaml

            try:
                compose_data = yaml.safe_load(content)
                services = list(compose_data.get("services", {}).keys()) if compose_data else []
                networks = list(compose_data.get("networks", {}).keys()) if compose_data else []
                volumes = list(compose_data.get("volumes", {}).keys()) if compose_data else []

                return True, {
                    "path": compose_path,
                    "content": content,
                    "services": services,
                    "networks": networks,
                    "volumes": volumes,
                }
            except yaml.YAMLError as e:
                return False, f"Invalid YAML: {str(e)}"
        except Exception as e:
            return False, str(e)

    async def validate_compose_file(self, compose_path: str) -> tuple:
        success, result, error = await self._safe_docker_call(self.client.api.version)

        if not success:
            return False, {"error": error}

        try:
            content_result = await self.get_compose_file_content(compose_path)
            if not content_result[0]:
                return False, {"error": content_result[1]}

            data = content_result[1]
            return True, {
                "valid": True,
                "services_count": len(data["services"]),
                "networks_count": len(data["networks"]),
                "volumes_count": len(data["volumes"]),
            }
        except Exception as e:
            return False, {"error": str(e)}

    async def prune_images(self, filters: Dict[str, str] = None, dangling: bool = False) -> tuple:
        try:
            filters = filters or {}
            if dangling:
                filters["dangling"] = "true"

            success, result, error = await self._safe_docker_call(
                self.client.images.prune, filters=filters
            )

            if success:
                await self._log_operation("images", "prune", {"filters": filters})
                return True, result
            else:
                return False, {"error": error}
        except Exception as e:
            return False, {"error": str(e)}

    async def prune_networks(self, filters: Dict[str, str] = None) -> tuple:
        try:
            success, result, error = await self._safe_docker_call(
                self.client.networks.prune, filters=filters
            )

            if success:
                await self._log_operation("networks", "prune", {"filters": filters})
                return True, result
            else:
                return False, {"error": error}
        except Exception as e:
            return False, {"error": str(e)}

    async def prune_volumes(self, filters: Dict[str, str] = None) -> tuple:
        try:
            success, result, error = await self._safe_docker_call(
                self.client.volumes.prune, filters=filters
            )

            if success:
                await self._log_operation("volumes", "prune", {"filters": filters})
                return True, result
            else:
                return False, {"error": error}
        except Exception as e:
            return False, {"error": str(e)}

    async def get_system_info(self) -> tuple:
        success, info, error = await self._safe_docker_call(self.client.info)

        if success:
            return True, info
        else:
            return False, {"error": error}

    async def get_docker_version(self) -> tuple:
        success, version, error = await self._safe_docker_call(self.client.api.version)

        if success:
            return True, version
        else:
            return False, {"error": error}
