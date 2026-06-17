from database.neo4j import driver
from parsers.edge_parser import EdgePaser

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
                                r.evidences = r.evidences + $evidence
                """.format(from_label=src.type,from_key=src.key, 
                           to_label=dest.type, to_key=dest.key,
                           connect_type=connect_type)
        await session.run(query, from_value=src.value, to_value=dest.value, evidence=evidence)