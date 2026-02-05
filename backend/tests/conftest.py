import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, patch

from app.main import app
from app.db.database import Base, get_db
from app.core.config import settings


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session_factory = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        yield session


@pytest.fixture
async def client(test_db) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(test_db):
    from app.models.user import User
    from app.core.auth import get_password_hash
    from sqlalchemy import select
    
    result = await test_db.execute(select(User).where(User.username == "testuser"))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        return existing_user

    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
        is_superuser=False
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    from app.core.auth import create_access_token
    token = create_access_token(data={"sub": test_user.username, "user_id": test_user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_docker_client():
    with patch("docker.DockerClient") as MockClient:
        client_instance = MockClient.return_value
        
        container_mock = MagicMock()
        container_mock.id = "123"
        container_mock.short_id = "123"
        container_mock.name = "test-container"
        container_mock.status = "running"
        container_mock.ports = {}
        container_mock.attrs = {
            "Config": {
                "Image": "nginx:latest", 
                "Labels": {}, 
                "Env": ["KEY=VALUE"],
                "Cmd": ["run"],
                "Healthcheck": {},
                "WorkingDir": "/app",
                "Entrypoint": ["/entrypoint.sh"],
                "User": "root",
                "Tty": False,
                "OpenStdin": False
            },
            "State": {
                "Status": "running", 
                "StartedAt": "2023-01-01T12:00:00Z",
                "FinishedAt": "",
                "RestartCount": 0,
                "OOMKilled": False,
                "Dead": False,
                "ExitCode": 0
            },
            "NetworkSettings": {
                "Networks": {}, 
                "IPAddress": "172.17.0.2",
                "Hostname": "test",
                "Gateway": "172.17.0.1",
                "MacAddress": "02:42:ac:11:00:02"
            },
            "HostConfig": {
                "Memory": 0,
                "MemorySwap": 0,
                "CpuShares": 0,
                "CpuPeriod": 0,
                "CpuQuota": 0,
                "BlkioWeight": 0,
                "BlkioDeviceReadBps": [],
                "BlkioDeviceWriteBps": [],
                "RestartPolicy": {"Name": "no", "MaximumRetryCount": 0}
            },
            "Created": "2023-01-01T12:00:00Z",
            "Mounts": []
        }
        container_mock.image.tags = ["nginx:latest"]
        container_mock.logs = MagicMock(return_value=b"2023-01-01 12:00:00 Test log\n")
        container_mock.diff = MagicMock(return_value=[])
        container_mock.top = MagicMock(return_value={"Processes": [], "Titles": []})
        
        client_instance.containers.list.return_value = [container_mock]
        client_instance.containers.get.return_value = container_mock
        client_instance.ping.return_value = True
        
        yield client_instance


@pytest.fixture
def mock_psutil():
    with patch("app.services.stats_service.psutil") as mock_psutil:
        cpu_mock = MagicMock()
        cpu_mock.return_value = 25.5
        mock_psutil.cpu_percent.return_value = cpu_mock
        
        memory_mock = MagicMock()
        memory_mock.total = 17179869184
        memory_mock.used = 8589934592
        memory_mock.available = 8589934592
        memory_mock.percent = 50.0
        memory_mock.swapped.used = 0
        memory_mock.swapped.total = 0
        mock_psutil.virtual_memory.return_value = memory_mock
        
        disk_mock = MagicMock()
        disk_mock.total = 512000000000
        disk_mock.used = 256000000000
        disk_mock.free = 256000000000
        disk_mock.percent = 50.0
        mock_psutil.disk_usage.return_value = disk_mock
        
        io_mock = MagicMock()
        io_mock.read_bytes = 1024000
        io_mock.write_bytes = 512000
        io_mock.read_count = 100
        io_mock.write_count = 50
        mock_psutil.disk_io_counters.return_value = io_mock
        
        net_mock = MagicMock()
        net_mock.bytes_sent = 1024000
        net_mock.bytes_recv = 2048000
        net_mock.packets_sent = 100
        net_mock.packets_recv = 200
        net_mock.errin = 0
        net_mock.errout = 0
        net_mock.dropin = 0
        net_mock.dropout = 0
        mock_psutil.net_io_counters.return_value = {"eth0": net_mock}
        
        mock_psutil.boot_time.return_value = 1672531200
        mock_psutil.cpu_count.return_value = 4
        mock_psutil.cpu_freq.return_value = MagicMock(current=2500.0)
        mock_psutil.sensors_temperatures.return_value = {}
        mock_psutil.process_iter.return_value = []
        mock_psutil.net_connections.return_value = []
        mock_psutil.disk_partitions.return_value = []
        
        yield mock_psutil


@pytest.fixture
async def test_superuser(test_db):
    from app.models.user import User
    from app.core.auth import get_password_hash
    from sqlalchemy import select
    
    result = await test_db.execute(select(User).where(User.username == "admin"))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        return existing_user
    
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword"),
        is_active=True,
        is_superuser=True
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
def admin_auth_headers(test_superuser):
    from app.core.auth import create_access_token
    token = create_access_token(data={"sub": test_superuser.username, "user_id": test_superuser.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_container_data():
    return {
        "id": "abc123def456",
        "short_id": "abc123def456",
        "name": "test-container",
        "image": "nginx:latest",
        "status": "running",
        "image_id": None,
        "created": "2023-01-01T12:00:00Z",
        "ports": {"80/tcp": {"HostIp": "0.0.0.0", "HostPort": "8080"}},
        "labels": {"app": "test"},
        "env": ["NODE_ENV=production"],
        "cmd": ["nginx", "-g", "daemon off;"],
        "volumes": ["/app/data:/data"],
        "network_settings": {
            "Networks": {
                "bridge": {
                    "IPAddress": "172.17.0.2",
                    "Gateway": "172.17.0.1"
                }
            }
        }
    }


@pytest.fixture
def sample_container_stats():
    return {
        "cpu_stats": {
            "cpu_usage": {"total_usage": 2000000000, "system_cpu_usage": 10000000000},
            "online_cpus": 4,
            "throttling_data": {"periods": 0, "throttled_periods": 0, "throttled_time": 0}
        },
        "precpu_stats": {
            "cpu_usage": {"total_usage": 1000000000, "system_cpu_usage": 5000000000}
        },
        "memory_stats": {
            "usage": 524288000,
            "limit": 1073741824,
            "active_anon": 100000,
            "inactive_anon": 200000,
            "active_file": 300000,
            "inactive_file": 400000
        },
        "networks": {
            "eth0": {
                "rx_bytes": 1024000,
                "rx_packets": 1000,
                "tx_bytes": 2048000,
                "tx_packets": 2000
            }
        },
        "blkio_stats": {
            "io_service_bytes_recursive": [],
            "io_serviced_recursive": [],
            "io_queue_recursive": [],
            "io_service_time_recursive": [],
            "io_wait_time_recursive": [],
            "io_merged_recursive": [],
            "io_time_recursive": []
        },
        "pids_stats": {"current": 15}
    }


@pytest.fixture
def sample_system_stats():
    return {
        "cpu_usage": 25.5,
        "memory_usage": 50.0,
        "memory_total": 17179869184,
        "memory_used": 8589934592,
        "memory_available": 8589934592,
        "disk_usage": 45.0,
        "disk_total": 512000000000,
        "disk_used": 256000000000,
        "disk_free": 256000000000,
        "network_bytes_sent": 1024000,
        "network_bytes_recv": 2048000,
        "load_average": (1.0, 1.5, 2.0),
        "boot_time": 1672531200
    }
