from database.neo4j import driver
from parsers.edge_parser import EdgePaser
from database.constraints import MAPPING_ENTITIES_TYPE, MAPPING_ENTITIES_KEY, MAPPING_ENTITY

from cachetools import TTLCache

graph_cache = TTLCache(maxsize=1000, ttl=3600)

async def post_relationship(edge: EdgePaser):
    async with driver.session() as session:
        src = edge.src
        dest = edge.dest
        connect_type = edge.connect_type
        evidence = edge.evidence
        query="""MERGE (from: {from_label} {{value: $from_value}})
                MERGE (to: {to_label} {{value: $to_value}})
                MERGE (from)-[r:{connect_type}]->(to)
                ON CREATE SET r.first_seen = datetime(),
                                r.last_seen = datetime(),
                                r.count = 1,
                                r.evidences = [$evidence]
                ON MATCH SET r.last_seen = datetime(),
                                r.count = r.count + 1,
                                r.last_seen = datetime(),
                                r.evidences =
                                CASE
                                    WHEN $evidence IN r.evidences
                                    THEN r.evidences
                                    ELSE r.evidences + $evidence
                                END
                """.format(from_label=src.type, 
                        to_label=dest.type,
                        connect_type=connect_type)
        await session.run(query, from_value=src.value, to_value=dest.value, evidence=evidence)

async def get_relationship_n_hop(type: str, value: str , hop: int):
    type = type if type != "file-hashes" else "file_hashes"
    async with driver.session() as session:
        if value == "all":
            query="""MATCH (from: {type})-[r*1..{hop}]-(to)
                RETURN from, r, to""".format(type=MAPPING_ENTITIES_TYPE[type], hop=hop)
        else:
            query="""MATCH (from: {type} {{value: $value}})-[r*1..{hop}]-(to)
                    RETURN from, r, to""".format(type=MAPPING_ENTITIES_TYPE[type], hop=hop)
        result = await session.run(query, value=value)
        return await result.data()
    
async def explore_entites(type: str, relationship: str):
    name = ""
    name += type if type is not None else ""
    name += relationship if relationship is not None else ""
    async with driver.session() as session:
        if type is None:
            query = "MATCH (entity)"
        else:
            query = "MATCH (entity: {type})".format(type=MAPPING_ENTITIES_TYPE[type])

        if relationship is not None:
            query += "-[r:{relationship}]-(to) RETURN entity, labels(entity) AS ent_label, r, to, labels(to) AS to_label".format(relationship=relationship)
        else:
            query += "-[r]-(to) RETURN DISTINCT entity, labels(entity) AS ent_label, r, to, labels(to) AS to_label"
        result = await session.run(query)
        record = await result.data()
        sub = [{k: v for k, v in ele.items() if k != "r" } for ele in record]
        return record
    
async def get_entities_follow(type: str, relationship: str):
    result = await explore_entites(type, relationship)
    return result

async def get_types():
    async with driver.session() as session:
        query = """CALL db.labels()"""
        result = await session.run(query)
        return await result.data()

async def get_relationships():
    async with driver.session() as session:
        query = """CALL db.relationshipTypes()"""
        result = await session.run(query)
        return await result.data()
