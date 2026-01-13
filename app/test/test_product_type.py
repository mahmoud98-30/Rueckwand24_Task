from fastapi import status
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.exc import IntegrityError
from datetime import datetime


@patch("app.routers.product_types.get_current_user")
def test_create_product_type_success(mock_user, client):
    mock_user.return_value = {"id": 1}

    # Create a proper mock product type with all required fields
    fake_product_type = MagicMock()
    fake_product_type.id = 1
    fake_product_type.name = "Poster"
    fake_product_type.description = "Wall poster product"
    fake_product_type.created_at = datetime.now()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    # Patch the ProductType model to return our mock
    with patch("app.routers.product_types.ProductType", return_value=fake_product_type):
        payload = {
            "name": "Poster",
            "description": "Wall poster product"
        }

        response = client.post("/api/product-types/", json=payload)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()

    assert body["name"] == "Poster"
    assert body["description"] == "Wall poster product"

    client.app.dependency_overrides = {}


@patch("app.routers.product_types.get_current_user")
def test_create_product_type_conflict(mock_user, client):
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
        "name": "Poster",
        "description": "Wall poster product"
    }

    response = client.post("/api/product-types/", json=payload)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Product type with this name already exists."

    client.app.dependency_overrides = {}


def test_list_product_types(client):
    fake_product_type1 = MagicMock()
    fake_product_type1.id = 1
    fake_product_type1.name = "Poster"
    fake_product_type1.description = "Wall poster product"
    fake_product_type1.created_at = datetime.now()

    fake_product_type2 = MagicMock()
    fake_product_type2.id = 2
    fake_product_type2.name = "Canvas"
    fake_product_type2.description = "Canvas print product"
    fake_product_type2.created_at = datetime.now()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = [fake_product_type1, fake_product_type2]
        db.execute = AsyncMock(return_value=result)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.get("/api/product-types/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Poster"
    assert response.json()[1]["name"] == "Canvas"

    client.app.dependency_overrides = {}


def test_get_product_type_success(client):
    fake_product_type = MagicMock()
    fake_product_type.id = 1
    fake_product_type.name = "Poster"
    fake_product_type.description = "Wall poster product"
    fake_product_type.created_at = datetime.now()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=fake_product_type)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.get("/api/product-types/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Poster"
    assert response.json()["description"] == "Wall poster product"

    client.app.dependency_overrides = {}


def test_get_product_type_not_found(client):
    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=None)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.get("/api/product-types/99")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product type not found"

    client.app.dependency_overrides = {}


@patch("app.routers.product_types.get_current_user")
def test_update_product_type_success(mock_user, client):
    mock_user.return_value = {"id": 1}

    fake_product_type = MagicMock()
    fake_product_type.id = 1
    fake_product_type.name = "Poster"
    fake_product_type.description = "Old description"
    fake_product_type.created_at = datetime.now()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=fake_product_type)
        db.commit = AsyncMock()
        # Update the fields when refresh is called
        db.refresh = AsyncMock(side_effect=lambda x: (
            setattr(x, 'name', 'Premium Poster'),
            setattr(x, 'description', 'High quality wall poster')
        ))
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    payload = {
        "name": "Premium Poster",
        "description": "High quality wall poster"
    }

    response = client.put("/api/product-types/1", json=payload)

    assert response.status_code == 200
    assert response.json()["name"] == "Premium Poster"
    assert response.json()["description"] == "High quality wall poster"

    client.app.dependency_overrides = {}


@patch("app.routers.product_types.get_current_user")
def test_update_product_type_partial(mock_user, client):
    mock_user.return_value = {"id": 1}

    fake_product_type = MagicMock()
    fake_product_type.id = 1
    fake_product_type.name = "Poster"
    fake_product_type.description = "Old description"
    fake_product_type.created_at = datetime.now()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=fake_product_type)
        db.commit = AsyncMock()
        # Only update the description
        db.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'description', 'Updated description'))
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    payload = {
        "description": "Updated description"
    }

    response = client.put("/api/product-types/1", json=payload)

    assert response.status_code == 200
    assert response.json()["description"] == "Updated description"

    client.app.dependency_overrides = {}


@patch("app.routers.product_types.get_current_user")
def test_update_product_type_not_found(mock_user, client):
    mock_user.return_value = {"id": 1}

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=None)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    payload = {
        "name": "Premium Poster"
    }

    response = client.put("/api/product-types/99", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Product type not found"

    client.app.dependency_overrides = {}


@patch("app.routers.product_types.get_current_user")
def test_delete_product_type_success(mock_user, client):
    mock_user.return_value = {"id": 1}

    fake_product_type = MagicMock()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=fake_product_type)
        db.delete = AsyncMock()
        db.commit = AsyncMock()
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.delete("/api/product-types/1")

    assert response.status_code == 200
    assert response.json()["detail"] == "Product type deleted successfully"

    client.app.dependency_overrides = {}


@patch("app.routers.product_types.get_current_user")
def test_delete_product_type_not_found(mock_user, client):
    mock_user.return_value = {"id": 1}

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=None)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.delete("/api/product-types/99")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product type not found"

    client.app.dependency_overrides = {}