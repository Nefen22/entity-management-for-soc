import re 
from .base_parser import BaseParser
from .edge_parser import Vertex
from database.constraints import MAPPING_ENTITIES_TYPE
from .llm_client import LLM_Client
import json
from .alert_parser import extract_enitty
from .json_parser import JsonParser
from fastapi import HTTPException, status

def encode_entity(message: str):
    entity_search = {}
    extract = extract_enitty(message)
    encoded = message
    count = 0
    for k, v in extract.items():
        entity_type = k
        count = 0
        for ele in v:
            encoded = encoded.replace(ele, f"<{entity_type}_{count}>")
            entity_search[ele] = f"<{entity_type}_{count}>"
            count+=1
    return encoded, entity_search

class LLMParser(BaseParser):
    @classmethod
    def normalize_data(cls, event: dict):
        if "message" in event.keys():
            message = {"message": event["message"]}
        else:
            message = event
        encoded_event, entity_search = encode_entity(json.dumps(message, ensure_ascii=False, indent=2))
        print(f"Encoded event: {encoded_event}")
        try:
            LLM_result = LLM_Client.parse(encoded_event, entity_search)
        except Exception as e:
            raise RuntimeError(f"Không thể phân tích dữ liệu do dịch vụ AI không hoạt động: {e}")

        return LLM_result
    
    @classmethod
    def from_event(cls, event: dict):
        nodes = []
        edges = []
        canonical = cls.normalize_data({k:v for k, v in event.items()
                                                if k not in
                                                ["source_type", "timestampp", "event_id", "event_type"]})
        print(f"Canonical: {canonical}")
        for ele in canonical:
            ele["source_type"] = event["source_type"]
            ele["timestamp"] = event["timestamp"]
            event_get = JsonParser.from_event(ele, "canonical")
            nodes += event_get.nodes
            edges += event_get.edges
        if nodes == []:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Can not extract any entity") 
        return cls(
            source_type=event.get("source_type"),
            nodes=nodes,
            edges=edges,
            evidence=event.get("event_id", "")
        )
