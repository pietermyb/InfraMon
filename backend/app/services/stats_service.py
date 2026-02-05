"""Statistics service for system and container metrics."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from typing import Dict, Any, List
import psutil
import os


class StatsService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_current_system_stats(self) -> Dict[str, Any]:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        network = psutil.net_io_counters()
        load_avg = os.getloadavg()
        uptime = psutil.boot_time()
        
        return {
            "id": 0,
            "cpu_usage": cpu_percent,
            "memory_usage": memory.percent,
            "memory_total": memory.total,
            "disk_usage": disk.percent,
            "disk_total": disk.total,
            "network_rx": network.bytes_recv,
            "network_tx": network.bytes_sent,
            "load_avg_1m": load_avg[0],
            "load_avg_5m": load_avg[1],
            "load_avg_15m": load_avg[2],
            "uptime": datetime.now().timestamp() - uptime,
            "timestamp": datetime.utcnow(),
        }
    
    async def get_dashboard_summary(self) -> Dict[str, Any]:
        system_stats = await self.get_current_system_stats()
        
        return {
            "system": system_stats,
            "containers": {
                "total": 0,
                "running": 0,
                "stopped": 0,
                "paused": 0,
            },
            "resources": {
                "cpu_cores": psutil.cpu_count(),
                "total_memory": memory.total,
                "total_disk": disk.total,
            },
            "uptime": system_stats["uptime"],
        }
