from database.neo4j import driver
from backend.database.constraints import MAPPING_ENTITIES_TYPE, MAPPING_ENTITIES_KEY, MAPPING_ENTITY

async def get_entity(type: str, value: str):
    type = type if type != "file-hashes" else "file_hashes"
    async with driver.session() as session:
        query ="""MATCH p=(entity: {type} {{{key}: $value}}) -[]- (to)
                RETURN DISTINCT nodes(p) AS nodes,
                    [rel in relationships(p) | type(rel)] AS edge_types,
                    [node in nodes(p) | labels(node)] AS node_labels""".format(key=MAPPING_ENTITIES_KEY[type],type=MAPPING_ENTITIES_TYPE[type])
        result = await session.run(query, value=value)
        record = await result.data()
        if not record:
            return None
        return record

async def post_entity(type: str, value: str):
    type = type if type != "file-hashes" else "file_hashes"
    async with driver.session() as session:
        query ="""MERGE (entity: {type} {{{key}: $value}})""".format(key=MAPPING_ENTITIES_KEY[type], type=MAPPING_ENTITIES_TYPE[type])
        await session.run(query, value=value)



