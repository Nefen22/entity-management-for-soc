from database.neo4j import driver
from parsers.edge_parser import EdgePaser
from database.constraints import MAPPING_ENTITIES_TYPE, MAPPING_ENTITIES_KEY, TENANT_DATABASE


async def post_relationship(tenant: str, edge: EdgePaser):
    async with driver.session() as session:
        src = edge.src
        dest = edge.dest
        connect_type = edge.connect_type
        evidence = edge.evidence
        query="""MERGE (src: {tenant}:{from_label} {{{f_key}: $from_value}})
                MERGE (dest: {tenant}:{to_label} {{{t_key}: $to_value}})
                MERGE (src)-[r:{connect_type}]->(dest)
                ON CREATE SET r.first_seen = datetime($time),
                                r.last_seen = datetime($time),
                                r.count = 1,
                                r.evidences = $evidence
                ON MATCH SET r.last_seen = datetime($time),
                                r.count = r.count + 1
                RETURN  src, labels(src) AS src_label,
                        dest, labels(dest) AS dest_label
                """.format(from_label=src.type, f_key=MAPPING_ENTITIES_KEY[src.type], 
                        to_label=dest.type, t_key=MAPPING_ENTITIES_KEY[dest.type],
                        connect_type=connect_type, tenant = TENANT_DATABASE[tenant])

        result = await session.run(query,from_value=src.value, to_value=dest.value, evidence=evidence, time = edge.time)
        return await result.single()

async def get_relationship_n_hop(tenant: str, type: str, value: str , hop: int):
    type = type if type != "file-hashes" else "file_hashes"
    async with driver.session() as session:
        query="""MATCH p=(start: {tenant} {type} {key_value})
                    CALL apoc.path.expandConfig(start, {{
                        minLevel: 1,
                        maxLevel: {hop},           // Số hop tối đa
                        uniqueness: "RELATIONSHIP_GLOBAL" // Thuật toán tối ưu lọc trùng cạnh ngay khi duyệt
                    }}) YIELD path
                    UNWIND relationships(path) AS rel
                    WITH DISTINCT rel
                    RETURN startNode(rel) AS source, labels(startNode(rel)) AS source_label,
                            endNode(rel) AS target, labels(endNode(rel)) AS target_label,
                            type(rel) AS edge_type,
                            properties(rel) AS prop""".format(key_value=f"{{{MAPPING_ENTITIES_KEY[type]} : $value}}" if type and value else "",
                                                              type=":" + MAPPING_ENTITIES_TYPE[type] if type else "",
                                                              hop=hop,
                                                              tenant=TENANT_DATABASE[tenant])
        result = await session.run(query, value=value)
        return await result.data()

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
        query = """MATCH (src:{tenant}{src_type}{{{src_key}:$src_value}}),
                (dest:{tenant}{dest_type}{{{dest_key}:$dest_value}}),
                p = shortestPath((src)-[*..15]-(dest))
                UNWIND relationships(p) AS rel
                    WITH DISTINCT rel
                    RETURN startNode(rel) AS source, labels(startNode(rel)) AS source_label,
                            endNode(rel) AS target, labels(endNode(rel)) AS target_label,
                            type(rel) AS edge_type,
                            properties(rel) AS prop""".format(tenant=TENANT_DATABASE[tenant],
                                                            src_type=":"+MAPPING_ENTITIES_TYPE[type] if type else "",
                                                            src_key=MAPPING_ENTITIES_KEY[type],
                                                            dest_type=":"+MAPPING_ENTITIES_TYPE[dest_type] if type else "",
                                                            dest_key=MAPPING_ENTITIES_KEY[dest_type])
        result = await session.run(query, src_value=value, dest_value=dest_value)
        return await result.data()