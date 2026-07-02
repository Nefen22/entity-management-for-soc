import asyncio
import geoip2.database
import ipaddress
import json
from cachetools import TTLCache
from database.neo4j import driver

hash_cache = TTLCache(maxsize=1000, ttl=3500)
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
JSON_PATH = CURRENT_DIR / "data" / "virustotal.json" 


with open(JSON_PATH) as f:
    load_hash = json.load(f) 

def lookup_hash(hash_value: str):
    return load_hash.get(hash_value)

async def enrichment_file_hash_func(hash_value:str):
    enrich_element={}
    if hash_value in hash_cache:
        enrich_element = hash_cache[hash_value]
    else:
        enrich_element = lookup_hash(hash_value = hash_value)
        if enrich_element is None:
            return {}
        hash_cache[hash_value] = enrich_element
    return enrich_element

async def hash_cache_check():
    return dict(hash_cache)