import pytest
from unittest.mock import MagicMock, patch


class TestDockerServiceUnit:
    def test_docker_client_initialization(self, mock_docker_client):
        from app.services.docker_service import DockerService
        
        service = DockerService(None)
        assert service is not None
    
    def test_list_all_containers_empty(self, mock_docker_client):
        mock_docker_client.containers.list.return_value = []
        
        from app.services.docker_service import DockerService
        import asyncio
        
        service = DockerService(None)
        containers = asyncio.get_event_loop().run_until_complete(
            service.list_all_containers(all_containers=False)
        )
        
        assert containers == []
    
    def test_inspect_container_returns_data(self, mock_docker_client):
        from app.services.docker_service import DockerService
        import asyncio
        
        service = DockerService(None)
        container = asyncio.get_event_loop().run_until_complete(
            service.inspect_container("123")
        )
        
        assert container is not None
        assert container["id"] == "123"
    
    def test_get_logs_success(self, mock_docker_client):
        from app.services.docker_service import DockerService
        import asyncio
        
        container = mock_docker_client.containers.get.return_value
        container.logs.return_value = b"Test log line\n"
        
        service = DockerService(None)
        logs = asyncio.get_event_loop().run_until_complete(
            service.get_logs("123", stdout=True, stderr=True, tail="100")
        )
        
        assert logs is not None
    
    def test_container_stats_formatting(self, mock_docker_client):
        from app.services.docker_service import DockerService
        import asyncio
        
        container = mock_docker_client.containers.get.return_value
        container.stats.return_value = {
            "cpu_stats": {
                "cpu_usage": {"total_usage": 2000, "system_cpu_usage": 10000},
                "online_cpus": 4
            },
            "memory_stats": {
                "usage": 500000000,
                "limit": 1000000000
            },
            "networks": {},
            "blkio_stats": {}
        }
        
        service = DockerService(None)
        stats = asyncio.get_event_loop().run_until_complete(
            service.get_container_stats_formatted("123")
        )
        
        assert stats is not None
        assert "cpu_percent" in stats


class TestContainerServiceUnit:
    def test_service_initialization(self):
        from app.services.container_service import ContainerService
        from sqlalchemy.ext.asyncio import AsyncSession
        
        service = ContainerService(MagicMock(spec=AsyncSession))
        assert service is not None


class TestStatsServiceUnit:
    def test_service_initialization(self):
        from app.services.stats_service import StatsService
        from sqlalchemy.ext.asyncio import AsyncSession
        
        service = StatsService(MagicMock(spec=AsyncSession))
        assert service is not None


class TestAuthServiceUnit:
    def test_password_hashing(self):
        from app.core.auth import get_password_hash, verify_password
        
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False
    
    def test_token_creation(self):
        from app.core.auth import create_access_token, verify_token
        import time
        
        data = {"sub": "testuser", "user_id": 1}
        token = create_access_token(data)
        
        assert token is not None
        assert len(token) > 0
        
        decoded = verify_token(token)
        assert decoded["sub"] == "testuser"
        assert decoded["user_id"] == 1
    
    def test_expired_token(self):
        from app.core.auth import create_access_token, verify_token
        from jose import jwt, JWTError
        
        data = {"sub": "testuser", "user_id": 1}
        token = create_access_token(data, expires_delta=-1)
        
        try:
            verify_token(token)
            assert False, "Should have raised JWTError"
        except JWTError:
            pass


class TestModelsUnit:
    def test_user_model_creation(self):
        from app.models.user import User
        
        user = User(
            username="test",
            email="test@test.com",
            hashed_password="hashed",
            is_active=True,
            is_superuser=False
        )
        
        assert user.username == "test"
        assert user.is_active is True
    
    def test_container_group_model_creation(self):
        from app.models.container_group import ContainerGroup
        
        group = ContainerGroup(
            name="Test Group",
            description="A test group",
            color="#FF0000"
        )
        
        assert group.name == "Test Group"
        assert group.color == "#FF0000"
    
    def test_container_model_creation(self):
        from app.models.container import Container
        
        container = Container(
            container_id="abc123",
            name="test-container",
            image="nginx:latest",
            status="running"
        )
        
        assert container.container_id == "abc123"
        assert container.status == "running"
