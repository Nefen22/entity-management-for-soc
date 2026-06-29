from fastapi import APIRouter, HTTPException, status
import services.entities as services
from models.responses import APIResponse

router = APIRouter()

@router.get("")
async def get_all_entities(tenant: str):
    result = await services.get_all_entities(tenant=tenant)
    return APIResponse(message=f"Get {type}: Completed", data=result)

@router.get("/{type}")
async def get_list_entity_type_rels(tenant: str,type:str, relationship: str | None = None):
    result = await services.get_list_entity(tenant=tenant, type=type, relationship = relationship)
    return APIResponse(message=f"Get {type}: Completed", data=result)

@router.get("/{type}/{value:path}")
async def get_entity(tenant: str,type:str, value):
    result = await services.get_entity(tenant=tenant, type=type, value=value)
    return APIResponse(message=f"Get {value}: Completed", data=result)