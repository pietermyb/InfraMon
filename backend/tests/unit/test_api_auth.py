"""Unit tests for InfraMon backend authentication API."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Test successful login with valid credentials."""
    response = await client.post(
        "/api/v1/auth/login", json={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["username"] == "testuser"


@pytest.mark.asyncio
async def test_login_invalid_username(client: AsyncClient):
    """Test login with invalid username returns 401."""
    response = await client.post(
        "/api/v1/auth/login", json={"username": "nonexistent", "password": "testpassword"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, test_user):
    """Test login with invalid password returns 401."""
    response = await client.post(
        "/api/v1/auth/login", json={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_missing_username(client: AsyncClient):
    """Test login with missing username returns 422."""
    response = await client.post("/api/v1/auth/login", json={"password": "testpassword"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_missing_password(client: AsyncClient):
    """Test login with missing password returns 422."""
    response = await client.post("/api/v1/auth/login", json={"username": "testuser"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_me_success(client: AsyncClient, auth_headers, test_user):
    """Test get current user with valid token."""
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    """Test get_me without auth returns 401."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_invalid_token(client: AsyncClient):
    """Test get_me with invalid token returns 401."""
    response = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_change_password_success(client: AsyncClient, auth_headers, test_user):
    """Test password change with valid credentials."""
    response = await client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "testpassword",
            "new_password": "newpassword123",
            "new_password_confirm": "newpassword123",
        },
    )
    assert response.status_code == 200
    assert "successfully" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_change_password_wrong_current(client: AsyncClient, auth_headers):
    """Test password change with wrong current password."""
    response = await client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "wrongpassword",
            "new_password": "newpassword123",
            "new_password_confirm": "newpassword123",
        },
    )
    assert response.status_code == 400
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_change_password_unauthenticated(client: AsyncClient):
    """Test change password without auth returns 401."""
    response = await client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": "testpassword",
            "new_password": "newpassword123",
            "new_password_confirm": "newpassword123",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_change_password_missing_fields(client: AsyncClient, auth_headers):
    """Test password change with missing fields."""
    response = await client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={"current_password": "testpassword"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_change_password_mismatch(client: AsyncClient, auth_headers):
    """Test password change with mismatched confirm password."""
    response = await client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "testpassword",
            "new_password": "newpassword123",
            "new_password_confirm": "differentpassword",
        },
    )
    assert response.status_code == 422


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
