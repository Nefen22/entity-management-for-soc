from fastapi import APIRouter, HTTPException
from database.constraints import MAPPING_RELATIONSHIPS, MAPPING_ENTITIES_KEY, TENANT_DATABASE
from neo4j.time import DateTime
from datetime import datetime, timezone
import ulid
import time
import json
#Funtion 

def check_n_add_nodes(check_list,node):
    try:
        check_list[node["id"]]
        return None
    except:
        check_list[node["id"]] = ""
        return node

async def format_drawing(lst: list):
    lst=format_neo4j_data(lst)
    nodes_check = {}
    edges_check = []
    nodes = []
    edges = []
    root_label = [label for label in lst["root_label"] if label not in TENANT_DATABASE.values()][0]
    root_node = {"id": lst["root"][MAPPING_ENTITIES_KEY[root_label]], "type": root_label, "properties": lst["root"]}
    for rels in lst["relationships"]:
        source = rels["source"]
        source_label = [rel for rel in rels["source_label"] if rel not in TENANT_DATABASE.values()][0]
        source_name = source[MAPPING_ENTITIES_KEY[source_label]]
        target = rels["target"]
        target_label = [rel for rel in rels["target_label"] if rel not in TENANT_DATABASE.values()][0]
        target_name = target[MAPPING_ENTITIES_KEY[target_label]]
        pair_nodes=[check_n_add_nodes(nodes_check,{"id": source_name, "type": source_label, "properties": source}),
                    check_n_add_nodes(nodes_check, {"id": target_name, "type": target_label, "properties": target})]
        nodes+=[node for node in pair_nodes if node is not None]
        if (source_name, target_name) in edges_check:
            continue
        edges_check.append((source_name, target_name))
        edges_check.append((target_name, source_name))
        edges.append({
                    "source": source_name,
                    "target": target_name,
                    "type": rels["edge_type"],
                    "rel_properties": rels["prop"]
                })
    return{
        "root"  : root_node,  
        "nodes" : nodes,
        "edges" : edges,
    }

def format_neo4j_data(data):

    if isinstance(data, dict):
        return {k: format_neo4j_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [format_neo4j_data(i) for i in data]
    elif isinstance(data, DateTime):
        # Chuyển đổi neo4j.time.DateTime sang Python datetime tiêu chuẩn
        return datetime(data.year, data.month, data.day, data.hour, data.minute, int(data.second), int(data.nanosecond / 1000))
    return data

def normalize_event(event:dict):
    return {
        **event,
        "timestamp": event.get("timestamp") or datetime.now(timezone.utc).isoformat(),
        "event_id": event.get("event_id") or str(ulid.new()),
        "source_type": event.get("source_type", "unknown"),
    }

def normalize_dict(d):
    clean_dict = {}
    for k, v in d.items():
        if k in ['first_seen', 'last_seen', 'count']:  
            continue
        clean_dict[k] = str(v) 
    return json.dumps(clean_dict, sort_keys=True)