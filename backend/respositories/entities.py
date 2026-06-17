from database.neo4j import driver
from database.constraints import MAPPING_ENTITIES_TYPE, MAPPING_ENTITIES_KEY, MAPPING_ENTITY

async def post_entities(type: str, value: str):
    async with driver.session() as session:
        query ="""MERGE ({entity_name}: {type} {{{key}: $value}}) RETURN {entity_name}""".format(entity_name=MAPPING_ENTITY[type], type=type, key=MAPPING_ENTITIES_KEY[type])
        await session.run(query, value=value)

async def get_entities(type: str, value: str):
    async with driver.session() as session:
        query ="""MATCH ({entity_name}: {type} {{{key}: $value}}) RETURN {entity_name}""".format(entity_name=MAPPING_ENTITY[type], type=type, key=MAPPING_ENTITIES_KEY[type])
        result = await session.run(query, value=value)
        record = await result.single()
        return record.data()
    
