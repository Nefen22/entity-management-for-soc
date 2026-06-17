from fastapi import APIRouter, HTTPException
import enrichment.geoip as geoip2
import enrichment.virustotal_mock as virustotal_mock
from models.responses import APIResponse

router = APIRouter()

@router.post("/ips/{value}/enrichment")
async def enrichment_ip(value:str):
    await geoip2.enrichment_ip_func(value)
    return APIResponse(message=f"Enrichment {value} completed!")

@router.post("/file-hash/{value}/enrichment")
async def enrichment_file_hash(value:str):
    await virustotal_mock.enrichment_file_hash_func(value)
    return APIResponse(message=f"Enrichment {value} completed!")