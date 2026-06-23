from fastapi import APIRouter, HTTPException
from parsers.edge_parser import EdgePaser
from parsers.base_parser import BaseParser
from parsers.alert_parser import AlertParser
from parsers.json_parser import JsonParser
import json
from models.responses import APIResponse
import repositories.graph as repo
from .entities import post_entity, check_existed_logs
from logs.audit_log import write_audit_log
from backend.database.constraints import REVERSED_TYPE, MAPPING_ENTITIES_KEY
from .function import format_drawing

#Services
async def ingest(events: dict):
    if events.get("source_type") == "alert":
        sub_event = AlertParser.from_event(events)
    else:
        sub_event = JsonParser.from_event(events, events.get("source_type"))
    rel = sub_event.get_relationship()
    for type, value in sub_event.get_nodes():
        if not (value in ([ele.src.value for ele in rel]+[ele.dest.value for ele in rel])) or value == []:
            continue 
        for node in value:
            await post_entity(type, node)

    for ele_rel in rel:
        await check_existed_logs(REVERSED_TYPE[ele_rel.src.type], ele_rel.src.value, True)
        await check_existed_logs(REVERSED_TYPE[ele_rel.dest.type], ele_rel.dest.value, True)
        await repo.post_relationship(ele_rel)

async def ingest_sample(file: str):
    with open(f'./datasets/{file}', 'r', encoding='utf-8') as file:
        data = json.load(file)
    for event in data:
        await ingest(event)

async def get_relationship_n_hop(type:str, value:str, hop:int):
    result = await repo.get_relationship_n_hop(type=type, value=value, hop=hop)
    return await format_drawing(result)

async def get_entities_follow(type: str, relationship: str):
    if (type, relationship) in repo.graph_cache:
        result = repo.graph_cache[(type, relationship)]
    else:
        result = await repo.get_entities_follow(type=type, relationship=relationship)
    seen = set()
    record = []
    for ele in result:
        key = MAPPING_ENTITIES_KEY[ele["node_labels"][0][0]]
        if not (ele["nodes"][0][key] in seen or seen.add(ele["nodes"][0][key])):
            record.append({
                "id": ele["nodes"][0][key],
                "type": ele["node_labels"][0][0],
                "properties": ele["nodes"][0]
            })
    return record
            

async def explore_entites(type: str, relationship: str):
    result = await repo.explore_entites(type=type, relationship=relationship)
    record = await format_drawing(result)
    return record

async def get_types(relationship:str):
    result = await repo.get_types(relationship)
    return [ele["label"][0] if isinstance(ele["label"], list) else ele["label"] for ele in result]

async def get_relationships(type:str):
    result = await repo.get_relationships(type)
    return [ele["relationshipType"][0] if isinstance(ele["relationshipType"], list) else ele["relationshipType"]  for ele in result]
