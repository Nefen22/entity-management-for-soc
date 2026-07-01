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
SEED_NAME = os.getenv("SEED_NAME", "")

@asynccontextmanager
async def lifespan(app: FastAPI):
    if SEED_DATA:
        seed = SEED[SEED_NAME]
        for tenant in seed.keys():
            TENANT_DATABASE[tenant] = f"Tenant_{tenant}"
        if RESET_DB:
            Path("/app/backend/logs/audit_log.json").write_text("")
            await init_db(RESET_DB)
            await seed_db(seed)

    yield

async def load_tenant(tenant: str):
    async with driver.session() as session:
        await session.run(
            f"CREATE (n:{TENANT_DATABASE[tenant]} {{dummy: true}}) DETACH DELETE n"
        )

async def seed_db(seed:dict):
    for tenant, file in seed.items():
        await load_tenant(tenant)
        await ingest_sample(tenant=tenant, file=file)
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

