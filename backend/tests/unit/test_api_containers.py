import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock, patch


@pytest.mark.asyncio
async def test_list_containers_empty(client: AsyncClient, auth_headers, mock_docker_client):
    mock_docker_client.containers.list.return_value = []
    
    response = await client.get("/api/v1/containers", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["containers"]) == 0
    assert data["data"]["running"] == 0


@pytest.mark.asyncio
async def test_list_containers_with_filters(client: AsyncClient, auth_headers, mock_docker_client):
    response = await client.get(
        "/api/v1/containers?all_containers=true",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_get_container_not_found(client: AsyncClient, auth_headers, mock_docker_client):
    container = mock_docker_client.containers.get.side_effect = Exception("Container not found")
    
    response = await client.get("/api/v1/containers/nonexistent", headers=auth_headers)
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_start_container_already_running(client: AsyncClient, auth_headers, mock_docker_client):
    container = mock_docker_client.containers.get.return_value
    container.status = "running"
    
    response = await client.post("/api/v1/containers/123/start", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_stop_container_not_running(client: AsyncClient, auth_headers, mock_docker_client):
    container = mock_docker_client.containers.get.return_value
    container.status = "stopped"
    
    response = await client.post("/api/v1/containers/123/stop", headers=auth_headers)
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_restart_container(client: AsyncClient, auth_headers, mock_docker_client):
    container = mock_docker_client.containers.get.return_value
    container.restart.return_value = None
    
    response = await client.post(
        "/api/v1/containers/123/restart?timeout=30&force=true",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "restarted successfully" in data["message"].lower()


@pytest.mark.asyncio
async def test_remove_container(client: AsyncClient, auth_headers, mock_docker_client):
    container = mock_docker_client.containers.get.return_value
    container.remove.return_value = None
    
    response = await client.delete(
        "/api/v1/containers/123?force=false&volumes=false",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "removed successfully" in data["message"].lower()


@pytest.mark.asyncio
async def test_pause_container(client: AsyncClient, auth_headers, mock_docker_client):
    container = mock_docker_client.containers.get.return_value
    container.pause.return_value = None
    
    response = await client.post("/api/v1/containers/123/pause", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_unpause_container(client: AsyncClient, auth_headers, mock_docker_client):
    container = mock_docker_client.containers.get.return_value
    container.unpause.return_value = None
    
    response = await client.post("/api/v1/containers/123/unpause", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_kill_container(client: AsyncClient, auth_headers, mock_docker_client):
    container = mock_docker_client.containers.get.return_value
    container.kill.return_value = None
    
    response = await client.post(
        "/api/v1/containers/123/kill?signal=SIGKILL",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_rename_container(client: AsyncClient, auth_headers, mock_docker_client):
    container = mock_docker_client.containers.get.return_value
    container.rename.return_value = None
    
    response = await client.put(
        "/api/v1/containers/123/rename",
        headers=auth_headers,
        json={"new_name": "new-container-name"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_get_container_logs(client: AsyncClient, auth_headers, mock_docker_client):
    container = mock_docker_client.containers.get.return_value
    container.logs.return_value = b"2023-01-01 12:00:00 Test log message\n"
    
    response = await client.get(
        "/api/v1/containers/123/logs?tail=100&timestamps=true",
        headers=auth_headers
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_container_inspect(client: AsyncClient, auth_headers, mock_docker_client):
    response = await client.get("/api/v1/containers/123/inspect", headers=auth_headers)
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_container_stats_formatted(client: AsyncClient, auth_headers, mock_docker_client):
    response = await client.get("/api/v1/containers/123/stats/formatted", headers=auth_headers)
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_container_diff(client: AsyncClient, auth_headers, mock_docker_client):
    container = mock_docker_client.containers.get.return_value
    container.diff.return_value = [
        {"Path": "/app/file.txt", "Kind": 0},
        {"Path": "/var/log/app.log", "Kind": 1}
    ]
    
    response = await client.get("/api/v1/containers/123/diff", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "changes" in data


@pytest.mark.asyncio
async def test_container_exec(client: AsyncClient, auth_headers, mock_docker_client):
    container = mock_docker_client.containers.get.return_value
    exec_mock = MagicMock()
    exec_mock.exec_inside.return_value = (True, "output", "")
    container.exec_run.return_value = (0, b"command output")
    
    response = await client.post(
        "/api/v1/containers/123/exec",
        headers=auth_headers,
        json={"cmd": ["echo", "hello"]}
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_init_shell(client: AsyncClient, auth_headers, mock_docker_client):
    response = await client.post(
        "/api/v1/containers/123/shell?shell=/bin/bash",
        headers=auth_headers
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_bulk_action_start(client: AsyncClient, auth_headers, mock_docker_client):
    response = await client.post(
        "/api/v1/containers/bulk-action",
        headers=auth_headers,
        json={
            "action": "start",
            "container_ids": ["123", "456"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "succeeded" in data


@pytest.mark.asyncio
async def test_bulk_action_stop(client: AsyncClient, auth_headers, mock_docker_client):
    response = await client.post(
        "/api/v1/containers/bulk-action",
        headers=auth_headers,
        json={
            "action": "stop",
            "container_ids": ["123"],
            "timeout": 30
        }
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_prune_containers(client: AsyncClient, auth_headers, mock_docker_client):
    container = mock_docker_client.containers.prune.return_value = {
        "ContainersDeleted": ["deleted-container-id"],
        "SpaceReclaimed": 1024
    }
    
    response = await client.delete("/api/v1/containers", headers=auth_headers)
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_container_update_limits(client: AsyncClient, auth_headers, mock_docker_client):
    container = mock_docker_client.containers.get.return_value
    container.update.return_value = None
    
    response = await client.patch(
        "/api/v1/containers/123",
        headers=auth_headers,
        json={"memory_limit": 536870912, "cpu_shares": 512}
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_unauthorized_container_access(client: AsyncClient):
    response = await client.get("/api/v1/containers")
    assert response.status_code == 401
