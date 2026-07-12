from backend.repositories.mongo_repo import UserRepository
from backend.auth.jwt import create_access_token, decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, Request
from backend.auth.password import verify_password
import os

security_scheme = HTTPBearer(auto_error=False)

async def login(username: str, password: str):
    user = UserRepository.get_user(username)
    if not user or not verify_password(password, user["password"]):
        return None

    return create_access_token({
        "sub": username,
        "role": user["role"],
        "tenant": user["tenants"]
    })

async def authenticate_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        
        user = UserRepository.get_user(payload.get("sub"))
        return {
            "username": payload["sub"],
            "role": user["role"],
            "tenants": user["tenants"]
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
def require_permission(permission: str | None = None):
    async def checker(user: dict = Depends(authenticate_user)):
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        permissions = UserRepository.get_permission(user["role"])["permissions"]
        if permission and permission not in permissions:
            raise HTTPException(status_code=403, detail="Forbidden")
        user["permissions"]=permissions
        return {
            "username": user["username"],
            "role": user["role"],
            "tenants": user["tenants"],
            "permissions": permissions
        }

    return checker
