from fastapi import APIRouter, HTTPException
from backend.database.constraints import MAPPING_RELATIONSHIPS, MAPPING_ENTITIES_KEY, TENANT_DATABASE
from neo4j.time import DateTime
from datetime import datetime
import time

#Funtion 

async def format_drawing(lst: list):
    # nodes{
    #     id:
    #     type:
    #     properties:
    # }
    
    nodes = []
    edges = []
    check_nodes = {}
    check_edges = {}
    for ele in lst:
        record = format_neo4j_data(ele)
        for index in range(len(record["edge_types"])):
            source = record["nodes"][index] 
            s_labels=[label for label in record["node_labels"][index] if label not in TENANT_DATABASE.values()]
            source_label = s_labels[0]
            source_key = MAPPING_ENTITIES_KEY[source_label]
            source_name = source_label + ":" + source[source_key]
            
            target = record["nodes"][index + 1]
            t_labels=[label for label in record["node_labels"][index+1] if label not in TENANT_DATABASE.values()]
            target_label = t_labels[0]
            target_key = MAPPING_ENTITIES_KEY[target_label]
            target_name = target_label + ":" + target[target_key]

            try:
                check_nodes[source_name]
            except:
                check_nodes[source_name] = True
                nodes.append({
                    "id":source_name,
                    "type":source_label,
                    "properties": source
                })
            try:
                check_nodes[target_name]
            except:
                check_nodes[target_name] = True
                nodes.append({
                    "id":target_name,
                    "type":target_label,
                    "properties": target
                })

            try:
                MAPPING_RELATIONSHIPS[(source_label, target_label)]
            except:
                source_name, target_name = target_name,  source_name
            try:
                check_edges[(source_name, target_name)]
                continue
            except:
                check_edges[(source_name, target_name)]=True
                edges.append({
                    "source": source_name,
                    "target": target_name,
                    "type": record["edge_types"][index],
                    "rel_properties": record["edges_properties"][index]
                })
    return {
        "nodes": nodes,
        "edges": edges
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
