from fastapi import APIRouter, HTTPException
from backend.database.constraints import MAPPING_RELATIONSHIPS, MAPPING_ENTITIES_KEY, TENANT_DATABASE
from neo4j.time import DateTime
from datetime import datetime
import time
from cachetools import TTLCache

graph_cache = TTLCache(maxsize=1000, ttl=3600)

#Funtion 

def check_n_add_nodes(check_list,node):
    try:
        check_list[node["id"]]
        return None
    except:
        check_list[node["id"]] = ""
        return node

async def format_drawing(lst: list):
    nodes_check = {}
    edges_check = []
    nodes = []
    edges = []
    for rels in lst:
        source = rels["source"]
        source_label = [rel for rel in rels["source_label"] if rel not in TENANT_DATABASE.values()][0]
        source_name = source_label + ":" + source[MAPPING_ENTITIES_KEY[source_label]]
        target = rels["target"]
        target_label = [rel for rel in rels["target_label"] if rel not in TENANT_DATABASE.values()][0]
        target_name = target_label + ":" + target[MAPPING_ENTITIES_KEY[target_label]]
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
        "nodes": nodes,
        "edges": edges,
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
