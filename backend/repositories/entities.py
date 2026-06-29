from database.neo4j import driver
from database.constraints import MAPPING_ENTITIES_TYPE, MAPPING_ENTITIES_KEY, TENANT_DATABASE
from .graph import get_relationship_n_hop

async def get_entity(tenant: str, type: str, value: str):
    type = type if type != "file-hashes" else "file_hashes"
    async with driver.session() as session:
        query ="""MATCH (entity: {tenant}:{type} {{{key}: $value}})
                    RETURN entity, labels(entity) AS label
                    """.format(tenant=TENANT_DATABASE[tenant],key=MAPPING_ENTITIES_KEY[type],type=MAPPING_ENTITIES_TYPE[type])
        result = await session.run(query, value=value)
        record = await result.single()
        if not record:
            return None
        return record

 
async def get_list_entity_type(tenant: str, type:str):
    result = await get_relationship_n_hop(tenant=tenant, type=type, hop = 1, value=None)
    return result

async def post_entity(tenant: str, type: str, value: str):
    type = type if type != "file-hashes" else "file_hashes"
    async with driver.session() as session:
        query ="""MERGE (entity: {tenant}:{type} {{{key}: $value}})""".format(tenant=TENANT_DATABASE[tenant],key=MAPPING_ENTITIES_KEY[type], type=MAPPING_ENTITIES_TYPE[type])
        await session.run(query, value=value)



