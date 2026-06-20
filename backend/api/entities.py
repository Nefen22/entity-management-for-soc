from fastapi import APIRouter, HTTPException, status
import services.entities as services
from models.responses import APIResponse

router = APIRouter()

@router.get("/{type}/{value}")
async def get_entity(type:str, value):
    result = await services.get_entity(type, value)
    return APIResponse(message=f"Get {value}: Completed", data=result)