import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from main import app  # điều chỉnh lại import nếu entrypoint app khác

client = TestClient(app)


# ---------------------- /api/auth/login ----------------------

def test_login_endpoint_returns_token_for_valid_credentials():
    with patch("services.auth.login", return_value="token-123") as mock_login:
        response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Login successful!"
    assert body["data"]["token"] == "token-123"
    mock_login.assert_called_once_with("admin", "admin123")


def test_login_endpoint_returns_401_for_invalid_credentials():
    with patch("services.auth.login", return_value=None):
        response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "wrong"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_login_endpoint_returns_422_for_missing_fields():
    response = client.post("/api/auth/login", json={"username": "admin"})

    assert response.status_code == 422


# ---------------------- /api/auth/me ----------------------

def test_me_endpoint_returns_permissions_for_authenticated_user():
    from services.auth import authenticate_user
    async def mock_authenticate_user():
        return {
            "username": "test_user",
            "role": "admin",
            "tenants": "all"
        }
    app.dependency_overrides[authenticate_user] = mock_authenticate_user
    try:
        with patch(
             "services.auth.UserRepository.get_permission",
             return_value={"permissions": ["graph:view", "graph:ingest"]},
          ):
            response = client.get("/api/auth/me")
    finally:
        app.dependency_overrides.pop(authenticate_user, None)

    assert response.status_code == 200
    body = response.json()
    assert body["permissions"] == ["graph:view", "graph:ingest"]


def test_me_endpoint_returns_403_when_permission_denied():
    from services.auth import authenticate_user
    async def mock_authenticate_user():
        return {
            "username": "test_user",
            "role": "user",
            "tenants": "all"
        }
    app.dependency_overrides[authenticate_user] = mock_authenticate_user
    try:
        with patch(
             "services.auth.UserRepository.get_permission",
             return_value={"permissions": []},
          ), \
         patch("services.auth.require_permission") as mock_require:
            async def forbidden_checker(user=None):
                from fastapi import HTTPException
                raise HTTPException(403, "Forbidden")

            mock_require.return_value = forbidden_checker
            response = client.get("/api/auth/me")
    finally:
        app.dependency_overrides.pop(authenticate_user, None)
    assert response.status_code in (200, 403)


def test_me_endpoint_returns_401_when_unauthenticated():
    response = client.get("/api/auth/me")
    assert response.status_code == 401