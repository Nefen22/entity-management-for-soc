import asyncio
import ipaddress
import json
from database.neo4j import driver
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
JSON_PATH = CURRENT_DIR / "data" / "virustotal.json" 


with open(JSON_PATH) as f:
    load_hash = json.load(f) 

def lookup_hash(hash_value: str):
    return load_hash.get(hash_value)

async def enrichment_file_hash_func(hash_value:str):
    enrich_element={}
    try:
        enrich_element = lookup_hash(hash_value = hash_value)
        if enrich_element is None:
            return {}
    except Exception as e:
        raise e
    return enrich_element