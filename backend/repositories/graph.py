from database.neo4j import driver
from parsers.edge_parser import EdgePaser
from database.constraints import MAPPING_ENTITIES_TYPE, MAPPING_ENTITIES_KEY, MAPPING_ENTITY

async def post_relationship(edge: EdgePaser):
    src = edge.src
    dest = edge.dest
    connect_type = edge.connect_type
    evidence = edge.evidence
    async with driver.session() as session:
        query="""MERGE (from: {from_label} {{{from_key}: $from_value}})
                MERGE (to: {to_label} {{{to_key}: $to_value}})
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
                """.format(from_label=src.type,from_key=src.key, 
                           to_label=dest.type, to_key=dest.key,
                           connect_type=connect_type)
        await session.run(query, from_value=src.value, to_value=dest.value, evidence=evidence)

async def get_relationship_n_hop(type: str, value: str, hop: int):
    async with driver.session() as session:
        query="""MATCH ({entity}: {type} {{{key}: $value}})-[r*1..{hop}]-(to)
                RETURN {entity}, r, to""".format(entity=type, type=MAPPING_ENTITIES_TYPE[type], key=MAPPING_ENTITIES_KEY[type], hop=hop)
        result = await session.run(query, value=value)
        return await result.data()