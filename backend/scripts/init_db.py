"""Database initialization and seeding script."""

import asyncio
import secrets
import string
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


DATABASE_URL = "sqlite+aiosqlite:///./inframon.db"


def generate_secure_password(length: int = 32) -> str:
    """Generate a cryptographically secure random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in "!@#$%^&*" for c in password)
        ):
            return password


async def init_database():
    """Initialize database with tables and seed data."""
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        from app.db.database import Base

        await conn.run_sync(Base.metadata.create_all)

    print("Database tables created successfully!")

    async with async_session() as session:
        from passlib.context import CryptContext

        from app.models.container_group import ContainerGroup
        from app.models.user import User

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        admin_username = "admin"
        result = await session.execute(
            text("SELECT id FROM users WHERE username = :username"), {"username": admin_username}
        )
        existing_admin = result.scalar_one_or_none()

        if not existing_admin:
            admin_password = generate_secure_password()

            admin_user = User(
                username=admin_username,
                email="admin@example.com",
                hashed_password=pwd_context.hash(admin_password),
                is_active=True,
                is_superuser=True,
            )
            session.add(admin_user)
            await session.commit()

            print(f"\n{'='*60}")
            print(f"ADMIN USER CREATED!")
            print(f"{'='*60}")
            print(f"Username: {admin_username}")
            print(f"Password: {admin_password}")
            print(f"{'='*60}")
            print("IMPORTANT: Save this password securely!")
            print("It will only be shown once.")
            print(f"{'='*60}\n")
        else:
            print(f"\nAdmin user '{admin_username}' already exists.")

        default_groups = [
            {
                "name": "Frontend",
                "description": "Frontend application containers",
                "color": "#3B82F6",
            },
            {"name": "Backend", "description": "Backend API containers", "color": "#10B981"},
            {"name": "Database", "description": "Database containers", "color": "#F59E0B"},
            {
                "name": "Monitoring",
                "description": "Monitoring and observability tools",
                "color": "#EF4444",
            },
            {
                "name": "DevTools",
                "description": "Development and auxiliary tools",
                "color": "#8B5CF6",
            },
        ]

        for group_data in default_groups:
            result = await session.execute(
                text("SELECT id FROM container_groups WHERE name = :name"),
                {"name": group_data["name"]},
            )
            existing = result.scalar_one_or_none()

            if not existing:
                group = ContainerGroup(**group_data)
                session.add(group)
                print(f"Created container group: {group_data['name']}")

        await session.commit()
        print("\nDefault container groups created!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())
