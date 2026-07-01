from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.tenants import router as tenants_router
from contextlib import asynccontextmanager
from pathlib import Path
from database.neo4j import init_db, driver
from api.graph import ingest_sample
from datasets.seed import SEED
from database.constraints import TENANT_DATABASE
import asyncio
import os

RESET_DB = os.getenv("RESET_DB", "true").lower() == "true"
SEED_DATA = os.getenv("SEED_DATA", "true").lower() == "true"
SEED_NAME = os.getenv("SEED_NAME", "DEMO")

@asynccontextmanager
async def lifespan(app: FastAPI):

    await wait_for_neo4j()
    if RESET_DB:
        Path("/app/backend/logs/audit_log.json").write_text("")
        await init_db(RESET_DB)
    if SEED_DATA:
        seed = SEED[SEED_NAME]
        await seed_db(seed)

    yield

async def load_tenant(tenant: str):
    TENANT_DATABASE[tenant] = f"Tenant_{tenant}"
    async with driver.session() as session:
        await session.run(
            f"CREATE (n:{TENANT_DATABASE[tenant]} {{dummy: true}}) DETACH DELETE n"
        )

async def seed_db(seed:dict):
    for tenant, file in seed.items():
        await load_tenant(tenant)
        await ingest_sample(tenant=tenant, file=file)

async def wait_for_neo4j(retries: int = 10, delay: float = 3.0):
    from neo4j.exceptions import ServiceUnavailable
    for attempt in range(retries):
        try:
            async with driver.session() as session:
                await session.run("RETURN 1")
            print("Neo4j connected")
            return
        except ServiceUnavailable:
            print(f"Neo4j not ready, retry {attempt + 1}/{retries}...")
            await asyncio.sleep(delay)
    raise RuntimeError("Neo4j unavailable after retries")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(tenants_router)

@app.get("/")
async def root():
    return {
        "status": "Online",
        "message": "Welcome to Entity management for SOC"
    }

