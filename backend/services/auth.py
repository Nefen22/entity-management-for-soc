from repositories.user import UserRepository
from backend.auth.jwt import create_access_token, decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

security_scheme = HTTPBearer()

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

async def authenticate_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        user = UserRepository.get_user(payload.get("sub"))
        return {
            "username": payload["sub"],
            "role": user["role"],
            "tenants": user["tenants"]
        }
    except:
        return None