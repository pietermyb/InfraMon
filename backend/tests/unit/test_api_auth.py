"""Unit tests for InfraMon backend authentication API."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint returns 200."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_login_invalid_username(client: AsyncClient):
    """Test login with invalid username returns 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "nonexistent", "password": "testpassword"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    """Test get_me without auth returns 401."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_invalid_token(client: AsyncClient):
    """Test get_me with invalid token returns 401."""
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_change_password_unauthenticated(client: AsyncClient):
    """Test change password without auth returns 401."""
    response = await client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": "testpassword",
            "new_password": "newpassword123"
        }
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_containers_unauthorized(client: AsyncClient):
    """Test list containers without auth returns 401."""
    response = await client.get("/api/v1/containers")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_container_unauthorized(client: AsyncClient):
    """Test get container without auth returns 401."""
    response = await client.get("/api/v1/containers/123")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_stats_system_unauthorized(client: AsyncClient):
    """Test stats system without auth returns 401."""
    response = await client.get("/api/v1/stats/system")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dashboard_unauthorized(client: AsyncClient):
    """Test dashboard without auth returns 401."""
    response = await client.get("/api/v1/stats/dashboard")
    assert response.status_code == 401
