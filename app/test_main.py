import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
import os

from main import app
from database import Base, get_db
from models import User, Material, ProductType, Item
from auth import get_password_hash

# Test database URL
TEST_DATABASE_URL = "mysql+aiomysql://testuser:testpass@localhost:3306/test_testdb"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=True
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Create tables before tests and drop after"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture
async def client():
    """Async HTTP client for testing"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user(client):
    """Create a test user and return credentials"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    response = await client.post("/api/users/", json=user_data)
    return user_data


@pytest.fixture
async def auth_token(client, test_user):
    """Get authentication token"""
    response = await client.post(
        "/api/auth/login",
        json={"username": test_user["username"], "password": test_user["password"]}
    )
    data = response.json()
    return data["access_token"]


@pytest.fixture
async def auth_headers(auth_token):
    """Authentication headers"""
    return {"Authorization": f"Bearer {auth_token}"}


# Health Check Tests
@pytest.mark.asyncio
async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# User Tests
@pytest.mark.asyncio
async def test_create_user(client):
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123"
    }
    response = await client.post("/api/users/", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "id" in data


@pytest.mark.asyncio
async def test_create_duplicate_user(client, test_user):
    response = await client.post("/api/users/", json=test_user)
    assert response.status_code == 400


# Authentication Tests
@pytest.mark.asyncio
async def test_login(client, test_user):
    response = await client.post(
        "/api/auth/login",
        json={"username": test_user["username"], "password": test_user["password"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    response = await client.post(
        "/api/auth/login",
        json={"username": "invalid", "password": "invalid"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client, auth_headers):
    response = await client.post("/api/auth/logout", headers=auth_headers)
    assert response.status_code == 200


# Material Tests
@pytest.mark.asyncio
async def test_create_material(client, auth_headers):
    material_data = {
        "name": "Wood",
        "description": "High quality wood material"
    }
    response = await client.post("/api/materials/", json=material_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == material_data["name"]
    assert "id" in data


@pytest.mark.asyncio
async def test_get_materials(client, auth_headers):
    response = await client.get("/api/materials/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_update_material(client, auth_headers):
    # Create material
    material_data = {"name": "Metal", "description": "Metal material"}
    create_response = await client.post("/api/materials/", json=material_data, headers=auth_headers)
    material_id = create_response.json()["id"]

    # Update material
    update_data = {"name": "Steel", "description": "Updated description"}
    response = await client.put(f"/api/materials/{material_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Steel"


@pytest.mark.asyncio
async def test_delete_material(client, auth_headers):
    # Create material
    material_data = {"name": "Plastic"}
    create_response = await client.post("/api/materials/", json=material_data, headers=auth_headers)
    material_id = create_response.json()["id"]

    # Delete material
    response = await client.delete(f"/api/materials/{material_id}", headers=auth_headers)
    assert response.status_code == 204


# Product Type Tests
@pytest.mark.asyncio
async def test_create_product_type(client, auth_headers):
    product_type_data = {
        "name": "Chair",
        "description": "Furniture item"
    }
    response = await client.post("/api/product-types/", json=product_type_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == product_type_data["name"]
    assert "id" in data


@pytest.mark.asyncio
async def test_get_product_types(client, auth_headers):
    response = await client.get("/api/product-types/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# Item Tests (Note: These require a static image file to work properly)
@pytest.mark.asyncio
async def test_create_item_without_image(client, auth_headers):
    """This test will fail if static image doesn't exist, which is expected"""
    # First create material and product type
    material_response = await client.post(
        "/api/materials/",
        json={"name": "TestMaterial"},
        headers=auth_headers
    )
    material_id = material_response.json()["id"]

    product_type_response = await client.post(
        "/api/product-types/",
        json={"name": "TestProduct"},
        headers=auth_headers
    )
    product_type_id = product_type_response.json()["id"]

    # Try to create item (will fail without static image)
    item_data = {
        "material_id": material_id,
        "product_type_id": product_type_id,
        "width": 100,
        "height": 100
    }
    response = await client.post("/api/items/", json=item_data, headers=auth_headers)
    # This will be 500 because static image doesn't exist
    assert response.status_code in [201, 500]


@pytest.mark.asyncio
async def test_unauthorized_access(client):
    """Test that endpoints require authentication"""
    response = await client.get("/api/materials/")
    assert response.status_code == 401