from enrichment.geoip import enrichment_ip_func
from enrichment.virustotal_mock import enrichment_file_hash_func
from database.neo4j import driver

async def enrichment_ip(value:str):
    sub_dict = await enrichment_ip_func(value)
    query = """MATCH (ip: IP {value: $value})
        SET ip += $props
    """
    async with driver.session() as session:
        result = await session.run(query, value = value, props = sub_dict)
    return await result.data()

async def enrichment_file_hash(hash_value:str):
    enrich_element = await enrichment_file_hash_func(hash_value)
    query = """MATCH (f: FileHash {hash_value: $hash_value})
            SET f += $props"""
    async with driver.session() as session:
        result =  await session.run(query, hash_value = hash_value, props = enrich_element)
        return await result.data()