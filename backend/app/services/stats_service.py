"""Statistics service for system and container metrics."""

import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, asc
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, AsyncGenerator
import psutil
import os
from pathlib import Path
import json

from app.models.system_stats import SystemStats
from app.models.container_stats import ContainerStats
from app.models.container import Container
from app.models.container_group import ContainerGroup
from app.services.docker_service import DockerService

logger = logging.getLogger(__name__)


class StatsService:
    def __init__(self, db: AsyncSession, user_id: Optional[int] = None):
        self.db = db
        self._user_id = user_id
        self._collection_interval = 60
        self._stats_history: List[Dict[str, Any]] = []
        self._max_history_size = 100
    
    async def get_current_system_stats(self) -> Dict[str, Any]:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        disk_io = psutil.disk_io_counters()
        network_io = psutil.net_io_counters(pernic=True)
        load_avg = os.getloadavg()
        uptime = psutil.boot_time()
        
        cpu_cores = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        temperatures = {}
        try:
            temps = psutil.sensors_temperatures()
            for name, entries in temps.items():
                if entries:
                    temperatures[name] = entries[0].current
        except Exception:
            pass
        
        network_interfaces = []
        for interface, counters in network_io.items():
            network_interfaces.append({
                "interface": interface,
                "bytes_sent": counters.bytes_sent,
                "bytes_recv": counters.bytes_recv,
                "packets_sent": counters.packets_sent,
                "packets_recv": counters.packets_recv,
                "errin": counters.errin,
                "errout": counters.errout,
                "dropin": counters.dropin,
                "dropout": counters.dropout,
            })
        
        current_time = datetime.utcnow()
        
        return {
            "id": 0,
            "cpu_usage": cpu_percent,
            "cpu_cores": cpu_cores,
            "cpu_frequency": cpu_freq.current if cpu_freq else 0,
            "memory_usage": memory.percent,
            "memory_total": memory.total,
            "memory_used": memory.used,
            "memory_available": memory.available,
            "memory_percent": memory.percent,
            "swap_usage": getattr(memory, 'swapped', {}).get('used', 0),
            "swap_total": getattr(memory, 'swapped', {}).get('total', 0),
            "disk_usage": disk.percent,
            "disk_total": disk.total,
            "disk_used": disk.used,
            "disk_free": disk.free,
            "disk_read_bytes": disk_io.read_bytes,
            "disk_write_bytes": disk_io.write_bytes,
            "disk_read_count": disk_io.read_count,
            "disk_write_count": disk_io.write_count,
            "network_rx": sum(n["bytes_recv"] for n in network_interfaces),
            "network_tx": sum(n["bytes_sent"] for n in network_interfaces),
            "network_interfaces": network_interfaces,
            "load_avg_1m": load_avg[0],
            "load_avg_5m": load_avg[1],
            "load_avg_15m": load_avg[2],
            "load_percent": (load_avg[0] / cpu_cores * 100) if cpu_cores > 0 else 0,
            "uptime": current_time.timestamp() - uptime,
            "boot_time": datetime.fromtimestamp(uptime).isoformat(),
            "temperatures": temperatures,
            "timestamp": current_time,
        }
    
    async def get_system_info(self) -> Dict[str, Any]:
        hostname = os.uname().nodename
        system = os.uname().sysname
        release = os.uname().release
        version = os.uname().version
        machine = os.uname().machine
        
        boot_time = psutil.boot_time()
        users = psutil.users()
        
        connected_users = []
        for user in users:
            connected_users.append({
                "name": user.name,
                "terminal": user.terminal,
                "host": user.host,
                "started": datetime.fromtimestamp(user.started).isoformat(),
            })
        
        return {
            "hostname": hostname,
            "system": system,
            "release": release,
            "version": version,
            "machine": machine,
            "boot_time": datetime.fromtimestamp(boot_time).isoformat(),
            "uptime": datetime.utcnow().timestamp() - boot_time,
            "cpu_architecture": machine,
            "kernel_version": version,
            "connected_users": connected_users,
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        }
    
    async def get_disk_partitions(self) -> List[Dict[str, Any]]:
        partitions = []
        for partition in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "opts": partition.opts,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                })
            except Exception:
                continue
        
        return partitions
    
    async def get_network_connections(self, kind: str = "inet") -> List[Dict[str, Any]]:
        connections = []
        try:
            for conn in psutil.net_connections(kind=kind):
                connections.append({
                    "fd": conn.fd,
                    "family": str(conn.family.name) if hasattr(conn.family, 'name') else str(conn.family),
                    "type": str(conn.type.name) if hasattr(conn.type, 'name') else str(conn.type),
                    "local_address": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                    "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    "status": conn.status,
                    "pid": conn.pid,
                })
        except Exception as e:
            logger.warning(f"Error getting network connections: {e}")
        
        return connections
    
    async def get_process_list(self, limit: int = 20, order_by: str = "cpu") -> List[Dict[str, Any]]:
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cmdline', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    cpu_percent = pinfo.get('cpu_percent', 0)
                    memory_percent = pinfo.get('memory_percent', 0)
                    processes.append({
                        "pid": pinfo['pid'],
                        "name": pinfo['name'],
                        "username": pinfo.get('username'),
                        "cmdline": ' '.join(pinfo.get('cmdline', [])) if pinfo.get('cmdline') else None,
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory_percent,
                    })
                except Exception:
                    continue
            
            if order_by == "cpu":
                processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            elif order_by == "memory":
                processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            elif order_by == "pid":
                processes.sort(key=lambda x: x['pid'])
            
            return processes[:limit]
        except Exception as e:
            logger.error(f"Error getting process list: {e}")
            return []
    
    async def get_container_resource_stats(self, container_id: str, formatted: bool = True) -> Dict[str, Any]:
        docker_service = DockerService(self.db)
        stats = await docker_service.get_container_stats_formatted(container_id)
        
        if "error" in stats:
            return stats
        
        if formatted:
            return stats
        
        raw_stats = await docker_service.get_container_stats(container_id, stream=False)
        return raw_stats
    
    async def get_container_processes(self, container_id: str) -> List[Dict[str, Any]]:
        docker_service = DockerService(self.db)
        success, container, error = await docker_service._safe_docker_call(
            docker_service.client.containers.get, container_id
        )
        
        if not success or not container:
            return []
        
        try:
            processes = await docker_service._run_in_executor(
                container.top, ps_args="aux"
            )
            
            process_list = []
            if isinstance(processes, tuple) and len(processes) > 0:
                headers = processes[0] if isinstance(processes[0], list) else []
                rows = processes[1] if isinstance(processes[1], list) else []
                
                if headers and rows:
                    for row in rows:
                        process = {}
                        for i, header in enumerate(headers):
                            process[header] = row[i] if i < len(row) else None
                        process_list.append(process)
            
            return process_list
        except Exception as e:
            logger.error(f"Error getting container processes: {e}")
            return []
    
    async def get_container_filesystem_usage(self, container_id: str) -> List[Dict[str, Any]]:
        docker_service = DockerService(self.db)
        success, container, error = await docker_service._safe_docker_call(
            docker_service.client.containers.get, container_id
        )
        
        if not success or not container:
            return []
        
        try:
            mounts = container.attrs.get("Mounts", [])
            usage_list = []
            
            for mount in mounts:
                if mount.get("Type") == "bind":
                    try:
                        path = mount.get("Destination", mount.get("Source"))
                        usage = psutil.disk_usage(path)
                        usage_list.append({
                            "mount_point": path,
                            "source": mount.get("Source"),
                            "total": usage.total,
                            "used": usage.used,
                            "free": usage.free,
                            "percent": usage.percent,
                        })
                    except Exception:
                        continue
                elif mount.get("Type") == "volume":
                    usage_list.append({
                        "mount_point": mount.get("Destination"),
                        "volume_name": mount.get("Name"),
                        "type": "volume",
                    })
            
            return usage_list
        except Exception as e:
            logger.error(f"Error getting container filesystem usage: {e}")
            return []
    
    async def collect_and_store_system_stats(self) -> SystemStats:
        stats = await self.get_current_system_stats()
        
        system_stats = SystemStats(
            cpu_usage=stats["cpu_usage"],
            memory_usage=stats["memory_usage"],
            memory_total=stats["memory_total"],
            disk_usage=stats["disk_usage"],
            disk_total=stats["disk_total"],
            network_rx=stats["network_rx"],
            network_tx=stats["network_tx"],
            load_avg_1m=stats["load_avg_1m"],
            load_avg_5m=stats["load_avg_5m"],
            load_avg_15m=stats["load_avg_15m"],
            uptime=stats["uptime"],
            timestamp=stats["timestamp"],
        )
        
        self.db.add(system_stats)
        await self.db.commit()
        await self.db.refresh(system_stats)
        
        self._stats_history.append(stats)
        if len(self._stats_history) > self._max_history_size:
            self._stats_history.pop(0)
        
        return system_stats
    
    async def collect_and_store_container_stats(self, container_id: str) -> Optional[ContainerStats]:
        docker_service = DockerService(self.db)
        container_stats = await docker_service.get_container_stats_formatted(container_id)
        
        if "error" in container_stats:
            return None
        
        result = await self.db.execute(
            select(Container).where(Container.container_id == container_id)
        )
        container = result.scalar_one_or_none()
        
        if not container:
            return None
        
        stats = ContainerStats(
            container_id=container.id,
            cpu_usage=container_stats.get("cpu_usage", 0),
            memory_usage=container_stats.get("memory_usage", 0),
            memory_limit=container_stats.get("memory_limit", 0),
            network_rx=container_stats.get("network_rx", 0),
            network_tx=container_stats.get("network_tx", 0),
            block_read=container_stats.get("block_read", 0),
            block_write=container_stats.get("block_write", 0),
            pids=container_stats.get("pids", 0),
        )
        
        self.db.add(stats)
        await self.db.commit()
        await self.db.refresh(stats)
        
        return stats
    
    async def get_system_stats_history(
        self,
        period: str = "1h",
        aggregate: bool = False,
    ) -> List[Dict[str, Any]]:
        now = datetime.utcnow()
        
        periods = {
            "1h": timedelta(hours=1),
            "6h": timedelta(hours=6),
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
        }
        
        delta = periods.get(period, timedelta(hours=1))
        start_time = now - delta
        
        query = select(SystemStats).where(
            SystemStats.timestamp >= start_time
        ).order_by(asc(SystemStats.timestamp))
        
        result = await self.db.execute(query)
        stats = result.scalars().all()
        
        if aggregate and len(stats) > 0:
            return self._aggregate_system_stats(stats, period)
        
        return [self._serialize_system_stat(s) for s in stats]
    
    async def get_container_stats_history(
        self,
        container_id: str,
        period: str = "1h",
        aggregate: bool = False,
    ) -> List[Dict[str, Any]]:
        now = datetime.utcnow()
        
        periods = {
            "1h": timedelta(hours=1),
            "6h": timedelta(hours=6),
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
        }
        
        delta = periods.get(period, timedelta(hours=1))
        start_time = now - delta
        
        container_result = await self.db.execute(
            select(Container).where(Container.container_id == container_id)
        )
        container = container_result.scalar_one_or_none()
        
        if not container:
            return []
        
        query = select(ContainerStats).where(
            and_(
                ContainerStats.container_id == container.id,
                ContainerStats.timestamp >= start_time
            )
        ).order_by(asc(ContainerStats.timestamp))
        
        result = await self.db.execute(query)
        stats = result.scalars().all()
        
        if aggregate and len(stats) > 0:
            return self._aggregate_container_stats(stats, period)
        
        return [self._serialize_container_stat(s) for s in stats]
    
    def _aggregate_system_stats(
        self,
        stats: List[SystemStats],
        period: str,
    ) -> List[Dict[str, Any]]:
        if not stats:
            return []
        
        interval_map = {
            "1h": 60,
            "6h": 300,
            "24h": 900,
            "7d": 3600,
            "30d": 14400,
        }
        
        interval_seconds = interval_map.get(period, 60)
        aggregated = {}
        
        for stat in stats:
            interval_timestamp = int(stat.timestamp.timestamp() / interval_seconds) * interval_seconds
            interval_key = datetime.fromtimestamp(interval_timestamp)
            
            if interval_key not in aggregated:
                aggregated[interval_key] = {
                    "timestamps": [],
                    "cpu_usage": [],
                    "memory_usage": [],
                    "network_rx": [],
                    "network_tx": [],
                    "disk_usage": [],
                    "load_avg_1m": [],
                }
            
            aggregated[interval_key]["timestamps"].append(stat.timestamp)
            aggregated[interval_key]["cpu_usage"].append(stat.cpu_usage)
            aggregated[interval_key]["memory_usage"].append(stat.memory_usage)
            aggregated[interval_key]["network_rx"].append(stat.network_rx)
            aggregated[interval_key]["network_tx"].append(stat.network_tx)
            aggregated[interval_key]["disk_usage"].append(stat.disk_usage)
            aggregated[interval_key]["load_avg_1m"].append(stat.load_avg_1m)
        
        result = []
        for timestamp, values in sorted(aggregated.items()):
            result.append({
                "timestamp": timestamp,
                "cpu_usage_avg": sum(values["cpu_usage"]) / len(values["cpu_usage"]) if values["cpu_usage"] else 0,
                "cpu_usage_max": max(values["cpu_usage"]) if values["cpu_usage"] else 0,
                "cpu_usage_min": min(values["cpu_usage"]) if values["cpu_usage"] else 0,
                "memory_usage_avg": sum(values["memory_usage"]) / len(values["memory_usage"]) if values["memory_usage"] else 0,
                "memory_usage_max": max(values["memory_usage"]) if values["memory_usage"] else 0,
                "memory_usage_min": min(values["memory_usage"]) if values["memory_usage"] else 0,
                "network_rx": values["network_rx"][-1] if values["network_rx"] else 0,
                "network_tx": values["network_tx"][-1] if values["network_tx"] else 0,
                "disk_usage": values["disk_usage"][-1] if values["disk_usage"] else 0,
                "load_avg_1m": values["load_avg_1m"][-1] if values["load_avg_1m"] else 0,
            })
        
        return result
    
    def _aggregate_container_stats(
        self,
        stats: List[ContainerStats],
        period: str,
    ) -> List[Dict[str, Any]]:
        if not stats:
            return []
        
        interval_map = {
            "1h": 60,
            "6h": 300,
            "24h": 900,
            "7d": 3600,
            "30d": 14400,
        }
        
        interval_seconds = interval_map.get(period, 60)
        aggregated = {}
        
        for stat in stats:
            interval_timestamp = int(stat.timestamp.timestamp() / interval_seconds) * interval_seconds
            interval_key = datetime.fromtimestamp(interval_timestamp)
            
            if interval_key not in aggregated:
                aggregated[interval_key] = {
                    "timestamps": [],
                    "cpu_usage": [],
                    "memory_usage": [],
                    "network_rx": [],
                    "network_tx": [],
                }
            
            aggregated[interval_key]["timestamps"].append(stat.timestamp)
            aggregated[interval_key]["cpu_usage"].append(stat.cpu_usage)
            aggregated[interval_key]["memory_usage"].append(stat.memory_usage)
            aggregated[interval_key]["network_rx"].append(stat.network_rx)
            aggregated[interval_key]["network_tx"].append(stat.network_tx)
        
        result = []
        for timestamp, values in sorted(aggregated.items()):
            result.append({
                "timestamp": timestamp,
                "cpu_usage_avg": sum(values["cpu_usage"]) / len(values["cpu_usage"]) if values["cpu_usage"] else 0,
                "cpu_usage_max": max(values["cpu_usage"]) if values["cpu_usage"] else 0,
                "memory_usage_avg": sum(values["memory_usage"]) / len(values["memory_usage"]) if values["memory_usage"] else 0,
                "memory_usage_max": max(values["memory_usage"]) if values["memory_usage"] else 0,
                "network_rx": values["network_rx"][-1] if values["network_rx"] else 0,
                "network_tx": values["network_tx"][-1] if values["network_tx"] else 0,
            })
        
        return result
    
    def _serialize_system_stat(self, stat: SystemStats) -> Dict[str, Any]:
        return {
            "id": stat.id,
            "cpu_usage": stat.cpu_usage,
            "memory_usage": stat.memory_usage,
            "memory_total": stat.memory_total,
            "disk_usage": stat.disk_usage,
            "disk_total": stat.disk_total,
            "network_rx": stat.network_rx,
            "network_tx": stat.network_tx,
            "load_avg_1m": stat.load_avg_1m,
            "load_avg_5m": stat.load_avg_5m,
            "load_avg_15m": stat.load_avg_15m,
            "uptime": stat.uptime,
            "timestamp": stat.timestamp,
        }
    
    def _serialize_container_stat(self, stat: ContainerStats) -> Dict[str, Any]:
        return {
            "id": stat.id,
            "container_id": stat.container_id,
            "cpu_usage": stat.cpu_usage,
            "memory_usage": stat.memory_usage,
            "memory_limit": stat.memory_limit,
            "network_rx": stat.network_rx,
            "network_tx": stat.network_tx,
            "block_read": stat.block_read,
            "block_write": stat.block_write,
            "pids": stat.pids,
            "timestamp": stat.timestamp,
        }
    
    async def get_dashboard_summary(self) -> Dict[str, Any]:
        system_stats = await self.get_current_system_stats()
        docker_service = DockerService(self.db)
        
        containers_result = await docker_service.list_all_containers(all_containers=True)
        
        running = sum(1 for c in containers_result if c.get("status") == "running")
        stopped = sum(1 for c in containers_result if c.get("status") == "stopped")
        paused = sum(1 for c in containers_result if c.get("status") == "paused")
        
        total_memory = system_stats.get("memory_total", 0)
        total_disk = system_stats.get("disk_total", 0)
        cpu_cores = system_stats.get("cpu_cores", 0)
        
        container_resources = {
            "total_containers": len(containers_result),
            "running": running,
            "stopped": stopped,
            "paused": paused,
            "total_cpu_cores": cpu_cores,
            "total_memory_bytes": total_memory,
            "total_disk_bytes": total_disk,
        }
        
        return {
            "system": system_stats,
            "containers": container_resources,
            "resources": {
                "cpu_cores": cpu_cores,
                "total_memory": total_memory,
                "total_disk": total_disk,
            },
            "uptime": system_stats["uptime"],
            "timestamp": datetime.utcnow(),
        }
    
    async def get_top_consumers(
        self,
        metric: str = "cpu",
        limit: int = 10,
        period: str = "1h",
    ) -> List[Dict[str, Any]]:
        now = datetime.utcnow()
        delta = {"1h": timedelta(hours=1), "24h": timedelta(hours=24), "7d": timedelta(days=7)}.get(
            period, timedelta(hours=1)
        )
        start_time = now - delta
        
        query = select(ContainerStats).where(
            ContainerStats.timestamp >= start_time
        )
        
        result = await self.db.execute(query)
        stats = result.scalars().all()
        
        container_stats = {}
        for stat in stats:
            if stat.container_id not in container_stats:
                container_stats[stat.container_id] = []
            container_stats[stat.container_id].append(stat)
        
        consumers = []
        for container_id, container_data in container_stats.items():
            container_result = await self.db.execute(
                select(Container).where(Container.id == container_id)
            )
            container = container_result.scalar_one_or_none()
            
            if not container:
                continue
            
            avg_cpu = sum(s.cpu_usage for s in container_data) / len(container_data) if container_data else 0
            max_cpu = max(s.cpu_usage for s in container_data) if container_data else 0
            avg_memory = sum(s.memory_usage for s in container_data) / len(container_data) if container_data else 0
            max_memory = max(s.memory_usage for s in container_data) if container_data else 0
            total_network = sum(s.network_rx + s.network_tx for s in container_data) if container_data else 0
            
            consumers.append({
                "container_id": container.container_id,
                "name": container.name,
                "image": container.image,
                "avg_cpu": avg_cpu,
                "max_cpu": max_cpu,
                "avg_memory": avg_memory,
                "max_memory": max_memory,
                "total_network": total_network,
                "status": container.status,
            })
        
        if metric == "cpu":
            consumers.sort(key=lambda x: x["avg_cpu"], reverse=True)
        elif metric == "memory":
            consumers.sort(key=lambda x: x["avg_memory"], reverse=True)
        elif metric == "network":
            consumers.sort(key=lambda x: x["total_network"], reverse=True)
        
        return consumers[:limit]
    
    async def compare_containers(
        self,
        container_ids: List[str],
        metric: str = "cpu",
        period: str = "1h",
    ) -> Dict[str, Any]:
        now = datetime.utcnow()
        delta = {"1h": timedelta(hours=1), "24h": timedelta(hours=24), "7d": timedelta(days=7)}.get(
            period, timedelta(hours=1)
        )
        start_time = now - delta
        
        container_results = {}
        for container_id in container_ids:
            container_stats = await self.get_container_stats_history(container_id, period, aggregate=True)
            container_results[container_id] = container_stats
        
        return {
            "container_ids": container_ids,
            "period": period,
            "metric": metric,
            "data": container_results,
            "timestamp": now,
        }
    
    async def get_resource_trends(
        self,
        metric: str = "cpu",
        period: str = "7d",
    ) -> Dict[str, Any]:
        stats = await self.get_system_stats_history(period, aggregate=True)
        
        if not stats:
            return {
                "metric": metric,
                "period": period,
                "trend": "unknown",
                "change_percent": 0,
                "data": [],
            }
        
        if len(stats) < 2:
            return {
                "metric": metric,
                "period": period,
                "trend": "stable",
                "change_percent": 0,
                "data": stats,
            }
        
        first_value = stats[0].get(f"{metric}_avg", 0) or stats[0].get(metric, 0)
        last_value = stats[-1].get(f"{metric}_avg", 0) or stats[-1].get(metric, 0)
        
        if first_value > 0:
            change_percent = ((last_value - first_value) / first_value) * 100
        else:
            change_percent = 0
        
        if change_percent > 5:
            trend = "increasing"
        elif change_percent < -5:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "metric": metric,
            "period": period,
            "trend": trend,
            "change_percent": round(change_percent, 2),
            "data": stats,
            "min_value": min(stats, key=lambda x: x.get(f"{metric}_avg", 0) or x.get(metric, 0)),
            "max_value": max(stats, key=lambda x: x.get(f"{metric}_avg", 0) or x.get(metric, 0)),
        }
    
    async def prune_old_stats(self, retention_days: int = 30) -> Dict[str, Any]:
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        system_result = await self.db.execute(
            select(func.count()).select_from(SystemStats).where(
                SystemStats.timestamp < cutoff_date
            )
        )
        system_deleted = system_result.scalar() or 0
        
        await self.db.execute(
            SystemStats.__table__.delete().where(
                SystemStats.timestamp < cutoff_date
            )
        )
        
        container_result = await self.db.execute(
            select(func.count()).select_from(ContainerStats).where(
                ContainerStats.timestamp < cutoff_date
            )
        )
        container_deleted = container_result.scalar() or 0
        
        await self.db.execute(
            ContainerStats.__table__.delete().where(
                ContainerStats.timestamp < cutoff_date
            )
        )
        
        await self.db.commit()
        
        return {
            "system_stats_deleted": system_deleted,
            "container_stats_deleted": container_deleted,
            "retention_days": retention_days,
        }
    
    async def export_stats(
        self,
        stats_type: str = "system",
        period: str = "24h",
        format: str = "json",
    ) -> Dict[str, Any]:
        if stats_type == "system":
            stats = await self.get_system_stats_history(period)
        elif stats_type == "container":
            docker_service = DockerService(self.db)
            containers = await docker_service.list_all_containers()
            stats = {}
            for container in containers[:5]:
                container_id = container.get("id")
                stats[container_id] = await self.get_container_stats_history(container_id, period)
        else:
            stats = []
        
        if format == "csv":
            return self._export_to_csv(stats, stats_type)
        
        return {
            "format": format,
            "stats_type": stats_type,
            "period": period,
            "exported_at": datetime.utcnow(),
            "data": stats,
        }
    
    def _export_to_csv(self, data: List[Dict[str, Any]], stats_type: str) -> Dict[str, str]:
        if not data:
            return {"csv": "", "error": "No data to export"}
        
        if stats_type == "system":
            headers = ["timestamp", "cpu_usage", "memory_usage", "disk_usage", "network_rx", "network_tx"]
            rows = []
            for item in data:
                rows.append([
                    item.get("timestamp", ""),
                    item.get("cpu_usage", 0),
                    item.get("memory_usage", 0),
                    item.get("disk_usage", 0),
                    item.get("network_rx", 0),
                    item.get("network_tx", 0),
                ])
        else:
            headers = ["timestamp", "cpu_usage", "memory_usage"]
            rows = []
            for item in data:
                rows.append([
                    item.get("timestamp", ""),
                    item.get("cpu_usage", 0),
                    item.get("memory_usage", 0),
                ])
        
        csv_lines = [",".join(headers)]
        for row in rows:
            csv_lines.append(",".join(str(v) for v in row))
        
        return {
            "format": "csv",
            "csv": "\n".join(csv_lines),
        }
    
    async def get_container_group_stats(self, group_id: int) -> Dict[str, Any]:
        result = await self.db.execute(
            select(ContainerGroup).where(ContainerGroup.id == group_id)
        )
        group = result.scalar_one_or_none()
        
        if not group:
            return {"error": "Group not found"}
        
        containers_result = await self.db.execute(
            select(Container).where(Container.group_id == group_id)
        )
        containers = containers_result.scalars().all()
        
        docker_service = DockerService(self.db)
        container_list = await docker_service.list_all_containers()
        
        group_cpu = 0
        group_memory = 0
        running_count = 0
        stopped_count = 0
        
        for container in containers:
            container_info = next((c for c in container_list if c.get("id") == container.container_id), None)
            if container_info:
                stats = await docker_service.get_container_stats_formatted(container.container_id)
                if "error" not in stats:
                    group_cpu += stats.get("cpu_usage", 0)
                    group_memory += stats.get("memory_usage", 0)
                
                if container_info.get("status") == "running":
                    running_count += 1
                else:
                    stopped_count += 1
        
        return {
            "group_id": group.id,
            "group_name": group.name,
            "total_containers": len(containers),
            "running_containers": running_count,
            "stopped_containers": stopped_count,
            "total_cpu_usage": group_cpu,
            "total_memory_usage": group_memory,
            "containers": [
                {"id": c.container_id, "name": c.name, "status": c.status}
                for c in containers
            ],
        }
