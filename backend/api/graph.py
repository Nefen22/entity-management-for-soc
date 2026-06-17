from fastapi import APIRouter, HTTPException
from parsers.edge_parser import EdgePaser
from parsers.base_parser import BaseParser
from parsers.siem_parser import SiemPaser
from parsers.edr_parser import EdrPaser
from parsers.cloud_parser import CloudPaser
import repositories.graph as repo
import json
from models.responses import APIResponse
import repositories.graph as repo

router = APIRouter()

@router.post("/ingest")
async def ingest(events: dict):
    if events.get("source_type") == "siem":
        sub_event = SiemPaser.from_event(events)
    elif events.get("source_type") == "edr":
        sub_event = EdrPaser.from_event(events)
    else:
        sub_event = CloudPaser.from_event(events)
    for edge in sub_event.get_relationship():
        print(edge)
        await repo.post_relationship(edge)
    return APIResponse(message="Ingest completed")

@router.post("/ingest/sample")
async def ingest_sample():
    with open('./datasets/sample_data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    for event in data:
        await ingest(event)
    return APIResponse(message="Sample data ingested!")

@router.get("/{type}/{value}/graph/{hop}")
async def get_relationship_n_hop(type:str, value:str, hop:int):
    result = await repo.get_relationship_n_hop(type=type, value=value, hop=hop)
    return APIResponse(message=f"Get query {hop} hop frrom {value} completed", data=result)