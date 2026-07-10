import os
import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock, patch

from services.auth import authenticate_user, login, require_permission


@pytest.mark.asyncio
async def test_login_returns_token_for_valid_credentials():
    user = {"username": "admin", "password": "hashed", "role": "admin", "tenants": ["all"]}

    with patch("services.auth.UserRepository.get_user", return_value=user), \
         patch("services.auth.verify_password", return_value=True), \
         patch("services.auth.create_access_token", return_value="token-123") as create_token:
        result = await login("admin", "admin123")

    create_token.assert_called_once_with({"sub": "admin", "role": "admin", "tenant": ["all"]})
    assert result == "token-123"


@pytest.mark.asyncio
async def test_login_returns_none_for_wrong_password():
    user = {"username": "admin", "password": "hashed", "role": "admin", "tenants": ["all"]}

    with patch("services.auth.UserRepository.get_user", return_value=user), \
         patch("services.auth.verify_password", return_value=False):
        result = await login("admin", "wrong")

    assert result is None


@pytest.mark.asyncio
async def test_login_returns_none_for_missing_user():
    with patch("services.auth.UserRepository.get_user", return_value=None):
        result = await login("missing", "password")

    assert result is None


@pytest.mark.asyncio
async def test_authenticate_user_returns_test_user_when_test_mode_enabled():
    with patch.dict(os.environ, {"TESTING_IN_DOCKER": "true"}, clear=False):
        result = await authenticate_user(credentials=None)

    assert result == {"username": "test_user", "role": "admin", "tenants": "all"}


@pytest.mark.asyncio
async def test_authenticate_user_raises_for_missing_credentials():
    with patch.dict(os.environ, {"TESTING_IN_DOCKER": "false"}, clear=False):
        with pytest.raises(HTTPException) as exc_info:
            await authenticate_user(credentials=None)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Unauthorized"


@pytest.mark.asyncio
async def test_authenticate_user_raises_for_invalid_or_tampered_token():
    credentials = MagicMock()
    credentials.credentials = "bad-token"

    with patch.dict(os.environ, {"TESTING_IN_DOCKER": "false"}, clear=False), \
         patch("services.auth.decode_access_token", side_effect=Exception("tampered")), \
         patch("services.auth.UserRepository.get_user", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            await authenticate_user(credentials=credentials)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Unauthorized"


@pytest.mark.asyncio
async def test_authenticate_user_returns_user_from_valid_payload():
    credentials = MagicMock()
    credentials.credentials = "valid-token"

    with patch.dict(os.environ, {"TESTING_IN_DOCKER": "false"}, clear=False), \
         patch("services.auth.decode_access_token", return_value={"sub": "admin"}), \
         patch("services.auth.UserRepository.get_user", return_value={"role": "admin", "tenants": ["all"]}):
        result = await authenticate_user(credentials=credentials)

    assert result == {"username": "admin", "role": "admin", "tenants": ["all"]}


@pytest.mark.asyncio
async def test_require_permission_returns_user_permissions_for_allowed_role():
    checker = require_permission("graph:view")

    with patch("services.auth.UserRepository.get_permission", return_value={"permissions": ["graph:view", "graph:ingest"]}):
        result = await checker(user={"username": "admin", "role": "admin", "tenants": ["all"]})

    assert result["permissions"] == ["graph:view", "graph:ingest"]
    assert result["role"] == "admin"


@pytest.mark.asyncio
async def test_require_permission_raises_for_missing_permission():
    checker = require_permission("graph:enrichment")

    with patch("services.auth.UserRepository.get_permission", return_value={"permissions": ["graph:view"]}):
        with pytest.raises(HTTPException) as exc_info:
            await checker(user={"username": "user", "role": "user", "tenants": ["google"]})

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Forbidden"


@pytest.mark.asyncio
async def test_require_permission_raises_for_missing_user():
    checker = require_permission("graph:view")

    with pytest.raises(HTTPException) as exc_info:
        await checker(user=None)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Unauthorized"
