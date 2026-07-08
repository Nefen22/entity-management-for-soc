import json
from redis.asyncio import Redis
import os
from .geoip import enrichment_ip_func
from .virustotal_mock import enrichment_file_hash_func

REDIS_HOST = os.getenv("REDIS_HOST", "redis-cache")

redis_client = Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

async def ips_enrich(value:str):
    cache_key = f"IP:{value}"
    cached_data = await redis_client.get(cache_key)

    if cached_data:
        print(f"Cache {cache_key} HIT!")
        return json.loads(cached_data)
    
    print(f"Cache {cache_key} MISS!")
    data = await enrichment_ip_func(value)

    await redis_client.setex(cache_key, 300, json.dumps(data))

    return data

async def hash_enrich(value:str):
    cache_key = f"HASH:{value}"
    cached_data = await redis_client.get(cache_key)

    if cached_data:
        print(f"Cache {cache_key} HIT!")
        return json.loads(cached_data)
    
    print(f"Cache {cache_key} MISS!")
    data = await enrichment_file_hash_func(value)

    await redis_client.setex(cache_key, 300, json.dumps(data))

    return data
