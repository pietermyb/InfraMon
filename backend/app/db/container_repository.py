"""Container repository."""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.repository import Repository
from app.models.container import Container


class ContainerRepository(Repository[Container]):
    """Repository for Container model."""

    async def get_by_container_id(self, container_id: str) -> Optional[Container]:
        """Get container by Docker container ID."""
        return await self.get_by(container_id=container_id)

    async def get_by_name(self, name: str) -> Optional[Container]:
        """Get container by name."""
        return await self.get_by(name=name)

    async def get_by_status(self, status: str) -> List[Container]:
        """Get all containers with a specific status."""
        return await self.filter(status=status)

    async def get_by_group(self, group_id: int) -> List[Container]:
        """Get all containers in a group."""
        return await self.filter(group_id=group_id)

    async def get_running_count(self) -> int:
        """Count running containers."""
        result = await self.session.execute(
            select(func.count()).select_from(Container).where(Container.status == "running")
        )
        return result.scalar() or 0

    async def get_total_count(self) -> int:
        """Count total containers."""
        return await self.count()

    async def get_stats_summary(self) -> dict:
        """Get container statistics summary."""
        running = await self.get_running_count()
        total = await self.get_total_count()
        return {
            "total": total,
            "running": running,
            "stopped": total - running,
        }


def get_container_repository(session: AsyncSession) -> ContainerRepository:
    """Factory function for ContainerRepository."""
    return ContainerRepository(Container, session)
