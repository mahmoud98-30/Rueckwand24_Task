from fastapi import status
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.exc import IntegrityError
from datetime import datetime


@patch("app.routers.users.hash_password")
def test_create_user_success(mock_hash, client):
    mock_hash.return_value = "hashed-password"

    # Create a proper mock user with all required fields
    fake_user = MagicMock()
    fake_user.id = 1
    fake_user.username = "john"
    fake_user.email = "john@test.com"
    fake_user.is_active = True
    fake_user.created_at = datetime.now()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    # Patch the User model to return our mock
    with patch("app.routers.users.User", return_value=fake_user):
        payload = {
            "username": "john",
            "email": "john@test.com",
            "password": "secret"
        }

        response = client.post("/api/users/", json=payload)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()

    assert body["username"] == "john"
    assert body["email"] == "john@test.com"

    client.app.dependency_overrides = {}


@patch("app.routers.users.hash_password")
def test_create_user_conflict(mock_hash, client):
    mock_hash.return_value = "hashed-password"

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.add = MagicMock()
        db.commit = AsyncMock(side_effect=IntegrityError(None, None, None))
        db.rollback = AsyncMock()
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    payload = {
        "username": "john",
        "email": "john@test.com",
        "password": "secret"
    }

    response = client.post("/api/users/", json=payload)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Username or email already exists."

    client.app.dependency_overrides = {}


@patch("app.routers.users.get_current_user")
def test_list_users(mock_user, client):
    mock_user.return_value = {"id": 1}

    fake_user = MagicMock()
    fake_user.id = 1
    fake_user.username = "john"
    fake_user.email = "john@test.com"
    fake_user.is_active = True
    fake_user.created_at = datetime.now()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = [fake_user]
        db.execute = AsyncMock(return_value=result)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.get("/api/users/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1

    client.app.dependency_overrides = {}


@patch("app.routers.users.get_current_user")
def test_get_user_success(mock_user, client):
    mock_user.return_value = {"id": 1}

    fake_user = MagicMock()
    fake_user.id = 1
    fake_user.username = "john"
    fake_user.email = "john@test.com"
    fake_user.is_active = True
    fake_user.created_at = datetime.now()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=fake_user)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.get("/api/users/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "john"

    client.app.dependency_overrides = {}

@patch("app.routers.users.get_current_user")
def test_get_user_not_found(mock_user, client):
    mock_user.return_value = {"id": 1}

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=None)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.get("/api/users/99")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

    client.app.dependency_overrides = {}


@patch("app.routers.users.get_current_user")
def test_update_user_success(mock_user, client):
    mock_user.return_value = {"id": 1}

    fake_user = MagicMock()
    fake_user.id = 1
    fake_user.username = "john"
    fake_user.email = "old@test.com"
    fake_user.is_active = True
    fake_user.created_at = datetime.now()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=fake_user)
        db.commit = AsyncMock()
        # Update the email when refresh is called
        db.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'email', 'new@test.com'))
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    payload = {"email": "new@test.com"}

    response = client.put("/api/users/1", json=payload)

    assert response.status_code == 200
    assert response.json()["email"] == "new@test.com"

    client.app.dependency_overrides = {}


@patch("app.routers.users.get_current_user")
def test_delete_user_success(mock_user, client):
    mock_user.return_value = {"id": 1}

    fake_user = MagicMock()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=fake_user)
        db.delete = AsyncMock()
        db.commit = AsyncMock()
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.delete("/api/users/1")

    assert response.status_code == 200
    assert response.json()["detail"] == "User deleted successfully"

    client.app.dependency_overrides = {}