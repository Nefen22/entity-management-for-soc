from fastapi import APIRouter, HTTPException, Depends
import services.enrichment as services
from models.responses import APIResponse
from services.auth import require_permission

router = APIRouter()

@router.post("/types/ips/values/{value}")
async def enrichment_ip(tenant: str, value:str, permission = Depends(require_permission("graph:enrichment"))):
    data = await services.enrichment_ip(tenant=tenant,value=value)
    if data:
        return APIResponse(message=f"Enrichment {value} completed!", data=dict(data))
    raise HTTPException(404, "Not found")

@router.post("/types/file-hashes/values/{value}")
async def enrichment_file_hash(tenant: str,value:str, permission = Depends(require_permission("graph:enrichment"))):
    data = await services.enrichment_file_hash(tenant=tenant,value=value)
    if data:
        return APIResponse(message=f"Enrichment {value} completed!", data=dict(data))
    raise HTTPException(404, "Not found")