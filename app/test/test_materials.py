from fastapi import status
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.exc import IntegrityError
from datetime import datetime


@patch("app.routers.materials.get_current_user")
def test_create_material_success(mock_user, client):
    mock_user.return_value = {"id": 1}

    # Create a proper mock material with all required fields
    fake_material = MagicMock()
    fake_material.id = 1
    fake_material.name = "Wood"
    fake_material.description = "Natural wood material"
    fake_material.created_at = datetime.now()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    # Patch the Material model to return our mock
    with patch("app.routers.materials.Material", return_value=fake_material):
        payload = {
            "name": "Wood",
            "description": "Natural wood material"
        }

        response = client.post("/api/materials/", json=payload)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()

    assert body["name"] == "Wood"
    assert body["description"] == "Natural wood material"

    client.app.dependency_overrides = {}


@patch("app.routers.materials.get_current_user")
def test_create_material_conflict(mock_user, client):
    mock_user.return_value = {"id": 1}

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.add = MagicMock()
        db.commit = AsyncMock(side_effect=IntegrityError(None, None, None))
        db.rollback = AsyncMock()
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    payload = {
        "name": "Wood",
        "description": "Natural wood material"
    }

    response = client.post("/api/materials/", json=payload)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Material with this name already exists."

    client.app.dependency_overrides = {}


def test_list_materials(client):
    fake_material1 = MagicMock()
    fake_material1.id = 1
    fake_material1.name = "Wood"
    fake_material1.description = "Natural wood material"
    fake_material1.created_at = datetime.now()

    fake_material2 = MagicMock()
    fake_material2.id = 2
    fake_material2.name = "Metal"
    fake_material2.description = "Steel material"
    fake_material2.created_at = datetime.now()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = [fake_material1, fake_material2]
        db.execute = AsyncMock(return_value=result)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.get("/api/materials/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Wood"
    assert response.json()[1]["name"] == "Metal"

    client.app.dependency_overrides = {}


def test_get_material_success(client):
    fake_material = MagicMock()
    fake_material.id = 1
    fake_material.name = "Wood"
    fake_material.description = "Natural wood material"
    fake_material.created_at = datetime.now()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=fake_material)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.get("/api/materials/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Wood"
    assert response.json()["description"] == "Natural wood material"

    client.app.dependency_overrides = {}


def test_get_material_not_found(client):
    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=None)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.get("/api/materials/99")

    assert response.status_code == 404
    assert response.json()["detail"] == "Material not found"

    client.app.dependency_overrides = {}


@patch("app.routers.materials.get_current_user")
def test_update_material_success(mock_user, client):
    mock_user.return_value = {"id": 1}

    fake_material = MagicMock()
    fake_material.id = 1
    fake_material.name = "Wood"
    fake_material.description = "Old description"
    fake_material.created_at = datetime.now()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=fake_material)
        db.commit = AsyncMock()
        # Update the fields when refresh is called
        db.refresh = AsyncMock(side_effect=lambda x: (
            setattr(x, 'name', 'Oak Wood'),
            setattr(x, 'description', 'Premium oak wood')
        ))
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    payload = {
        "name": "Oak Wood",
        "description": "Premium oak wood"
    }

    response = client.put("/api/materials/1", json=payload)

    assert response.status_code == 200
    assert response.json()["name"] == "Oak Wood"
    assert response.json()["description"] == "Premium oak wood"

    client.app.dependency_overrides = {}


@patch("app.routers.materials.get_current_user")
def test_update_material_partial(mock_user, client):
    mock_user.return_value = {"id": 1}

    fake_material = MagicMock()
    fake_material.id = 1
    fake_material.name = "Wood"
    fake_material.description = "Old description"
    fake_material.created_at = datetime.now()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=fake_material)
        db.commit = AsyncMock()
        # Only update the description
        db.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'description', 'New description'))
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    payload = {
        "description": "New description"
    }

    response = client.put("/api/materials/1", json=payload)

    assert response.status_code == 200
    assert response.json()["description"] == "New description"

    client.app.dependency_overrides = {}


@patch("app.routers.materials.get_current_user")
def test_update_material_not_found(mock_user, client):
    mock_user.return_value = {"id": 1}

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=None)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    payload = {
        "name": "Oak Wood"
    }

    response = client.put("/api/materials/99", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Material not found"

    client.app.dependency_overrides = {}


@patch("app.routers.materials.get_current_user")
def test_delete_material_success(mock_user, client):
    mock_user.return_value = {"id": 1}

    fake_material = MagicMock()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=fake_material)
        db.delete = AsyncMock()
        db.commit = AsyncMock()
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.delete("/api/materials/1")

    assert response.status_code == 200
    assert response.json()["detail"] == "Material deleted successfully"

    client.app.dependency_overrides = {}


@patch("app.routers.materials.get_current_user")
def test_delete_material_not_found(mock_user, client):
    mock_user.return_value = {"id": 1}

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=None)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.delete("/api/materials/99")

    assert response.status_code == 404
    assert response.json()["detail"] == "Material not found"

    client.app.dependency_overrides = {}