from fastapi import APIRouter, HTTPException, status
import services.entities as services
from models.responses import APIResponse

router = APIRouter()

@router.get("/{type}/{value}")
async def get_entity(tenant: str,type:str, value):
    result = await services.get_entity(tenant=tenant, type=type, value=value)
    return APIResponse(message=f"Get {value}: Completed", data=result)