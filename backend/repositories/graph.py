from database.neo4j import driver
from parsers.edge_parser import EdgePaser
from database.constraints import MAPPING_ENTITIES_TYPE, MAPPING_ENTITIES_KEY, TENANT_DATABASE
from .function import check_rels
from fastapi import HTTPException

async def post_relationship(tenant: str, edge: EdgePaser):
    async with driver.session() as session:
        src = edge.src
        dest = edge.dest
        connect_type = edge.connect_type
        evidence = edge.evidence
        query="""MERGE (src:`{tenant}`:`{from_label}` {{{f_key}: $from_value}})
                ON CREATE SET src.is_new = true
                
                MERGE (dest:`{tenant}`:`{to_label}` {{{t_key}: $to_value}})
                ON CREATE SET dest.is_new = true
                
                MERGE (src)-[r:`{connect_type}`]->(dest)
                ON CREATE SET r.first_seen = datetime($time),
                                r.last_seen = datetime($time),
                                r.count = 1,
                                r.evidence = $evidence
                ON MATCH SET r.last_seen = datetime($time),
                                r.count = r.count + 1
                                
                WITH src, dest, 
                    coalesce(src.is_new, false) AS src_is_new,
                    coalesce(dest.is_new, false) AS dest_is_new
                REMOVE src.is_new, dest.is_new
                
                RETURN  src, labels(src) AS src_label, src_is_new,
                        dest, labels(dest) AS dest_label, dest_is_new
                """.format(from_label=src.type, f_key=MAPPING_ENTITIES_KEY[src.type], 
                        to_label=dest.type, t_key=MAPPING_ENTITIES_KEY[dest.type],
                        connect_type=connect_type, tenant = TENANT_DATABASE[tenant])

        result = await session.run(query,from_value=src.value, to_value=dest.value, evidence=evidence, time = edge.time)
        return await result.single()

async def get_relationship_n_hop(tenant: str, type: str, value: str , hop: int):
    type = type if type != "file-hashes" else "file_hashes"
    async with driver.session() as session:
        query="""MATCH (start:{tenant}{type} {key_value})
                CALL apoc.path.expandConfig(start, {{
                    minLevel: 0,
                    maxLevel: $hop,
                    uniqueness: "RELATIONSHIP_GLOBAL"
                }}) YIELD path
                
                WITH start, apoc.coll.flatten(collect(relationships(path))) AS all_rels
                
                WITH start, apoc.coll.toSet(all_rels) AS unique_rels
                
                WITH start, unique_rels,
                    [r IN unique_rels WHERE startNode(r) = start OR endNode(r) = start] AS root_rels
                
                WITH start, root_rels,
                    [r IN unique_rels | {{
                        source: startNode(r), source_label: labels(startNode(r)),
                        target: endNode(r), target_label: labels(endNode(r)),
                        edge_type: type(r), prop: properties(r)
                    }}] AS relationships
                
                RETURN apoc.map.merge(properties(start), {{
                    first_seen: CASE WHEN size(root_rels) > 0 THEN apoc.coll.min([r IN root_rels | r.first_seen]) ELSE null END,
                    last_seen: CASE WHEN size(root_rels) > 0 THEN apoc.coll.max([r IN root_rels | r.last_seen]) ELSE null END,
                    count: apoc.coll.sum([r IN root_rels | r.count])
                }}) AS root,
                labels(start) AS root_label,
                relationships""".format(key_value=f"{{{MAPPING_ENTITIES_KEY[type]} : $value}}" if type and value else "",
                                            type=":" + MAPPING_ENTITIES_TYPE[type] if type else "",
                                            tenant=TENANT_DATABASE[tenant])

        result = await session.run(query, value=value, hop=hop)
        return await result.single()

async def clusters(tenant: str):
    async with driver.session() as session:
        query_edges = """MATCH (a:{tenant})-[r]->(b:{tenant})
                    RETURN labels(a) AS source_label,
                    type(r) AS rel_type,
                    labels(b) AS target_label,
                    COUNT(r) AS count""".format(tenant=TENANT_DATABASE[tenant])
        edges = await session.run(query_edges)
        query_nodes = """MATCH (a:{tenant})
                    RETURN labels(a) AS label, COUNT(*) AS count""".format(tenant=TENANT_DATABASE[tenant])
        nodes = await session.run(query_nodes)
        return {
            "nodes": await nodes.data(),
            "edges": await edges.data()
        }
    
async def entities_types_in_cluster(tenant: str, type: str):
    async with driver.session() as session:
        query="""MATCH (node:{tenant}:{type})-[r]-(target)
                RETURN  node,
                        labels(node) AS label,
                        COUNT(r) AS count""".format(tenant=TENANT_DATABASE[tenant], type=MAPPING_ENTITIES_TYPE[type])
        result = await session.run(query)
        return await result.data()

async def get_types(tenant: str, relationship:str):
    if not check_rels(relationship):
        raise HTTPException(status_code=404, detail="Relationship not found")  
    async with driver.session() as session:
        rel = f"-[r{relationship}]-(to)" if relationship else None
        query = """MATCH (n:{tenant}) {relationship}
                RETURN DISTINCT labels(n) AS label""".format(tenant=TENANT_DATABASE[tenant] ,relationship=rel if rel else "")
        result = await session.run(query)
        return await result.data()

async def filter_relationship(tenant: str, type:str):
    async with driver.session() as session:
        query = """MATCH (n:{tenant}{type})-[r]-(t:{tenant})
                RETURN DISTINCT type(r) AS relationshipType""".format(tenant=TENANT_DATABASE[tenant], type=":"+MAPPING_ENTITIES_TYPE[type] if type else "")
        result = await session.run(query)
        return await result.data()

async def path_finding(tenant: str, type: str, value:str, dest_type:str, dest_value:str):
    async with driver.session() as session:
        query = """MATCH (src:{tenant}{src_type} {{{src_key}: $src_value}}),
                    (dest:{tenant}{dest_type} {{{dest_key}: $dest_value}}),
                    p = shortestPath((src)-[*..15]-(dest))
                UNWIND relationships(p) AS rel
                WITH DISTINCT src, dest, rel
                WITH src, dest, collect({{
                    source: startNode(rel), source_label: labels(startNode(rel)),
                    target: endNode(rel), target_label: labels(endNode(rel)),
                    edge_type: type(rel), prop: properties(rel)
                }}) AS relationships
                RETURN src AS root, labels(src) AS root_label,
                    dest AS destination, labels(dest) AS destination_label,
                    relationships""".format(tenant=TENANT_DATABASE[tenant],
                                                            src_type=":"+MAPPING_ENTITIES_TYPE[type] if type else "",
                                                            src_key=MAPPING_ENTITIES_KEY[type],
                                                            dest_type=":"+MAPPING_ENTITIES_TYPE[dest_type] if type else "",
                                                            dest_key=MAPPING_ENTITIES_KEY[dest_type])
        result = await session.run(query, src_value=value, dest_value=dest_value)
        return await result.single()