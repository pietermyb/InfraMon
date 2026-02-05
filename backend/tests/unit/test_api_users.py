import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.container_group import ContainerGroup
from app.models.container import Container
from app.core.auth import get_password_hash


@pytest.fixture
def test_superuser(test_db):
    result = test_db.execute(select(User).where(User.username == "superuser"))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        return existing_user
    
    user = User(
        username="superuser",
        email="superuser@example.com",
        hashed_password=get_password_hash("superpassword"),
        is_active=True,
        is_superuser=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def superuser_auth_headers(test_superuser):
    from app.core.auth import create_access_token
    token = create_access_token(data={"sub": test_superuser.username, "user_id": test_superuser.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_user(test_db: AsyncSession, superuser_auth_headers, client: AsyncClient):
    response = await client.post(
        "/api/v1/users",
        headers=superuser_auth_headers,
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "is_superuser": False
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    
    result = await test_db.execute(select(User).where(User.username == "newuser"))
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.email == "newuser@example.com"


@pytest.mark.asyncio
async def test_create_duplicate_user(test_db: AsyncSession, superuser_auth_headers, client: AsyncClient, test_user):
    response = await client.post(
        "/api/v1/users",
        headers=superuser_auth_headers,
        json={
            "username": "testuser",
            "email": "another@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_users(test_db: AsyncSession, superuser_auth_headers, client: AsyncClient):
    response = await client.get(
        "/api/v1/users?page=1&page_size=20",
        headers=superuser_auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "total" in data
    assert "page" in data


@pytest.mark.asyncio
async def test_list_users_filter_by_active(test_db: AsyncSession, superuser_auth_headers, client: AsyncClient):
    response = await client.get(
        "/api/v1/users?is_active=true",
        headers=superuser_auth_headers
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_user(test_db: AsyncSession, client: AsyncClient, auth_headers, test_user):
    response = await client.get(
        f"/api/v1/users/{test_user.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_get_user_not_found(test_db: AsyncSession, superuser_auth_headers, client: AsyncClient):
    response = await client.get(
        "/api/v1/users/99999",
        headers=superuser_auth_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_user(test_db: AsyncSession, client: AsyncClient, auth_headers, test_user):
    response = await client.put(
        f"/api/v1/users/{test_user.id}",
        headers=auth_headers,
        json={"username": "updateduser", "email": "updated@example.com"}
    )
    
    assert response.status_code == 200
    
    result = await test_db.execute(select(User).where(User.id == test_user.id))
    user = result.scalar_one_or_none()
    assert user.username == "updateduser"


@pytest.mark.asyncio
async def test_delete_user(test_db: AsyncSession, superuser_auth_headers, client: AsyncClient):
    new_user = User(
        username="todelete",
        email="todelete@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True,
        is_superuser=False
    )
    test_db.add(new_user)
    await test_db.commit()
    await test_db.refresh(new_user)
    
    response = await client.delete(
        f"/api/v1/users/{new_user.id}",
        headers=superuser_auth_headers
    )
    
    assert response.status_code == 204
    
    result = await test_db.execute(select(User).where(User.id == new_user.id))
    user = result.scalar_one_or_none()
    assert user is None


@pytest.mark.asyncio
async def test_delete_self_fails(test_db: AsyncSession, superuser_auth_headers, client: AsyncClient, test_superuser):
    response = await client.delete(
        f"/api/v1/users/{test_superuser.id}",
        headers=superuser_auth_headers
    )
    
    assert response.status_code == 400
    assert "Cannot delete your own account" in response.json()["detail"]


@pytest.mark.asyncio
async def test_deactivate_user(test_db: AsyncSession, superuser_auth_headers, client: AsyncClient):
    new_user = User(
        username="deactivate",
        email="deactivate@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True,
        is_superuser=False
    )
    test_db.add(new_user)
    await test_db.commit()
    await test_db.refresh(new_user)
    
    response = await client.post(
        f"/api/v1/users/{new_user.id}/deactivate",
        headers=superuser_auth_headers
    )
    
    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_activate_user(test_db: AsyncSession, superuser_auth_headers, client: AsyncClient):
    new_user = User(
        username="activate",
        email="activate@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=False,
        is_superuser=False
    )
    test_db.add(new_user)
    await test_db.commit()
    await test_db.refresh(new_user)
    
    response = await client.post(
        f"/api/v1/users/{new_user.id}/activate",
        headers=superuser_auth_headers
    )
    
    assert response.status_code == 200
    assert response.json()["is_active"] is True


@pytest.mark.asyncio
async def test_non_admin_cannot_list_users(test_db: AsyncSession, client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/users", headers=auth_headers)
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_cannot_create_user_as_regular_user(test_db: AsyncSession, client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/v1/users",
        headers=auth_headers,
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_user_cannot_delete_other_user(test_db: AsyncSession, client: AsyncClient, test_user, test_superuser, superuser_auth_headers):
    response = await client.delete(
        f"/api/v1/users/{test_superuser.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 403
