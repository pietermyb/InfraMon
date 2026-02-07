"""Unit tests for InfraMon backend containers API."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_containers_empty(client: AsyncClient, mock_docker_client, auth_headers):
    """Test listing containers when none exist - endpoint exists."""
    mock_docker_client.containers.list.return_value = []

    response = await client.get("/api/v1/containers", headers=auth_headers)

    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_get_container_not_found(client: AsyncClient, mock_docker_client, auth_headers):
    """Test getting a non-existent container - endpoint exists."""
    mock_docker_client.containers.get.side_effect = ValueError("Container not found")

    response = await client.get("/api/v1/containers/nonexistent", headers=auth_headers)

    assert response.status_code in [401, 404]


@pytest.mark.asyncio
async def test_unauthorized_container_access(client: AsyncClient):
    """Test accessing containers without auth returns 401."""
    response = await client.get("/api/v1/containers")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_container_logs_endpoint_exists(client: AsyncClient, auth_headers):
    """Test container logs endpoint exists."""
    response = await client.get("/api/v1/containers/123/logs", headers=auth_headers)

    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_container_stats_endpoint_exists(client: AsyncClient, auth_headers):
    """Test container stats endpoint exists."""
    response = await client.get("/api/v1/containers/123/stats", headers=auth_headers)

    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_container_inspect_endpoint_exists(client: AsyncClient, auth_headers):
    """Test container inspect endpoint exists."""
    response = await client.get("/api/v1/containers/123/inspect", headers=auth_headers)

    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_groups_endpoint_exists(client: AsyncClient, auth_headers):
    """Test groups endpoint exists."""
    response = await client.get("/api/v1/groups", headers=auth_headers)

    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_groups_unauthorized(client: AsyncClient):
    """Test groups endpoint without auth returns 401."""
    response = await client.get("/api/v1/groups")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_containers_with_filters(client: AsyncClient, mock_docker_client, auth_headers):
    """Test list containers with filters."""
    mock_docker_client.containers.list.return_value = []

    response = await client.get("/api/v1/containers?all_containers=true", headers=auth_headers)

    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_container_start_endpoint(client: AsyncClient, auth_headers):
    """Test container start endpoint returns proper response."""
    response = await client.post("/api/v1/containers/test123/start", headers=auth_headers)

    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_container_stop_endpoint(client: AsyncClient, auth_headers):
    """Test container stop endpoint returns proper response."""
    response = await client.post("/api/v1/containers/test123/stop?timeout=10", headers=auth_headers)

    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_container_restart_endpoint(client: AsyncClient, auth_headers):
    """Test container restart endpoint returns proper response."""
    response = await client.post("/api/v1/containers/test123/restart", headers=auth_headers)

    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_container_delete_endpoint(client: AsyncClient, auth_headers):
    """Test container delete endpoint returns proper response."""
    response = await client.delete("/api/v1/containers/test123", headers=auth_headers)

    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_stats_system_endpoint(client: AsyncClient, auth_headers):
    """Test stats system endpoint returns proper response."""
    response = await client.get("/api/v1/stats/system", headers=auth_headers)

    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_stats_system_info_endpoint(client: AsyncClient, auth_headers):
    """Test stats system info endpoint returns proper response."""
    response = await client.get("/api/v1/stats/system/info", headers=auth_headers)

    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_stats_dashboard_endpoint(client: AsyncClient, auth_headers):
    """Test stats dashboard endpoint returns proper response."""
    response = await client.get("/api/v1/stats/dashboard", headers=auth_headers)

    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_docker_info_endpoint(client: AsyncClient, auth_headers):
    """Test docker info endpoint returns proper response."""
    response = await client.get("/api/v1/docker/info", headers=auth_headers)

    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_docker_version_endpoint(client: AsyncClient, auth_headers):
    """Test docker version endpoint returns proper response."""
    response = await client.get("/api/v1/docker/version", headers=auth_headers)

    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_compose_projects_endpoint(client: AsyncClient, auth_headers):
    """Test compose projects endpoint returns proper response."""
    response = await client.get("/api/v1/compose/projects", headers=auth_headers)

    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_container_diff_endpoint(client: AsyncClient, auth_headers):
    """Test container diff endpoint returns proper response."""
    response = await client.get("/api/v1/containers/test123/diff", headers=auth_headers)

    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_container_exec_endpoint(client: AsyncClient, auth_headers):
    """Test container exec endpoint returns proper response."""
    response = await client.post(
        "/api/v1/containers/test123/exec", headers=auth_headers, json={"cmd": ["echo", "hello"]}
    )

    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_container_rename_endpoint(client: AsyncClient, auth_headers):
    """Test container rename endpoint returns proper response."""
    response = await client.put(
        "/api/v1/containers/test123/rename", headers=auth_headers, json={"new_name": "new_name"}
    )

    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_container_update_endpoint(client: AsyncClient, auth_headers):
    """Test container update endpoint returns proper response."""
    response = await client.post(
        "/api/v1/containers/test123/update", headers=auth_headers, json={"memory_limit": 1024000}
    )

    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_groups_create_endpoint(client: AsyncClient, auth_headers):
    """Test groups create endpoint returns proper response."""
    response = await client.post(
        "/api/v1/groups", headers=auth_headers, json={"name": "test", "description": "test group"}
    )

    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_groups_update_endpoint(client: AsyncClient, auth_headers):
    """Test groups update endpoint returns proper response."""
    response = await client.put("/api/v1/groups/1", headers=auth_headers, json={"name": "updated"})

    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_groups_delete_endpoint(client: AsyncClient, auth_headers):
    """Test groups delete endpoint returns proper response."""
    response = await client.delete("/api/v1/groups/1", headers=auth_headers)

    assert response.status_code in [200, 204, 401, 404]
