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
from database.constraints import REVERSED_TYPE, MAPPING_REALITIONSHIPS
from functools import reduce

#Funtion 

async def format_drawing(lst: list):
    # nodes{
    #     id:
    #     type:
    #     properties:
    # }
    
    nodes = []
    edges = []
    check_nodes = []
    check_edges = []
    for record in lst:
        for index in range(len(record["nodes"])):
            node = record["nodes"][index]
            n_type = record["node_labels"][index][0]
            node_name =  n_type + ":" + node["value"]
            if node_name in check_nodes:
                continue
            check_nodes.append(node_name)
            nodes.append({
                "id":node_name,
                "type":n_type,
                "properties": node
            })
        
        for index in range(len(record["edge_types"])):
            source = record["nodes"][index] 
            source_label = record["node_labels"][index][0]
            source_name = source_label + ":" + source["value"]
            target = record["nodes"][index + 1]
            target_label = record["node_labels"][index + 1][0]
            target_name = target_label + ":" + target["value"]
            edge_types = record["edge_types"][index]

            if (source_label, target_label) not in MAPPING_REALITIONSHIPS.keys():
                source_label, target_label = target, source_label
                source_name, target_name = target_name, source_name
            if (source_name, target_name) in check_edges:
                continue

            check_edges.append((source_name, target_name))
            edges.append({
                "source": source_name,
                "target": target_name,
                "type": edge_types
            })
    return {
        "nodes": nodes,
        "edges": edges
    }


#Services
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
    for type, value in sub_event.get_nodes():
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
    #return result
    return await format_drawing(result)

async def get_entities_follow(type: str, relationship: str):
    if (type, relationship) in repo.graph_cache:
        return repo.graph_cache[(type, relationship)]
    else:
        result = await repo.get_entities_follow(type=type, relationship=relationship)
    seen = set()
    return [{"entity":ele["nodes"][0], "label":ele["node_labels"][0]} for ele in result if not (ele["nodes"][0]["value"] in seen or seen.add(ele["nodes"][0]["value"]))]

async def explore_entites(type: str, relationship: str):
    result = await repo.explore_entites(type=type, relationship=relationship)
    record = await format_drawing(result)
    return record

async def get_types():
    result = await repo.get_types()
    return [ele["label"] for ele in result]

async def get_relationships():
    result = await repo.get_relationships()
    return [ele["relationshipType"] for ele in result]
