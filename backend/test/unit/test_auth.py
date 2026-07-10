import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from auth.jwt import create_access_token, decode_access_token, SECRET_KEY, ALGORITHM
from services.auth import login
from auth.password import verify_password, hash_password


class TestJWTDecoding:
    """Test jwt.py decode_access_token function"""

    def test_decode_expired_token(self):
        """Test that expired token raises exception properly"""
        # Create an expired token
        expired_data = {
            "sub": "testuser",
            "role": "admin",
            "exp": datetime.now() - timedelta(minutes=1)  # Expired 1 minute ago
        }
        expired_token = jwt.encode(expired_data, SECRET_KEY, algorithm=ALGORITHM)
        
        # Should raise Exception with message about expiration
        with pytest.raises(Exception) as exc_info:
            decode_access_token(expired_token)
        assert "expired" in str(exc_info.value).lower()

    def test_decode_invalid_token_signature(self):
        """Test that invalid token signature raises exception"""
        # Create token with wrong secret key
        wrong_key_data = {
            "sub": "testuser",
            "role": "admin",
            "exp": datetime.now() + timedelta(minutes=15)
        }
        invalid_token = jwt.encode(wrong_key_data, "wrong_secret_key", algorithm=ALGORITHM)
        
        # Should raise Exception with message about invalid token
        with pytest.raises(Exception) as exc_info:
            decode_access_token(invalid_token)
        assert "invalid" in str(exc_info.value).lower()

    def test_decode_malformed_token(self):
        """Test that malformed token raises exception"""
        malformed_token = "not.a.valid.token.format"
        
        with pytest.raises(Exception) as exc_info:
            decode_access_token(malformed_token)
        assert "invalid" in str(exc_info.value).lower()

    def test_decode_valid_token(self):
        """Test that valid token decodes successfully"""
        data = {
            "sub": "testuser",
            "role": "admin"
        }
        token = create_access_token(data)
        payload = decode_access_token(token)
        
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"


class TestAuthService:
    """Test services/auth.py login function"""

    @pytest.mark.asyncio # Đánh dấu hàm test là async
    async def test_login_nonexistent_user(self):
        """Test login with non-existent username"""
        
        with patch("services.auth.UserRepository.get_user", return_value=None):
            result = await login("nonexistent", "password123")
        
        assert result is None 

        with patch("services.auth.UserRepository.get_user", return_value=None):
            from backend.repositories.auth import UserRepository
            user = UserRepository.get_user("nonexistent_user_xyz")
            assert user is None

    def test_login_wrong_password(self):
        """Test login with correct username but wrong password"""
        fake_user = {
            "password": "correct_password",
            "role": "user",
            "tenants": ["tenant1"]
        }
        
        result = verify_password("wrong_password", hash_password(fake_user["password"]))
        assert result is False

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        result = verify_password("mypassword", hash_password("mypassword"))
        assert result is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        result = verify_password("password1", hash_password("password2"))
        assert result is False
