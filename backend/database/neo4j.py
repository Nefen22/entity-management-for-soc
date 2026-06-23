from neo4j import AsyncGraphDatabase
import os
from functools import reduce
from .constraints import MAPPING_ENTITIES_KEY_CLEAN

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = AsyncGraphDatabase.driver(URI, auth=(USER, PASSWORD))

async def indexing_for_entities():
    index = 0
    async with driver.session() as session:
        task = []
        for key, value in MAPPING_ENTITIES_KEY_CLEAN.items():
            query="""CREATE INDEX {value}_index IF NOT EXISTS
                    FOR (n:{type})
                    ON (n.{value})""".format(value=value, index=index, type=key)
            task.append(session.run(query))
        for t in task:
            await t

async def drop_all_indexes():
    async with driver.session() as session:
        result = await session.run("""
            SHOW INDEXES
            YIELD name
            RETURN name
        """)

        records = await result.data()

        for record in records:
            await session.run(
                f"DROP INDEX `{record['name']}`"
            )