from database.neo4j import driver
from parsers.edge_parser import EdgePaser
from backend.database.constraints import MAPPING_ENTITIES_TYPE, MAPPING_ENTITIES_KEY, MAPPING_ENTITY

from cachetools import TTLCache

graph_cache = TTLCache(maxsize=1000, ttl=3600)

async def post_relationship(edge: EdgePaser):
    async with driver.session() as session:
        src = edge.src
        dest = edge.dest
        connect_type = edge.connect_type
        evidence = edge.evidence
        query="""MERGE (from: {from_label} {{{f_key}: $from_value}})
                MERGE (to: {to_label} {{{t_key}: $to_value}})
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
                """.format(from_label=src.type, f_key=MAPPING_ENTITIES_KEY[src.type], 
                        to_label=dest.type, t_key=MAPPING_ENTITIES_KEY[dest.type],
                        connect_type=connect_type)
        await session.run(query, from_value=src.value, to_value=dest.value, evidence=evidence)

async def get_relationship_n_hop(type: str, value: str , hop: int):
    type = type if type != "file-hashes" else "file_hashes"
    async with driver.session() as session:
        if value == "all":
            query="""MATCH p=(entity: {type})-[*1..{hop}]-(to)""".format(type=MAPPING_ENTITIES_TYPE[type], hop=hop)
        else:
            query="""MATCH p=(from: {type} {{{key}: $value}})-[*1..{hop}]-(to)""".format(key=MAPPING_ENTITIES_KEY[type], type=MAPPING_ENTITIES_TYPE[type], hop=hop)
        query+="""UNWIND nodes(p) AS n
                    UNWIND relationships(p) AS r
                    RETURN nodes(p) AS nodes,
                            relationships(p) AS edges,
                            [rel in relationships(p) | type(rel)] AS edge_types,
                            [rel in relationships(p) | properties(rel)] AS edges_properties,
                            [node in nodes(p) | labels(node)] AS node_labels"""
        result = await session.run(query, value=value)
        return await result.data()
    
async def explore_entites(type: str, relationship: str):
    async with driver.session() as session:
        if type is None:
            query = "MATCH p=(entity)"
        else:
            query = "MATCH p=(entity: {type})".format(type=MAPPING_ENTITIES_TYPE[type])
        
        if relationship is not None:
            query += """-[r:{relationship}]""".format(relationship=relationship)
        else:
            query += """-[r]"""

        if type is None:
            query += """->(to)"""
        else:
            query += """-(to)"""
        query+="""RETURN DISTINCT nodes(p) AS nodes,
                    [rel in relationships(p) | type(rel)] AS edge_types,
                    [rel in relationships(p) | properties(rel)] AS edges_properties,
                    [node in nodes(p) | labels(node)] AS node_labels"""
        result = await session.run(query)
        record = await result.data()
        sub = [{k: v for k, v in ele.items() if k != "r" } for ele in record]
        return record
    
async def get_entities_follow(type: str, relationship: str):
    result = await explore_entites(type, relationship)
    return result

async def get_types(relationship:str):
    async with driver.session() as session:
        rel = f"-[r{relationship}]-(to)" if relationship else None
        query = """MATCH (n) {relationship}
                RETURN DISTINCT labels(n) AS label""".format(relationship=rel if rel else "")
        result = await session.run(query)
        return await result.data()

async def get_relationships(type:str):
    async with driver.session() as session:
        query = """MATCH (n{type})-[r]-(t)
                RETURN DISTINCT type(r) AS relationshipType""".format(type=":"+type if type else "")
        result = await session.run(query)
        return await result.data()
