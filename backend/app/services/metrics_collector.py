import asyncio
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings
from app.services.stats_service import StatsService
from app.services.docker_service import DockerService

logger = logging.getLogger(__name__)

class MetricsCollector:
    def __init__(self):
        self.engine = create_async_engine(settings.DATABASE_URL, echo=False)
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)
        self.interval = 60  # seconds
        self._running = False
        self._task = None

    async def start(self):
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._collection_loop())
        logger.info(f"Metrics collection background task started (interval: {self.interval}s)")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        await self.engine.dispose()
        logger.info("Metrics collection background task stopped")

    async def _collection_loop(self):
        while self._running:
            try:
                async with self.async_session() as session:
                    stats_service = StatsService(session)
                    docker_service = DockerService(session)
                    
                    # 1. Collect System Stats
                    logger.debug("Collecting system stats...")
                    await stats_service.collect_and_store_system_stats()
                    
                    # 2. Collect Container Stats for running containers
                    logger.debug("Collecting container stats...")
                    containers = await docker_service.list_all_containers(all_containers=False)
                    for container in containers:
                        container_id = container.get("container_id")
                        if container_id:
                            await stats_service.collect_and_store_container_stats(container_id)
                    
                    await session.commit()
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
            
            await asyncio.sleep(self.interval)

metrics_collector = MetricsCollector()
