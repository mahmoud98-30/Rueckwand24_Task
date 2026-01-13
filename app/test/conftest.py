import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.auth import get_current_user
from app.database import get_db
from app.models import User


@pytest.fixture
def client():
    return TestClient(app)


# 🔥 Disable auth for all tests
@pytest.fixture(autouse=True)
def override_auth():
    def fake_current_user():
        return User(
            id=1,
            username="testuser",
            email="test@test.com",
            hashed_password="hashed",
        )

    app.dependency_overrides[get_current_user] = fake_current_user
    yield
    app.dependency_overrides.pop(get_current_user, None)


# 🔥 Disable real DB for all tests
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture(autouse=True)
def override_db():
    async def fake_db():
        db = MagicMock()
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.rollback = AsyncMock()
        db.refresh = AsyncMock()
        db.execute = AsyncMock()
        db.get = AsyncMock()
        db.delete = AsyncMock()
        yield db

    app.dependency_overrides[get_db] = fake_db
    yield
    app.dependency_overrides.pop(get_db, None)
