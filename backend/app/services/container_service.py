"""Container management service."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.container import Container
from app.models.container_group import ContainerGroup
from app.schemas import ContainerGroupCreate, ContainerGroupUpdate, ContainerResponse


class ContainerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_containers(
        self, all_containers: bool = False, group_id: Optional[int] = None
    ) -> List[Container]:
        query = select(Container)

        if not all_containers:
            query = query.where(Container.status == "running")

        if group_id:
            query = query.where(Container.group_id == group_id)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def sync_containers(self):
        from app.services.docker_service import DockerService

        docker = DockerService(self.db)
        containers = await docker.list_all_containers()

        for container_data in containers:
            result = await self.db.execute(
                select(Container).where(Container.container_id == container_data["id"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                existing.name = container_data["name"]
                existing.image = container_data["image"]
                existing.status = container_data["status"]
            else:
                container = Container(
                    container_id=container_data["id"],
                    name=container_data["name"],
                    image=container_data["image"],
                    status=container_data["status"],
                    docker_compose_path=container_data.get("compose_file"),
                )
                self.db.add(container)

        await self.db.commit()

    async def list_groups(self) -> List[ContainerGroup]:
        result = await self.db.execute(select(ContainerGroup))
        return result.scalars().all()

    async def create_group(self, group_data: ContainerGroupCreate) -> ContainerGroup:
        group = ContainerGroup(**group_data.model_dump())
        self.db.add(group)
        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def update_group(
        self, group_id: int, group_data: ContainerGroupUpdate
    ) -> Optional[ContainerGroup]:
        result = await self.db.execute(select(ContainerGroup).where(ContainerGroup.id == group_id))
        group = result.scalar_one_or_none()

        if not group:
            return None

        update_data = group_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(group, field, value)

        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def delete_group(self, group_id: int) -> bool:
        result = await self.db.execute(select(ContainerGroup).where(ContainerGroup.id == group_id))
        group = result.scalar_one_or_none()

        if not group:
            return False

        await self.db.delete(group)
        await self.db.commit()
        return True
