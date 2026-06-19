from database.neo4j import driver
from database.constraints import MAPPING_ENTITIES_TYPE, MAPPING_ENTITIES_KEY, MAPPING_ENTITY

async def get_entity(type: str, value: str):
    type = type if type != "file-hashes" else "file_hashes"
    async with driver.session() as session:
        query ="""MATCH ({entity_name}: {type} {{{key}: $value}}) RETURN {entity_name}""".format(entity_name=type, type=MAPPING_ENTITIES_TYPE[type], key=MAPPING_ENTITIES_KEY[type])
        result = await session.run(query, value=value)
        return await result.single()

async def get_entities(type: str):
    type = type if type != "file-hashes" else "file_hashes"
    async with driver.session() as session:
        result = await session.run("""MATCH ({entity_name}: {type} )
                                   RETURN {entity_name}
                                   """.format(entity_name=type, type=MAPPING_ENTITIES_TYPE[type]))
        return await result.data()
    

async def post_entity(type: str, value: str):
    type = type if type != "file-hashes" else "file_hashes"
    async with driver.session() as session:
        query ="""MERGE ({entity_name}: {type} {{{key}: $value}})""".format(entity_name=type, type=MAPPING_ENTITIES_TYPE[type], key=MAPPING_ENTITIES_KEY[type])
        await session.run(query, value=value)

