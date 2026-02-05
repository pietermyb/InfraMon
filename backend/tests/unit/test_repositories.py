"""Unit tests for database repositories - simplified."""


class TestUserRepository:
    """Tests for user repository."""

    def test_user_repository_import(self):
        """Test user repository can be imported."""
        from app.db.user_repository import UserRepository

        assert UserRepository is not None


class TestContainerRepository:
    """Tests for container repository."""

    def test_container_repository_import(self):
        """Test container repository can be imported."""
        from app.db.container_repository import ContainerRepository

        assert ContainerRepository is not None


class TestRepository:
    """Tests for base repository."""

    def test_repository_import(self):
        """Test base repository can be imported."""
        from app.db.repository import Repository

        assert Repository is not None


class TestDatabaseModule:
    """Tests for database module."""

    def test_database_import(self):
        """Test database module can be imported."""
        from app.db.database import async_sessionmaker, engine, get_db

        assert engine is not None
        assert async_sessionmaker is not None
        assert get_db is not None

    def test_engine_is_initialized(self):
        """Test database engine is initialized."""
        from app.db.database import engine

        assert engine is not None

    def test_async_sessionmaker_exists(self):
        """Test async session maker exists."""
        from app.db.database import async_sessionmaker

        assert async_sessionmaker is not None
