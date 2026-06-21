from enrichment.geoip import enrichment_ip_func
from enrichment.virustotal_mock import enrichment_file_hash_func
from database.neo4j import driver

async def enrichment_ip(value:str):
    sub_dict = await enrichment_ip_func(value)
    query = """MATCH (entity: IP {value: $value})
        SET entity += $props
        RETURN entity, labels(entity) AS label"""
    async with driver.session() as session:
        result = await session.run(query, value = value, props = sub_dict)
        return await result.single()

async def enrichment_file_hash(hash_value:str):
    enrich_element = await enrichment_file_hash_func(hash_value)
    if not enrich_element:
        query = """MATCH (entity: FileHash {value: $hash_value})
            RETURN entity, labels(entity) AS label"""
    else:
        query = """MATCH (entity: FileHash {value: $hash_value})
                SET entity += $props
                RETURN entity, labels(entity) AS label"""
    async with driver.session() as session:
        result =  await session.run(query, hash_value = hash_value, props = enrich_element)
        return await result.single()