import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient


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
        
        net_io_mock = MagicMock()
        net_io_mock.bytes_sent = 1024000
        net_io_mock.bytes_recv = 2048000
        net_io_mock.packets_sent = 100
        net_io_mock.packets_recv = 200
        net_io_mock.errin = 0
        net_io_mock.errout = 0
        net_io_mock.dropin = 0
        net_io_mock.dropout = 0
        mock_psutil.net_io_counters.return_value = {"eth0": net_io_mock}
        
        mock_psutil.boot_time.return_value = 1672531200
        mock_psutil.cpu_count.return_value = 4
        mock_psutil.cpu_freq.return_value = MagicMock(current=2500.0)
        mock_psutil.sensors_temperatures.return_value = {}
        mock_psutil.process_iter.return_value = []
        
        yield mock_psutil


@pytest.mark.asyncio
async def test_get_system_stats(client: AsyncClient, auth_headers, mock_psutil):
    with patch("app.services.stats_service.os.getloadavg", return_value=(1.0, 1.5, 2.0)):
        response = await client.get("/api/v1/stats/system", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "cpu_usage" in data
        assert "memory_usage" in data
        assert "disk_usage" in data


@pytest.mark.asyncio
async def test_get_system_info(client: AsyncClient, auth_headers, mock_psutil):
    with patch("platform.processor", return_value="x86_64"), \
         patch("platform.system", return_value="Linux"), \
         patch("platform.release", return_value="5.15.0"):
        response = await client.get("/api/v1/stats/system/info", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "os" in data
        assert "kernel" in data


@pytest.mark.asyncio
async def test_get_disk_partitions(client: AsyncClient, auth_headers, mock_psutil):
    with patch("app.services.stats_service.psutil.disk_partitions") as mock_partitions:
        partition_mock = MagicMock()
        partition_mock.device = "/dev/sda1"
        partition_mock.mountpoint = "/"
        partition_mock.fstype = "ext4"
        partition_mock.opts = "rw,relatime"
        mock_partitions.return_value = [partition_mock]
        
        response = await client.get("/api/v1/stats/system/disk", headers=auth_headers)
        
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_network_interfaces(client: AsyncClient, auth_headers, mock_psutil):
    response = await client.get("/api/v1/stats/system/network", headers=auth_headers)
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_network_connections(client: AsyncClient, auth_headers, mock_psutil):
    with patch("app.services.stats_service.psutil.net_connections") as mock_connections:
        conn_mock = MagicMock()
        conn_mock.fd = 0
        conn_mock.family = 2
        conn_mock.type = 1
        conn_mock.laddr = ("127.0.0.1", 8080)
        conn_mock.raddr = ()
        conn_mock.status = "LISTEN"
        conn_mock.pid = 1234
        mock_connections.return_value = [conn_mock]
        
        response = await client.get("/api/v1/stats/system/connections?kind=tcp", headers=auth_headers)
        
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_process_list(client: AsyncClient, auth_headers, mock_psutil):
    proc_mock = MagicMock()
    proc_mock.pid = 1234
    proc_mock.name.return_value = "python"
    proc_mock.cpu_percent.return_value = 5.0
    proc_mock.memory_percent.return_value = 2.5
    proc_mock.cmdline.return_value = ["python", "script.py"]
    proc_mock.username.return_value = "root"
    
    with patch("app.services.stats_service.psutil.process_iter", return_value=[proc_mock]):
        response = await client.get(
            "/api/v1/stats/system/processes?limit=10&order_by=cpu",
            headers=auth_headers
        )
        
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_system_stats_history(client: AsyncClient, auth_headers):
    response = await client.get(
        "/api/v1/stats/system/history?period=1h&aggregate=false",
        headers=auth_headers
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_dashboard_stats(client: AsyncClient, auth_headers, mock_docker_client):
    with patch("app.services.stats_service.StatsService.get_dashboard_summary") as mock_summary:
        mock_summary.return_value = {
            "total_containers": 5,
            "running_containers": 3,
            "stopped_containers": 2,
            "cpu_usage": 25.5,
            "memory_usage": 50.0,
            "disk_usage": 45.0
        }
        
        response = await client.get("/api/v1/stats/dashboard", headers=auth_headers)
        
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_container_processes(client: AsyncClient, auth_headers, mock_docker_client):
    container = mock_docker_client.containers.get.return_value
    container.top.return_value = {
        "Processes": [["root", "1234", "0", "0", "S", "python"]],
        "Titles": ["USER", "PID", "%CPU", "%MEM", "STAT", "COMMAND"]
    }
    
    response = await client.get("/api/v1/containers/123/stats/processes", headers=auth_headers)
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_container_filesystem(client: AsyncClient, auth_headers, mock_docker_client):
    container = mock_docker_client.containers.get.return_value
    container.get_stats.return_value = {
        "Filesystem": "/dev/sda1",
        "Used": 1024000,
        "Available": 512000000,
        "MountedOn": "/app"
    }
    
    response = await client.get("/api/v1/containers/123/stats/filesystem", headers=auth_headers)
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_container_stats_history(client: AsyncClient, auth_headers):
    response = await client.get(
        "/api/v1/containers/123/stats/history?period=1h&aggregate=false",
        headers=auth_headers
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_top_consumers(client: AsyncClient, auth_headers):
    response = await client.get(
        "/api/v1/stats/top-consumers?metric=cpu&limit=10&period=1h",
        headers=auth_headers
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_compare_containers(client: AsyncClient, auth_headers):
    response = await client.get(
        "/api/v1/stats/compare?container_ids=abc123&container_ids=def456&metric=cpu&period=1h",
        headers=auth_headers
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_resource_trends(client: AsyncClient, auth_headers):
    response = await client.get(
        "/api/v1/stats/trends?metric=cpu&period=7d",
        headers=auth_headers
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_prune_stats(client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/v1/stats/prune?retention_days=30",
        headers=auth_headers
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_export_stats_json(client: AsyncClient, auth_headers):
    response = await client.get(
        "/api/v1/stats/export?stats_type=system&period=24h&format=json",
        headers=auth_headers
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_export_stats_csv(client: AsyncClient, auth_headers):
    response = await client.get(
        "/api/v1/stats/export?stats_type=container&period=24h&format=csv",
        headers=auth_headers
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_group_stats(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/stats/groups/1", headers=auth_headers)
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_unauthorized_stats_access(client: AsyncClient):
    response = await client.get("/api/v1/stats/system")
    assert response.status_code == 401
