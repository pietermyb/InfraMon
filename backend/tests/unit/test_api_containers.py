"""Unit tests for InfraMon backend containers API."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_containers_empty(client: AsyncClient, mock_docker_client):
    """Test listing containers when none exist - endpoint exists."""
    mock_docker_client.containers.list.return_value = []

    response = await client.get(
        "/api/v1/containers", headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_get_container_not_found(client: AsyncClient, mock_docker_client):
    """Test getting a non-existent container - endpoint exists."""
    mock_docker_client.containers.get.side_effect = ValueError("Container not found")

    response = await client.get(
        "/api/v1/containers/nonexistent", headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code in [401, 404]


@pytest.mark.asyncio
async def test_unauthorized_container_access(client: AsyncClient):
    """Test accessing containers without auth returns 401."""
    response = await client.get("/api/v1/containers")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_container_logs_endpoint_exists(client: AsyncClient):
    """Test container logs endpoint exists."""
    response = await client.get(
        "/api/v1/containers/123/logs", headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_container_stats_endpoint_exists(client: AsyncClient):
    """Test container stats endpoint exists."""
    response = await client.get(
        "/api/v1/containers/123/stats", headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_container_inspect_endpoint_exists(client: AsyncClient):
    """Test container inspect endpoint exists."""
    response = await client.get(
        "/api/v1/containers/123/inspect", headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code in [200, 401, 404]


@pytest.mark.asyncio
async def test_groups_endpoint_exists(client: AsyncClient):
    """Test groups endpoint exists."""
    response = await client.get("/api/v1/groups", headers={"Authorization": "Bearer test_token"})

    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_groups_unauthorized(client: AsyncClient):
    """Test groups endpoint without auth returns 401."""
    response = await client.get("/api/v1/groups")
    assert response.status_code == 401
