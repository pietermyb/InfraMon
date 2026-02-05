import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_superuser(test_db):
    from app.models.user import User
    from app.core.auth import get_password_hash
    from sqlalchemy import select
    
    result = test_db.execute(select(User).where(User.username == "admin"))
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
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def admin_auth_headers(mock_superuser):
    from app.core.auth import create_access_token
    token = create_access_token(data={"sub": mock_superuser.username, "user_id": mock_superuser.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_list_groups_empty(client: AsyncClient, auth_headers):
    with patch("app.services.container_service.ContainerService") as MockService:
        mock_instance = MagicMock()
        mock_instance.list_groups.return_value = []
        MockService.return_value = mock_instance
        
        response = await client.get("/api/v1/groups", headers=auth_headers)
        
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_groups_with_data(client: AsyncClient, auth_headers):
    with patch("app.services.container_service.ContainerService") as MockService:
        mock_group = MagicMock()
        mock_group.id = 1
        mock_group.name = "Test Group"
        mock_group.description = "Test Description"
        mock_group.color = "#FF0000"
        mock_group.created_at = MagicMock()
        mock_instance = MagicMock()
        mock_instance.list_groups.return_value = [mock_group]
        MockService.return_value = mock_instance
        
        response = await client.get("/api/v1/groups", headers=auth_headers)
        
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_group(client: AsyncClient, admin_auth_headers):
    with patch("app.services.container_service.ContainerService") as MockService:
        mock_group = MagicMock()
        mock_group.id = 1
        mock_group.name = "New Group"
        mock_group.description = "New Description"
        mock_group.color = "#00FF00"
        mock_instance = MagicMock()
        mock_instance.create_group.return_value = mock_group
        MockService.return_value = mock_instance
        
        response = await client.post(
            "/api/v1/groups",
            headers=admin_auth_headers,
            json={
                "name": "New Group",
                "description": "New Description",
                "color": "#00FF00"
            }
        )
        
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_group_unauthorized(client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/v1/groups",
        headers=auth_headers,
        json={
            "name": "New Group",
            "description": "New Description"
        }
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_group(client: AsyncClient, admin_auth_headers):
    with patch("app.services.container_service.ContainerService") as MockService:
        mock_group = MagicMock()
        mock_group.id = 1
        mock_group.name = "Updated Group"
        mock_instance = MagicMock()
        mock_instance.update_group.return_value = mock_group
        MockService.return_value = mock_instance
        
        response = await client.put(
            "/api/v1/groups/1",
            headers=admin_auth_headers,
            json={"name": "Updated Group", "color": "#0000FF"}
        )
        
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_group_not_found(client: AsyncClient, admin_auth_headers):
    with patch("app.services.container_service.ContainerService") as MockService:
        mock_instance = MagicMock()
        mock_instance.update_group.return_value = None
        MockService.return_value = mock_instance
        
        response = await client.put(
            "/api/v1/groups/999",
            headers=admin_auth_headers,
            json={"name": "Updated Group"}
        )
        
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_group(client: AsyncClient, admin_auth_headers):
    with patch("app.services.container_service.ContainerService") as MockService:
        mock_instance = MagicMock()
        mock_instance.delete_group.return_value = True
        MockService.return_value = mock_instance
        
        response = await client.delete("/api/v1/groups/1", headers=admin_auth_headers)
        
        assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_group_not_found(client: AsyncClient, admin_auth_headers):
    with patch("app.services.container_service.ContainerService") as MockService:
        mock_instance = MagicMock()
        mock_instance.delete_group.return_value = False
        MockService.return_value = mock_instance
        
        response = await client.delete("/api/v1/groups/999", headers=admin_auth_headers)
        
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_groups_unauthorized(client: AsyncClient):
    response = await client.get("/api/v1/groups")
    assert response.status_code == 401
