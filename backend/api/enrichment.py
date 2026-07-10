from fastapi import APIRouter, HTTPException, Depends
import services.enrichment as services
from models.responses import APIResponse
from services.auth import require_permission

router = APIRouter()

@router.post("/types/{type}/values/{value}")
async def enrichment_ip(tenant: str, type:str, value:str, permission = Depends(require_permission("graph:enrichment"))):
    data = await services.enrich(tenant=tenant,type=type,value=value)
    if data:
        return APIResponse(message=f"Enrichment {value} completed!", data=dict(data))
    raise HTTPException(404, "Not found")