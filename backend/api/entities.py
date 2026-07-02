from fastapi import APIRouter, HTTPException, status
import services.entities as services
from models.responses import APIResponse

router = APIRouter()

@router.get("/lists")
async def get_list_entity(tenant: str,type:str | None=None, relationship: str | None = None, start: str | None = None, end: str | None = None):
    result = await services.get_list_entity(tenant=tenant, type=type, relationship = relationship, start=start, end=end)
    return APIResponse(message=f"Get {type}: Completed", data=result)

@router.get("/types/{type}/values/{value:path}")
async def get_entity(tenant: str,type:str, value):
    result = await services.get_entity(tenant=tenant, type=type, value=value)
    return APIResponse(message=f"Get {value}: Completed", data=result)