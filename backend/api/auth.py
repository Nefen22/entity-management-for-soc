from fastapi import APIRouter, HTTPException
import services.enrichment as services
from models.responses import APIResponse
import services.auth as services
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth")

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(data: LoginRequest):
    data = await services.login(data.username, data.password)
    if data:
        return APIResponse(message="Login successful!", data={"token":data})
    raise HTTPException(401, "Invalid username or password")