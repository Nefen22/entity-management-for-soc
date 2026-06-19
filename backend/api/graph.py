from fastapi import APIRouter, HTTPException
from parsers.edge_parser import EdgePaser
from parsers.base_parser import BaseParser
from parsers.siem_parser import SiemPaser
from parsers.edr_parser import EdrPaser
from parsers.cloud_parser import CloudPaser
from parsers.alert_parser import AlertParser
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
    elif events.get("source_type") == "cloud":
        sub_event = CloudPaser.from_event(events)
    elif events.get("source_type") == "alert":
        sub_event = AlertParser.from_event(events)
    rel = sub_event.get_relationship()
    for type, value in sub_event.get_nodes().items():
        if value == [] or value in [ele.src.value for ele in rel] + [ele.dest.value for ele in rel]:
            continue 
        for node in value:
            await repo.post_entities(type, node)
    await repo.post_relationship(rel)
    return APIResponse(message="Ingest completed")

@router.post("/ingest/sample")
async def ingest_sample():
    with open('./datasets/sample_data1.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    for event in data:
        await ingest(event)
    return APIResponse(message="Sample data ingested!")

@router.get("/{type}/{value}/graph/{hop}")
async def get_relationship_n_hop(type:str, value:str, hop:int):
    result = await repo.get_relationship_n_hop(type=type, value=value, hop=hop)
    return APIResponse(message=f"Get query {hop} hop frrom {value} completed", data=result)