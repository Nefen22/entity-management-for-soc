from fastapi import APIRouter, HTTPException
from backend.database.constraints import REVERSED_TYPE, MAPPING_REALITIONSHIPS, MAPPING_ENTITIES_KEY
from neo4j.time import DateTime
from datetime import datetime
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
    for ele in lst:
        record = format_neo4j_data(ele)
        for index in range(len(record["nodes"])):
            node = record["nodes"][index]
            n_type = record["node_labels"][index][0]
            key = MAPPING_ENTITIES_KEY[n_type]
            node_name =  n_type + ":" + node[key]
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
            source_key = MAPPING_ENTITIES_KEY[source_label]
            source_name = source_label + ":" + source[source_key]
            target = record["nodes"][index + 1]
            target_label = record["node_labels"][index + 1][0]
            target_key = MAPPING_ENTITIES_KEY[target_label]
            target_name = target_label + ":" + target[target_key]
            if target_label not in MAPPING_REALITIONSHIPS[source_label].keys():
                source_name, target_name = target_name, source_name
            if (source_name, target_name) in check_edges:
                continue

            check_edges.append((source_name, target_name))
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