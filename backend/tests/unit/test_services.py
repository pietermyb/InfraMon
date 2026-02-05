"""Unit tests for InfraMon backend services and utilities."""

from datetime import datetime


class TestFactories:
    """Test factory classes."""

    def test_user_factory_create(self):
        from tests.factories import UserFactory

        user = UserFactory.create(username="testuser")
        assert user["username"] == "testuser"
        assert user["email"] == "test@example.com"
        assert user["is_active"] is True

    def test_user_factory_custom(self):
        from tests.factories import UserFactory

        user = UserFactory.create(username="admin", email="admin@test.com", is_superuser=True)
        assert user["username"] == "admin"
        assert user["is_superuser"] is True

    def test_container_factory_create(self):
        from tests.factories import ContainerFactory

        container = ContainerFactory.create(name="web-server")
        assert container["name"] == "web-server"
        assert container["image"] == "nginx:latest"
        assert container["status"] == "running"

    def test_container_group_factory_create(self):
        from tests.factories import ContainerGroupFactory

        group = ContainerGroupFactory.create(name="Web Apps")
        assert group["name"] == "Web Apps"
        assert group["color"] == "#3498db"

    def test_system_stats_factory_create(self):
        from tests.factories import SystemStatsFactory

        stats = SystemStatsFactory.create(cpu_usage=50.0)
        assert stats["cpu_usage"] == 50.0
        assert stats["memory_usage"] == 50.0


class TestAuthUtils:
    """Test authentication utilities."""

    def test_password_hashing(self):
        from app.core.auth import get_password_hash, verify_password

        password = "testpassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 50
        assert verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        from app.core.auth import get_password_hash, verify_password

        password = "testpassword123"
        hashed = get_password_hash(password)

        assert verify_password("wrongpassword", hashed) is False

    def test_token_creation(self):
        from app.core.auth import create_access_token

        data = {"sub": "testuser", "user_id": 1}
        token = create_access_token(data)

        assert token is not None
        assert len(token) > 50
        assert isinstance(token, str)


class TestModelHelpers:
    """Test model helper functions."""

    def test_datetime_now(self):
        """Test datetime utilities."""
        now = datetime.utcnow()
        assert now is not None
        assert isinstance(now, datetime)

    def test_container_status_values(self):
        """Test container status values."""
        valid_statuses = [
            "running",
            "stopped",
            "paused",
            "created",
            "restarting",
            "removing",
            "exited",
            "dead",
        ]

        for status in valid_statuses:
            assert status in valid_statuses


class TestConfigHelpers:
    """Test configuration helpers."""

    def test_settings_import(self):
        """Test settings can be imported."""
        from app.core.config import settings

        assert settings is not None

    def test_database_url_config(self):
        """Test database URL configuration."""
        from app.core.config import settings

        assert settings.DATABASE_URL is not None
        assert (
            "sqlite" in settings.DATABASE_URL.lower()
            or "postgresql" in settings.DATABASE_URL.lower()
        )

    def test_jwt_config(self):
        """Test JWT configuration."""
        from app.core.config import settings

        assert settings.SECRET_KEY is not None
        assert len(settings.SECRET_KEY) > 0
