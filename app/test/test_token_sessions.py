from fastapi import status
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

from app.database import get_db
from app.auth import get_current_user


def _fake_user(user_id: int = 1):
    u = MagicMock()
    u.id = user_id
    return u


def _fake_session(session_id: int, user_id: int):
    s = MagicMock()
    s.id = session_id
    s.user_id = user_id
    s.token = "fake-token"  # include if TokenSessionOut has it
    s.revoked = False
    s.expires_at = datetime.utcnow() + timedelta(days=1)
    s.created_at = datetime.utcnow()
    return s


def test_list_token_sessions_only_current_user(client):
    # override auth dependency
    client.app.dependency_overrides[get_current_user] = lambda: _fake_user(1)

    s1 = _fake_session(1, user_id=1)
    s2 = _fake_session(2, user_id=1)

    async def fake_db():
        db = MagicMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = [s1, s2]
        db.execute = AsyncMock(return_value=result)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.get("/api/token-sessions/")

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert len(body) == 2
    assert body[0]["id"] == 1
    assert body[1]["id"] == 2

    client.app.dependency_overrides = {}


def test_get_token_session_success(client):
    client.app.dependency_overrides[get_current_user] = lambda: _fake_user(1)

    s = _fake_session(1, user_id=1)

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=s)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.get("/api/token-sessions/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1

    client.app.dependency_overrides = {}


def test_get_token_session_not_found_when_missing(client):
    client.app.dependency_overrides[get_current_user] = lambda: _fake_user(1)

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=None)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.get("/api/token-sessions/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Token session not found"

    client.app.dependency_overrides = {}


def test_get_token_session_not_found_when_other_user(client):
    # current user is 1, session belongs to user 2 -> 404
    client.app.dependency_overrides[get_current_user] = lambda: _fake_user(1)

    s = _fake_session(1, user_id=2)

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=s)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.get("/api/token-sessions/1")

    assert response.status_code == 404
    assert response.json()["detail"] == "Token session not found"

    client.app.dependency_overrides = {}


def test_update_token_session_success(client):
    client.app.dependency_overrides[get_current_user] = lambda: _fake_user(1)

    s = _fake_session(1, user_id=1)

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=s)
        db.commit = AsyncMock()

        async def refresh_side_effect(obj):
            # simulate values after update
            # obj.revoked and obj.expires_at already mutated in endpoint
            return None

        db.refresh = AsyncMock(side_effect=refresh_side_effect)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    new_exp = (datetime.utcnow() + timedelta(days=10)).isoformat()

    payload = {
        "revoked": True,
        "expires_at": new_exp,
    }

    response = client.put("/api/token-sessions/1", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 1
    assert body["revoked"] is True

    client.app.dependency_overrides = {}


def test_update_token_session_not_found_when_other_user(client):
    client.app.dependency_overrides[get_current_user] = lambda: _fake_user(1)

    s = _fake_session(1, user_id=2)

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=s)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.put("/api/token-sessions/1", json={"revoked": True})

    assert response.status_code == 404
    assert response.json()["detail"] == "Token session not found"

    client.app.dependency_overrides = {}


def test_delete_token_session_success(client):
    client.app.dependency_overrides[get_current_user] = lambda: _fake_user(1)

    s = _fake_session(1, user_id=1)

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=s)
        db.delete = AsyncMock()
        db.commit = AsyncMock()
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.delete("/api/token-sessions/1")

    assert response.status_code == 200
    assert response.json()["detail"] == "Token session deleted"

    client.app.dependency_overrides = {}


def test_delete_token_session_not_found(client):
    client.app.dependency_overrides[get_current_user] = lambda: _fake_user(1)

    async def fake_db():
        db = MagicMock()
        db.get = AsyncMock(return_value=None)
        yield db

    client.app.dependency_overrides[get_db] = fake_db

    response = client.delete("/api/token-sessions/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Token session not found"

    client.app.dependency_overrides = {}
