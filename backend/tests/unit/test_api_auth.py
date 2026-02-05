import pytest
from httpx import AsyncClient
from unittest.mock import patch
from app.core.auth import create_access_token, get_password_hash


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["username"] == "testuser"


@pytest.mark.asyncio
async def test_login_invalid_username(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "nonexistent", "password": "testpassword"}
    )
    assert response.status_code == 401
    data = response.json()
    assert "Incorrect username or password" in data["detail"]


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, test_user):
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    data = response.json()
    assert "Incorrect username or password" in data["detail"]


@pytest.mark.asyncio
async def test_login_inactive_user(client: AsyncClient, test_db):
    from app.models.user import User
    from sqlalchemy import select
    
    result = await test_db.execute(select(User).where(User.username == "testuser"))
    user = result.scalar_one_or_none()
    user.is_active = False
    await test_db.commit()
    
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 400
    data = response.json()
    assert "inactive" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_me_authenticated(client: AsyncClient, auth_headers, test_user):
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_invalid_token(client: AsyncClient):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_change_password_success(client: AsyncClient, auth_headers, test_db, test_user):
    response = await client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "testpassword",
            "new_password": "newpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "Password updated successfully" in data["message"]


@pytest.mark.asyncio
async def test_change_password_wrong_current(client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert "Incorrect current password" in data["detail"]


@pytest.mark.asyncio
async def test_change_password_unauthenticated(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": "testpassword",
            "new_password": "newpassword123"
        }
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
