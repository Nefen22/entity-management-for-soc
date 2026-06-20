from database.neo4j import driver
from database.constraints import MAPPING_ENTITIES_TYPE, MAPPING_ENTITIES_KEY, MAPPING_ENTITY

async def get_entity(type: str, value: str):
    type = type if type != "file-hashes" else "file_hashes"
    async with driver.session() as session:
        query ="""MATCH (entity: {type} {{value: $value}}) RETURN entity, labels(entity) AS label""".format(type=MAPPING_ENTITIES_TYPE[type])
        result = await session.run(query, value=value)
        record = await result.single()
        if not record:
            return None
        return record

async def post_entity(type: str, value: str):
    type = type if type != "file-hashes" else "file_hashes"
    async with driver.session() as session:
        query ="""MERGE (entity: {type} {{value: $value}})""".format(type=MAPPING_ENTITIES_TYPE[type])
        await session.run(query, value=value)



