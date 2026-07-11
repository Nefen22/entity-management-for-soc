from fastapi import APIRouter, HTTPException, status
from parsers.alert_parser import AlertParser
from parsers.llm_parser import LLMParser
from parsers.json_parser import JsonParser
import json
from models.responses import APIResponse
import repositories.graph as repo
from .entities import post_entity, check_existed_logs, write_node_create_log
from database.constraints import MAPPING_ENTITIES_KEY,TENANT_DATABASE
from repositories.mongo_repo import EventsRepository
from .function import format_drawing, normalize_event, format_neo4j_data
from .enrichment import enrich
from models.node import Node
from datetime import datetime, timezone


#Services
async def ingest(tenant: str, event: dict | str, auto_ingest : bool | None = False):
    event = normalize_event(event=event)
    try:
        sub_event = JsonParser.from_event(event, event.get("source_type"))
    except ValueError:
        try:
            sub_event = LLMParser.from_event(event)
        except:
            sub_event = AlertParser.from_event(event)

        if sub_event.nodes == []:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Can not extract any entity")
    rel = sub_event.get_relationship()
    for type, value in sub_event.get_nodes():
        if not (value in ([ele.src.value for ele in rel]+[ele.dest.value for ele in rel])) or value == []:
            continue 
        for node in value:
            await post_entity(tenant=tenant, type=type, value=node,
                              time=event.get("timestamp") if event.get("timestamp") else str(datetime.now(timezone.utc).isoformat()))
            if auto_ingest:
                await enrich(tenant=tenant, type=type, value=node)
    for ele_rel in rel:
        src_check = await check_existed_logs(tenant, ele_rel.src.type, ele_rel.src.value, True)
        dest_check = await check_existed_logs(tenant, ele_rel.dest.type, ele_rel.dest.value, True)
        result = await repo.post_relationship(tenant, ele_rel)
        if src_check:
            s_label = [label for label in result["src_label"] if label not in TENANT_DATABASE.values()][0]
            src_r = Node(id=result["src"][MAPPING_ENTITIES_KEY[s_label]],type=s_label,properties=result["src"])
            await write_node_create_log(tenant,src_r)
            if auto_ingest:
                await enrich(tenant=tenant, type=src_r.type, value=src_r.id)
        if dest_check:
            d_label = [label for label in result["dest_label"] if label not in TENANT_DATABASE.values()][0]
            dest_r = Node(id=result["dest"][MAPPING_ENTITIES_KEY[d_label]],type=d_label,properties=result["dest"])
            await write_node_create_log(tenant,dest_r)
            if auto_ingest:
                await enrich(tenant=tenant, type=dest_r.type, value=dest_r.id)
    await EventsRepository.post_event(tenant=tenant, event=event)
    return sub_event

async def batch_sample(tenant: str, file: str | list, auto_ingest: bool | None = False):
    if isinstance(file, str):
        with open(f'./datasets/{file}', 'r', encoding='utf-8') as file:
            data = json.load(file)
    else:
        data = file
    sub_data = []
    for event in data:
        sub_data.extend(await ingest(tenant, event, auto_ingest))
    return sub_data

async def get_relationship_n_hop(tenant: str, type:str, value:str, hop:int):
    result = await repo.get_relationship_n_hop(tenant=tenant,type=type, value=value, hop=hop)
    record = result.data()
    return await format_drawing(record)

async def clusters(tenant: str):
    result = await repo.clusters(tenant)
    nodes = [{  "id": [label for label in record["label"] if label not in TENANT_DATABASE.values()][0],
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

async def entities_types_in_cluster(tenant: str, type: str):
    result = await repo.entities_types_in_cluster(tenant, type)
    return [{
        "id": record["node"][MAPPING_ENTITIES_KEY[
            [label for label in record["label"] if label not in TENANT_DATABASE.values()][0]]],
        "type": [label for label in record["label"] if label not in TENANT_DATABASE.values()][0],
        "relationship_count": record["count"]
    } for record in result]

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

async def filter_relationship(tenant: str, type:str):
    result = await repo.filter_relationship(tenant, type)
    return [ele["relationshipType"][0] if isinstance(ele["relationshipType"], list) else ele["relationshipType"]  for ele in result]

async def path_finding(tenant: str, type: str, value:str, dest_type:str, dest_value:str):
    result = await repo.path_finding(tenant=tenant, type=type, value=value, dest_type=dest_type, dest_value=dest_value)
    return await format_drawing(result)