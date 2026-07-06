import re 
from .base_parser import BaseParser
from .edge_parser import Vertex
from database.constraints import MAPPING_ENTITIES_TYPE
from .llm_client import LLM_Client
import json
from .alert_parser import extract_enitty


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
