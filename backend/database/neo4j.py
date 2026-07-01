from neo4j import AsyncGraphDatabase
import os
from functools import reduce
from .constraints import MAPPING_ENTITIES_KEY_CLEAN, TENANT_DATABASE
from fastapi import FastAPI, HTTPException, status
from pathlib import Path

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")
TESTING_IN_DOCKER = os.getenv("TESTING_IN_DOCKER", "true").lower() == "true"

driver = AsyncGraphDatabase.driver(URI, auth=(USER, PASSWORD))

async def init_db(reset: bool):
    if reset:
        await drop_all_indexes()
        await clear_database()
        await indexing_for_entities()

async def clear_database():
    async with driver.session() as session:
        query="""MATCH (n) DETACH DELETE n"""
        await session.run(query)

async def indexing_for_entities():
    async with driver.session() as session:
        task = []
        for key, value in MAPPING_ENTITIES_KEY_CLEAN.items():
            query="""CREATE INDEX {value}_index IF NOT EXISTS
                    FOR (n:{type})
                    ON (n.{value})""".format(value=value, type=key)
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

