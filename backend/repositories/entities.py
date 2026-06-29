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
    
async def get_all_entities(tenant: str):
    async with driver.session() as session:
        query ="""MATCH (node: {tenant})
                    RETURN node, labels(node) AS label
                    """.format(tenant=TENANT_DATABASE[tenant])
        result = await session.run(query)
        return await result.data()

async def get_list_entity(tenant: str, type:str, relationship:str):
    async with driver.session() as session:
        rel = ""
        if relationship:
            rel = f"-[rel:{relationship}]-(t)"
        query ="""MATCH (node: {tenant} {type}) {rels}
                    RETURN node, labels(node) AS label
                    """.format(tenant=TENANT_DATABASE[tenant], type = ":"+MAPPING_ENTITIES_TYPE[type], rels=rel)
        result = await session.run(query)
        return await result.data()

async def post_entity(tenant: str, type: str, value: str):
    type = type if type != "file-hashes" else "file_hashes"
    async with driver.session() as session:
        query ="""MERGE (entity: {tenant}:{type} {{{key}: $value}})""".format(tenant=TENANT_DATABASE[tenant],key=MAPPING_ENTITIES_KEY[type], type=MAPPING_ENTITIES_TYPE[type])
        await session.run(query, value=value)



