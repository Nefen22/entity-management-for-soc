from fastapi import APIRouter, HTTPException, status, Depends
import services.entities as services
from models.responses import APIResponse
from services.auth import require_permission

router = APIRouter()

@router.get("/lists")
async def get_list_entity(tenant: str,type:str | None=None, relationship: str | None = None, start: str | None = None, end: str | None = None):
    result = await services.get_list_entity(tenant=tenant, type=type, relationship = relationship, start=start, end=end)
    return APIResponse(message=f"Get {type}: Completed", data=result)

@router.get("/types/{type}/values/{value:path}")
async def get_entity(tenant: str,type:str, value, permission = Depends(require_permission("graph:view"))):
    result = await services.get_entity(tenant=tenant, type=type, value=value)
    return APIResponse(message=f"Get {value}: Completed", data=dict(result))