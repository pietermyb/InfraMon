"""Repository pattern implementation for database operations."""

from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

ModelType = TypeVar("ModelType")


class Repository(Generic[ModelType]):
    """Generic repository for CRUD operations."""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: Any) -> Optional[ModelType]:
        """Get a single record by ID."""
        result = await self.session.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_by(self, **kwargs) -> Optional[ModelType]:
        """Get a single record by keyword arguments."""
        result = await self.session.execute(select(self.model).filter_by(**kwargs))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination."""
        result = await self.session.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def count(self) -> int:
        """Count all records."""
        result = await self.session.execute(select(func.count()).select_from(self.model))
        return result.scalar()

    async def create(self, **kwargs) -> ModelType:
        """Create a new record."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: Any, **kwargs) -> Optional[ModelType]:
        """Update a record by ID."""
        await self.session.execute(update(self.model).where(self.model.id == id).values(**kwargs))
        await self.session.commit()
        return await self.get(id)

    async def delete(self, id: Any) -> bool:
        """Delete a record by ID."""
        result = await self.session.execute(delete(self.model).where(self.model.id == id))
        await self.session.commit()
        return result.rowcount > 0

    async def exists(self, **kwargs) -> bool:
        """Check if a record exists."""
        result = await self.session.execute(select(self.model).filter_by(**kwargs).exists())
        return await self.session.scalar(result)

    async def filter(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        descending: bool = False,
        **kwargs,
    ) -> List[ModelType]:
        """Filter records with various options."""
        query = select(self.model)

        if kwargs:
            for key, value in kwargs.items():
                query = query.where(getattr(self.model, key) == value)

        query = query.offset(skip).limit(limit)

        if order_by:
            if descending:
                query = query.order_by(getattr(self.model, order_by).desc())
            else:
                query = query.order_by(getattr(self.model, order_by).asc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def bulk_create(self, instances: List[ModelType]) -> List[ModelType]:
        """Create multiple records at once."""
        self.session.add_all(instances)
        await self.session.commit()
        for instance in instances:
            await self.session.refresh(instance)
        return instances
