from enrichment.enrich import ips_enrich, hash_enrich
from database.neo4j import driver
from database.constraints import TENANT_DATABASE, MAPPING_ENTITIES_KEY, MAPPING_ENTITIES_TYPE

async def enrich(tenant: str,type:str, value:str):
    sub_dict = await ips_enrich(value) if type in ["IP", "ips"] else await hash_enrich(value)
    check =  "SET entity += $props" if sub_dict else ""
    query = """MATCH (entity:{tenant}:{type} {{{key}: $value}})
        {enrich}
        RETURN entity, labels(entity) AS label""".format(tenant=TENANT_DATABASE[tenant],
                                                         type=MAPPING_ENTITIES_TYPE[type],
                                                         key=MAPPING_ENTITIES_KEY[type],
                                                         enrich = check)
    async with driver.session() as session:
        result = await session.run(query,value = value, props = sub_dict)
        return await result.single()