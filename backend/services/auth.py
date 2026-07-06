from repositories.user import UserRepository
from backend.auth.jwt import create_access_token, decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, Request
import os

security_scheme = HTTPBearer(auto_error=False)

def verify_password(password: str, stored_password: str):
    return password == stored_password

async def login(username:str, password:str):
    user = UserRepository.get_user(username)

    if not user:
        return None
    
    if not verify_password(password, user["password"]):
        return None

    return create_access_token({
        "sub": username,
        "role": user["role"],
        "tenant": user["tenants"]
    })

async def authenticate_user(request: Request):
    # Allow test mode to bypass authentication
    if os.getenv("TESTING_IN_DOCKER") == "true":
        return {
            "username": "test_user",
            "role": "admin",
            "tenants": "all"
        }
    
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        payload = decode_access_token(token)
        user = UserRepository.get_user(payload.get("sub"))
        return {
            "username": payload["sub"],
            "role": user["role"],
            "tenants": user["tenants"]
        }
    except:
        raise HTTPException(status_code=401, detail="Unauthorized")