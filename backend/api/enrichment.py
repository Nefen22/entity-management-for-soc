from fastapi import APIRouter, HTTPException
import services.enrichment as services
from models.responses import APIResponse

router = APIRouter()

@router.post("/ips/{value}")
async def enrichment_ip(value:str):
    await services.enrichment_ip(value)
    return APIResponse(message=f"Enrichment {value} completed!")

@router.post("/file-hash/{value}")
async def enrichment_file_hash(value:str):
    await services.enrichment_file_hash(value)
    return APIResponse(message=f"Enrichment {value} completed!")