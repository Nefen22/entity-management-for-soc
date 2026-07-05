import re 
from .base_parser import BaseParser
from .edge_parser import Vertex
from database.constraints import MAPPING_ENTITIES_TYPE
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