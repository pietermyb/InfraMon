"""User repository."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from app.db.repository import Repository
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRepository(Repository[User]):
    """Repository for User model."""

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return await self.get_by(username=username)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return await self.get_by(email=email)

    async def get_active_users(self) -> list[User]:
        """Get all active users."""
        return await self.filter(is_active=True)

    async def get_superusers(self) -> list[User]:
        """Get all superuser accounts."""
        return await self.filter(is_superuser=True)

    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        is_superuser: bool = False
    ) -> User:
        """Create a new user with hashed password."""
        hashed_password = pwd_context.hash(password)
        return await self.create(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=is_superuser,
        )

    async def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        user = await self.get_by_username(username)
        if not user:
            return None
        if not pwd_context.verify(password, user.hashed_password):
            return None
        return user

    async def update_password(self, user_id: int, new_password: str) -> Optional[User]:
        """Update user password."""
        hashed_password = pwd_context.hash(new_password)
        return await self.update(user_id, hashed_password=hashed_password)

    async def deactivate(self, user_id: int) -> Optional[User]:
        """Deactivate a user account."""
        return await self.update(user_id, is_active=False)

    async def activate(self, user_id: int) -> Optional[User]:
        """Activate a user account."""
        return await self.update(user_id, is_active=True)


def get_user_repository(session: AsyncSession) -> UserRepository:
    """Factory function for UserRepository."""
    return UserRepository(User, session)
