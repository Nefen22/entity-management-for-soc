from enrichment.geoip import enrichment_ip_func
from enrichment.virustotal_mock import enrichment_file_hash_func
from database.neo4j import driver

async def enrichment_ip(tenant: str,value:str):
    sub_dict = await enrichment_ip_func(value)
    check =  "SET entity += $props \n" if sub_dict else ""
    query = """MATCH (entity:{tenant}:IP {value: $value})
        {enrich}
        SET entity += $props
        RETURN entity, labels(entity) AS label""".format(tenant=tenant, sub_dict = check)
    async with driver.session() as session:
        result = await session.run(query,value = value, props = sub_dict)
        return await result.single()

async def enrichment_file_hash(tenant: str, hash_value:str):
    enrich_element = await enrichment_file_hash_func(hash_value)
    check = "SET entity += $props \n" if enrich_element else ""
    query = """MATCH (entity: {tenant}:FileHash {hash_value: $hash_value})
            {enrich}
            RETURN entity, labels(entity) AS label""".format(tenant=tenant,enrich = check)
    async with driver.session() as session:
        result =  await session.run(query, hash_value = hash_value, props = enrich_element)
        return await result.single()