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
from .entities import post_entity, check_existed_logs
from logs.audit_log import write_audit_log
from database.constraints import REVERSED_TYPE
from functools import reduce

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
        if not (value in ([ele.src.value for ele in rel]+[ele.dest.value for ele in rel])) or value == []:
            continue 
        for node in value:
            await post_entity(type, node)

    for ele_rel in rel:
        await check_existed_logs(REVERSED_TYPE[ele_rel.src.type], ele_rel.src.value, True)
        await check_existed_logs(REVERSED_TYPE[ele_rel.dest.type], ele_rel.dest.value, True)
        await repo.post_relationship(ele_rel)

async def ingest_sample():
    with open('./datasets/sample_data1.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    for event in data:
        await ingest(event)

async def get_relationship_n_hop(type:str, value:str, hop:int):
    result = await repo.get_relationship_n_hop(type=type, value=value, hop=hop)
    return [relation["r"] for relation in result]

async def get_entities_follow(type: str, relationship: str):
    name = ""
    name += type if type is not None else ""
    name += relationship if relationship is not None else ""
    if name in repo.graph_cache:
        return repo.graph_cache[name]
    else:
        result = await repo.get_entities_follow(type=type, relationship=relationship)
    seen = set()
    return [{"entity":ele["entity"], "label":ele["ent_label"]} for ele in result if not (ele["entity"]["value"] in seen or seen.add(ele["entity"]["value"]))]

async def explore_entites(type: str, relationship: str):
    result = await repo.explore_entites(type=type, relationship=relationship)
    return result

async def get_types():
    result = await repo.get_types()
    return [ele["label"] for ele in result]

async def get_relationships():
    result = await repo.get_relationships()
    return [ele["relationshipType"] for ele in result]
