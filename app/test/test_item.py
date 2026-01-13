from fastapi import status
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.exc import IntegrityError
from datetime import datetime


@patch("app.routers.items.get_current_user")
@patch("app.routers.items.crop_and_create_pdf")
def test_create_item_success(mock_pdf, mock_user, client):
    mock_user.return_value = {"id": 1}
    mock_pdf.return_value = "/path/to/generated.pdf"

    # Create a proper mock item with all required fields
    fake_item = MagicMock()
    fake_item.id = 1
    fake_item.material_id = 1
    fake_item.product_type_id = 1
    fake_item.width = 100.5
    fake_item.height = 200.0
    fake_item.pdf_path = None  # Initially None, then set to PDF path
    fake_item.created_at = datetime.now()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.add = MagicMock()
        db.commit = AsyncMock()
        # Set pdf_path on second refresh
        db.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'pdf_path', '/path/to/generated.pdf'))
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    # Patch the Item model to return our mock
    with patch("app.routers.items.Item", return_value=fake_item):
        payload = {
            "material_id": 1,
            "product_type_id": 1,
            "width": 100.5,
            "height": 200.0
        }

        response = client.post("/api/items/", json=payload)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()

    assert body["material_id"] == 1
    assert body["product_type_id"] == 1
    assert body["width"] == 100.5
    assert body["height"] == 200.0
    assert body["pdf_path"] == "/path/to/generated.pdf"

    # Verify PDF was generated with correct parameters
    mock_pdf.assert_called_once_with(width=100.5, height=200.0, item_id=1)

    client.app.dependency_overrides = {}


@patch("app.routers.items.get_current_user")
def test_create_item_foreign_key_error(mock_user, client):
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
        "material_id": 999,  # Non-existent material
        "product_type_id": 1,
        "width": 100.5,
        "height": 200.0
    }

    response = client.post("/api/items/", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "foreign key constraint" in response.json()["detail"]

    client.app.dependency_overrides = {}


@patch("app.routers.items.get_current_user")
@patch("app.routers.items.crop_and_create_pdf")
def test_create_item_pdf_generation_fails(mock_pdf, mock_user, client):
    mock_user.return_value = {"id": 1}
    mock_pdf.side_effect = Exception("PDF generation error")

    fake_item = MagicMock()
    fake_item.id = 1
    fake_item.material_id = 1
    fake_item.product_type_id = 1
    fake_item.width = 100.5
    fake_item.height = 200.0
    fake_item.pdf_path = None
    fake_item.created_at = datetime.now()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    with patch("app.routers.items.Item", return_value=fake_item):
        payload = {
            "material_id": 1,
            "product_type_id": 1,
            "width": 100.5,
            "height": 200.0
        }

        response = client.post("/api/items/", json=payload)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "PDF generation failed" in response.json()["detail"]

    client.app.dependency_overrides = {}


def test_list_items(client):
    fake_item1 = MagicMock()
    fake_item1.id = 1
    fake_item1.material_id = 1
    fake_item1.product_type_id = 1
    fake_item1.width = 100.5
    fake_item1.height = 200.0
    fake_item1.pdf_path = "/path/to/item1.pdf"
    fake_item1.created_at = datetime.now()

    fake_item2 = MagicMock()
    fake_item2.id = 2
    fake_item2.material_id = 2
    fake_item2.product_type_id = 2
    fake_item2.width = 150.0
    fake_item2.height = 250.5
    fake_item2.pdf_path = "/path/to/item2.pdf"
    fake_item2.created_at = datetime.now()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = [fake_item1, fake_item2]
        db.execute = AsyncMock(return_value=result)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.get("/api/items/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
    assert response.json()[0]["width"] == 100.5
    assert response.json()[1]["width"] == 150.0

    client.app.dependency_overrides = {}


def test_get_item_success(client):
    fake_item = MagicMock()
    fake_item.id = 1
    fake_item.material_id = 1
    fake_item.product_type_id = 1
    fake_item.width = 100.5
    fake_item.height = 200.0
    fake_item.pdf_path = "/path/to/item.pdf"
    fake_item.created_at = datetime.now()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=fake_item)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.get("/api/items/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["width"] == 100.5
    assert response.json()["height"] == 200.0
    assert response.json()["pdf_path"] == "/path/to/item.pdf"

    client.app.dependency_overrides = {}


def test_get_item_not_found(client):
    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=None)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.get("/api/items/99")

    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

    client.app.dependency_overrides = {}


@patch("app.routers.items.get_current_user")
def test_update_item_success(mock_user, client):
    mock_user.return_value = {"id": 1}

    fake_item = MagicMock()
    fake_item.id = 1
    fake_item.material_id = 1
    fake_item.product_type_id = 1
    fake_item.width = 100.5
    fake_item.height = 200.0
    fake_item.pdf_path = "/path/to/item.pdf"
    fake_item.created_at = datetime.now()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=fake_item)
        db.commit = AsyncMock()
        # Update the fields when refresh is called
        db.refresh = AsyncMock(side_effect=lambda x: (
            setattr(x, 'material_id', 2),
            setattr(x, 'width', 150.0),
            setattr(x, 'height', 250.0)
        ))
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    payload = {
        "material_id": 2,
        "width": 150.0,
        "height": 250.0
    }

    response = client.put("/api/items/1", json=payload)

    assert response.status_code == 200
    assert response.json()["material_id"] == 2
    assert response.json()["width"] == 150.0
    assert response.json()["height"] == 250.0

    client.app.dependency_overrides = {}


@patch("app.routers.items.get_current_user")
def test_update_item_partial(mock_user, client):
    mock_user.return_value = {"id": 1}

    fake_item = MagicMock()
    fake_item.id = 1
    fake_item.material_id = 1
    fake_item.product_type_id = 1
    fake_item.width = 100.5
    fake_item.height = 200.0
    fake_item.pdf_path = "/path/to/item.pdf"
    fake_item.created_at = datetime.now()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=fake_item)
        db.commit = AsyncMock()
        # Only update width
        db.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'width', 175.0))
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    payload = {
        "width": 175.0
    }

    response = client.put("/api/items/1", json=payload)

    assert response.status_code == 200
    assert response.json()["width"] == 175.0

    client.app.dependency_overrides = {}


@patch("app.routers.items.get_current_user")
def test_update_item_not_found(mock_user, client):
    mock_user.return_value = {"id": 1}

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=None)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    payload = {
        "width": 150.0
    }

    response = client.put("/api/items/99", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

    client.app.dependency_overrides = {}


@patch("app.routers.items.get_current_user")
def test_delete_item_success(mock_user, client):
    mock_user.return_value = {"id": 1}

    fake_item = MagicMock()

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=fake_item)
        db.delete = AsyncMock()
        db.commit = AsyncMock()
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.delete("/api/items/1")

    assert response.status_code == 200
    assert response.json()["detail"] == "Item deleted successfully"

    client.app.dependency_overrides = {}


@patch("app.routers.items.get_current_user")
def test_delete_item_not_found(mock_user, client):
    mock_user.return_value = {"id": 1}

    from app.database import get_db

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=None)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.delete("/api/items/99")

    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

    client.app.dependency_overrides = {}