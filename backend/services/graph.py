from fastapi import APIRouter, HTTPException
from parsers.edge_parser import EdgePaser
from parsers.base_parser import BaseParser
from parsers.alert_parser import AlertParser
from parsers.json_parser import JsonParser
import json
from models.responses import APIResponse
import repositories.graph as repo
from .entities import post_entity, check_existed_logs, write_node_create_log
from database.constraints import REVERSED_TYPE, MAPPING_ENTITIES_KEY,TENANT_DATABASE
from .function import format_drawing
from models.node import Node


#Services
async def ingest(tenant: str, event: dict):
    try:
        sub_event = JsonParser.from_event(event, event.get("source_type"))
    except ValueError:
        canonical = AlertParser.normalize_data(event)
        print(f"Canonical: {canonical}")
        sub_event = JsonParser(nodes=[], edges=[], source_type=event.get("source_type"), evidence=event.get("event_id", ""))
        for ele in canonical:
            ele["source_type"] = event["source_type"]
            ele["timestamp"] = event["timestamp"]
            event_get = JsonParser.from_event(ele, "canonical")
            sub_event.nodes += event_get.nodes
            sub_event.edges += event_get.edges
    rel = sub_event.get_relationship()
    for type, value in sub_event.get_nodes():
        if not (value in ([ele.src.value for ele in rel]+[ele.dest.value for ele in rel])) or value == []:
            continue 
        for node in value:
            await post_entity(tenant=tenant, type=type, value=node, time=event["timestamp"])
    for ele_rel in rel:
        src_check = await check_existed_logs(tenant, ele_rel.src.type, ele_rel.src.value, True)
        dest_check = await check_existed_logs(tenant, ele_rel.dest.type, ele_rel.dest.value, True)
        result = await repo.post_relationship(tenant, ele_rel)
        if src_check:
            s_label = [label for label in result["src_label"] if label not in TENANT_DATABASE.values()][0]
            src_r = Node(id=result["src"][MAPPING_ENTITIES_KEY[s_label]],type=s_label,properties=result["src"])
            await write_node_create_log(src_r)
        if dest_check:
            d_label = [label for label in result["dest_label"] if label not in TENANT_DATABASE.values()][0]
            dest_r = Node(id=result["dest"][MAPPING_ENTITIES_KEY[d_label]],type=d_label,properties=result["dest"])
            await write_node_create_log(dest_r)
    return sub_event

async def batch_sample(tenant: str, file: str | list):
    if isinstance(file, str):
        with open(f'./datasets/{file}', 'r', encoding='utf-8') as file:
            data = json.load(file)
    else:
        data = file
    nodes, relationships = [], []
    for event in data:
        record = await ingest(tenant, event)
        event_nodes, event_relationships = record.get_nodes(), record.get_relationship()
        nodes.extend(event_nodes)
        relationships.extend(event_relationships)
    return {
        "nodes": nodes,
        "relationships": relationships
    }

async def get_relationship_n_hop(tenant: str, type:str, value:str, hop:int):
    result = await repo.get_relationship_n_hop(tenant=tenant,type=type, value=value, hop=hop)
    #return result
    return await format_drawing(result)

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