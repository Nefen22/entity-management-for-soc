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
from backend.database.constraints import REVERSED_TYPE, MAPPING_ENTITIES_KEY,TENANT_DATABASE
from .function import format_drawing, check_n_add_nodes


#Services
async def ingest(tenant: str, events: dict):
    if events.get("source_type") == "alert":
        sub_event = AlertParser.from_event(events)
    else:
        sub_event = JsonParser.from_event(events, events.get("source_type"))
    rel = sub_event.get_relationship()
    for type, value in sub_event.get_nodes():
        if not (value in ([ele.src.value for ele in rel]+[ele.dest.value for ele in rel])) or value == []:
            continue 
        for node in value:
            await post_entity(tenant=tenant, type=type, value=node)
    for ele_rel in rel:
        await check_existed_logs(tenant, ele_rel.src.type, ele_rel.src.value, True)
        await check_existed_logs(tenant, ele_rel.dest.type, ele_rel.dest.value, True)
        await repo.post_relationship(tenant, ele_rel)

async def ingest_sample(tenant: str, file: str):
    with open(f'./datasets/{file}', 'r', encoding='utf-8') as file:
        data = json.load(file)
    for event in data:
        await ingest(tenant, event)

async def get_relationship_n_hop(tenant: str, type:str, value:str, hop:int):
    result = await repo.get_relationship_n_hop(tenant=tenant,type=type, value=value, hop=hop)
    #return result
    return await format_drawing(result)

# async def explore_entites(tenant: str, type: str, relationship: str):
#     result = await repo.explore_entites(tenant=tenant, type=type, relationship=relationship)
#     record = await format_drawing(result)
#     return record

async def clusters(tenant: str):
    result = await repo.clusters(tenant)
    nodes = [{  "id": "Cluster_"+[label for label in record["label"] if label not in TENANT_DATABASE.values()][0],
                "type": "Cluster",
                "entity_type": [label for label in record["label"] if label not in TENANT_DATABASE.values()][0],
                "count": record["count"]
            } for record in result["nodes"]]
    edges = [{
                "source": [label for label in record["source_label"] if label not in TENANT_DATABASE.values()][0],
                "target": [label for label in record["target_label"] if label not in TENANT_DATABASE.values()][0],
                "type"  : record["rel_type"],
                "count" : record["count"]
            } for record in result["edges"]]
    return {
        "nodes": nodes,
        "edges": edges
    }

async def entity_in_cluster(tenant: str, type: str):
    result = await repo.entity_in_cluster(tenant, type)
    return await format_drawing(result)


async def get_types(tenant: str, relationship:str):
    result = await repo.get_types(tenant,relationship)
    labels =[]
    for ele in result:
        if not isinstance(ele["label"], list):
            labels.append(ele["label"])
        elif ele["label"][0] in TENANT_DATABASE.values():
            labels.append(ele["label"][1])
        else:
            labels.append(ele["label"][0])
    return labels

async def get_relationships(tenant: str, type:str):
    result = await repo.get_relationships(tenant, type)
    return [ele["relationshipType"][0] if isinstance(ele["relationshipType"], list) else ele["relationshipType"]  for ele in result]
