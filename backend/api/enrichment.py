from fastapi import APIRouter, HTTPException
import services.enrichment as services
from models.responses import APIResponse

router = APIRouter()

@router.post("/types/ips/values/{value}")
async def enrichment_ip(tenant: str, value:str):
    data = await services.enrichment_ip(tenant=tenant,value=value)
    if data:
        return APIResponse(message=f"Enrichment {value} completed!", data=data)
    raise HTTPException(404, "Not found")

@router.post("/types/file-hashes/values/{value}")
async def enrichment_file_hash(tenant: str,value:str):
    data = await services.enrichment_file_hash(tenant=tenant,value=value)
    if data:
        return APIResponse(message=f"Enrichment {value} completed!", data=data)
    raise HTTPException(404, "Not found")