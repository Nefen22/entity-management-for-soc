from fastapi import APIRouter, HTTPException, status
import services.entities as services
from models.responses import APIResponse

router = APIRouter()

@router.get("/{type}")
async def get_list_entity_type(tenant: str,type:str):
    result = await services.get_list_entity_type(tenant=tenant, type=type)
    return APIResponse(message=f"Get {type}: Completed", data=result)

@router.get("/{type}/{value:path}")
async def get_entity(tenant: str,type:str, value):
    result = await services.get_entity(tenant=tenant, type=type, value=value)
    return APIResponse(message=f"Get {value}: Completed", data=result)