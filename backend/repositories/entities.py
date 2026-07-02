from database.neo4j import driver
from database.constraints import MAPPING_ENTITIES_TYPE, MAPPING_ENTITIES_KEY, TENANT_DATABASE

async def get_entity(tenant: str, type: str, value: str):
    type = type if type != "file-hashes" else "file_hashes"
    async with driver.session() as session:
        query ="""MATCH (entity:{tenant}:{type}{{{key}: $value}})
                    RETURN entity, labels(entity) AS label
                    """.format(tenant=TENANT_DATABASE[tenant],key=MAPPING_ENTITIES_KEY[type],type=MAPPING_ENTITIES_TYPE[type])
        result = await session.run(query, value=value)
        record = await result.single()
        if not record:
            return None
        return record

async def get_list_entity(tenant: str, type:str, relationship:str, start:str | None = None, end:str | None = None):
    async with driver.session() as session:
        rel = ""
        start_date="""any(first IN rel.first_seen WHERE datetime(first) >= datetime($start))"""
        end_date="""any(last IN rel.last_seen WHERE datetime(last) <= datetime($end))"""
        if not (start or end):
            date_time = ""
        elif not start:
            date_time = "WHERE " + end_date
        elif not end:
            date_time = "WHERE " + start_date
        else:
            date_time =f"""WHERE {start_date}
                            AND {end_date}"""
        query ="""MATCH (node:{tenant}{type})-[rel{relationship}]-(t)
                    {date_filter}
                    RETURN DISTINCT node, labels(node) AS label
                    """.format(tenant=TENANT_DATABASE[tenant],
                               type = ":"+MAPPING_ENTITIES_TYPE[type] if type else "",
                               relationship=":"+relationship if relationship else "",
                               date_filter = date_time)
        print(query)
        result = await session.run(query, start=start, end=end)
        return await result.data()

async def post_entity(tenant: str, type: str, value: str):
    type = type if type != "file-hashes" else "file_hashes"
    async with driver.session() as session:
        query ="""MERGE (entity:{tenant}:{type}{{{key}: $value}})""".format(tenant=TENANT_DATABASE[tenant],key=MAPPING_ENTITIES_KEY[type], type=MAPPING_ENTITIES_TYPE[type])
        await session.run(query, value=value)



