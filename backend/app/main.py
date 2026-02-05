import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.security import (
    InputSanitizationMiddleware,
    RateLimitMiddleware,
    RequestSizeMiddleware,
    SecurityHeadersMiddleware,
)
from app.db.database import close_db, init_db

LOG_LEVEL = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


async def create_admin_user():
    """Create admin user if it doesn't exist."""
    try:
        import secrets
        import string

        from passlib.context import CryptContext
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        async with async_session() as session:
            result = await session.execute(
                text("SELECT id FROM users WHERE username = :username"),
                {"username": settings.ADMIN_USERNAME},
            )
            existing = result.scalar_one_or_none()

            if not existing:
                if not settings.ADMIN_PASSWORD:
                    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
                    admin_password = "".join(secrets.choice(alphabet) for _ in range(32))
                else:
                    admin_password = settings.ADMIN_PASSWORD[:72]

                from app.models.user import User

                admin_user = User(
                    username=settings.ADMIN_USERNAME,
                    email="admin@example.com",
                    hashed_password=pwd_context.hash(admin_password),
                    is_active=True,
                    is_superuser=True,
                )
                session.add(admin_user)
                await session.commit()
                logger.info(
                    f"Admin user '{settings.ADMIN_USERNAME}' created with generated password"
                )
                logger.info(f"ADMIN_PASSWORD={admin_password}")
            else:
                logger.info("Admin user already exists")

        await engine.dispose()
    except Exception as e:
        logger.warning(f"Could not create admin user: {e}")


async def create_default_groups():
    """Create default container groups if they don't exist."""
    try:
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

        from app.models.container_group import ContainerGroup

        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        async_session = async_sessionmaker(engine, expire_on_commit=False)

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

        async with async_session() as session:
            for group_data in default_groups:
                result = await session.execute(
                    text("SELECT id FROM container_groups WHERE name = :name"),
                    {"name": group_data["name"]},
                )
                existing = result.scalar_one_or_none()

                if not existing:
                    group = ContainerGroup(**group_data)
                    session.add(group)
                    logger.info(f"Created container group: {group_data['name']}")

            await session.commit()

        await engine.dispose()
    except Exception as e:
        logger.warning(f"Could not create default groups: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting InfraMon Backend Application...")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Database: {settings.DATABASE_URL}")

    await init_db()
    logger.info("Database initialized successfully")

    await create_admin_user()
    await create_default_groups()

    # Start metrics collection background task
    from app.services.metrics_collector import metrics_collector

    await metrics_collector.start()

    yield

    # Stop metrics collection background task
    from app.services.metrics_collector import metrics_collector

    await metrics_collector.stop()

    logger.info("Shutting down InfraMon Backend Application...")
    await close_db()
    logger.info("Database connections closed")


app = FastAPI(
    title="InfraMon API",
    description="Docker Container Monitoring and Management System",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.CORS_ALLOW_ALL else settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeMiddleware)
app.add_middleware(InputSanitizationMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/")
async def root():
    return {
        "name": "InfraMon",
        "version": "0.1.0",
        "description": "Docker Container Monitoring and Management System",
        "api_docs": "/api/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
