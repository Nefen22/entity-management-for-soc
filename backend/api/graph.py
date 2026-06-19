from fastapi import APIRouter, HTTPException
from parsers.edge_parser import EdgePaser
from parsers.base_parser import BaseParser
from parsers.siem_parser import SiemPaser
from parsers.edr_parser import EdrPaser
from parsers.cloud_parser import CloudPaser
from parsers.alert_parser import AlertParser
import json
from models.responses import APIResponse
import services.graph as services
from .entities import post_entity

router = APIRouter()

@router.post("/ingest")
async def ingest(events: dict):
    await services.ingest(events)
    return APIResponse(message="Ingest completed")

@router.post("/ingest/sample")
async def ingest_sample():
    await services.ingest_sample()
    return APIResponse(message="Sample data ingested!")

@router.get("/{type}/{value}/graph/{hop}")
async def get_relationship_n_hop(type:str, value:str, hop:int):
    result = await services.get_relationship_n_hop(type=type, value=value, hop=hop)
    return APIResponse(message=f"Get query {hop} hop frrom {value} completed", data=result)