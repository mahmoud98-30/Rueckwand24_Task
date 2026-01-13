from fastapi import status
from unittest.mock import AsyncMock, patch, ANY

@patch("app.routers.auth.create_token_session", new_callable=AsyncMock)
@patch("app.routers.auth.authenticate_user", new_callable=AsyncMock)
def test_login_success(mock_authenticate, mock_create_token, client):
    # Arrange
    fake_user = {"id": 1, "username": "testuser"}
    mock_authenticate.return_value = fake_user
    mock_create_token.return_value = "fake-jwt-token"

    data = {
        "username": "testuser",
        "password": "correctpassword"
    }

    # Act
    response = client.post(
        "/api/auth/login",
        data=data,  # OAuth2PasswordRequestForm uses form-data
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    body = response.json()

    assert body["access_token"] == "fake-jwt-token"
    assert body["token_type"] == "bearer"

    mock_authenticate.assert_awaited_once()
    mock_create_token.assert_awaited_once()

@patch("app.routers.auth.authenticate_user", new_callable=AsyncMock)
def test_login_invalid_credentials(mock_authenticate, client):
    # Arrange
    mock_authenticate.return_value = None

    data = {
        "username": "wrong",
        "password": "wrong"
    }

    # Act
    response = client.post(
        "/api/auth/login",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid username or password"

    mock_authenticate.assert_awaited_once()

@patch("app.routers.auth.revoke_token", new_callable=AsyncMock)
def test_logout_success(mock_revoke, client):
    fake_token = "fake-jwt-token"

    response = client.post(
        "/api/auth/logout",
        headers={
            "Authorization": f"Bearer {fake_token}"
        }
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["detail"] == "Logged out successfully"

    mock_revoke.assert_awaited_once_with(fake_token, ANY)
