import re 
from .base_parser import BaseParser
from .edge_parser import Vertex
from database.constraints import MAPPING_ENTITIES_TYPE, ALL_PATTERNS, MAPPING_RELATIONSHIPS
from iocsearcher.searcher import Searcher
from .llm_client import LLM_Client
import json

searcher = Searcher()

def list_vertex(type:  str, lst:list):
    return [Vertex(type = MAPPING_ENTITIES_TYPE[type], value=ele) for ele in lst]

def encode_entity(message: str):
    entity_search = {}
    search = searcher.search_data(message)
    encoded = message
    count = 0
    for item in search:
        ele = json.loads(item.json())
        entity_type = ele["name"]
        ioc_value = ele["value"]
        encoded = encoded.replace(ioc_value, f"<{entity_type}_{count}>")
        entity_search[ioc_value] = f"<{entity_type}_{count}>"
        count+=1
    return encoded, entity_search

class AlertParser(BaseParser):
    @classmethod
    def normalize_data(cls, event: dict):
        if "message" in event.keys():
            message = {"message": event["message"]}
        else:
            message = event
        encoded_event, entity_search = encode_entity(json.dumps(message, ensure_ascii=False, indent=2))
        print(f"Encoded event: {encoded_event}")
        LLM_result = LLM_Client.parse(encoded_event, entity_search)
        return LLM_result

    @classmethod
    def from_event(cls, event: dict):
        message = event.get("message")
        lst = []
        time = str(event.get("timestamp"))
        nodes= []
        for k,v in ALL_PATTERNS.items():
            sub_lst = []
            list(map(lambda x: sub_lst.extend(x.findall(message)), v))
            nodes += list_vertex(k, sub_lst)
            lst+=sub_lst
        edges = [{"source": s_node,
                   "target": t_node,
                   "type": MAPPING_RELATIONSHIPS[(s_node.type,t_node.type)] if (s_node.type, t_node.type) in MAPPING_RELATIONSHIPS.keys() else "",
                   "time": time,
                   }
                   for s_node in nodes for t_node in nodes]
        edges=[edge for edge in edges if edge["type"] != ""]
        return cls(
            source_type=event.get("source_type"),
            nodes=nodes,
            edges=edges,
            evidence=event.get("event_id", "")
        )