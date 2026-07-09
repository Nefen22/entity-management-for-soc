from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.tenants import router as tenants_router
from api.logs import router as logs_router
from api.auth import router as auth_router
from contextlib import asynccontextmanager
from pathlib import Path
from database.neo4j import init_db, driver
from api.graph import batch_sample
from datasets.seed import SEED
from database.constraints import TENANT_DATABASE
from api.auth import login
from database.mongodb import MongoDB
import os

RESET_DB = os.getenv("RESET_DB", "true").lower() == "true"
SEED_NAME = os.getenv("SEED_NAME", "")
ADMIN_NAME = "admin"
ADMIN_PASS = "admin123"
@asynccontextmanager
async def lifespan(app: FastAPI):
    MongoDB.connect()
    seed = SEED[SEED_NAME]
    for tenant in seed.keys():
        TENANT_DATABASE[tenant] = f"Tenant_{tenant}"
    if RESET_DB:
        Path("/app/backend/logs/audit_log.jsonl").write_text("")
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
        await batch_sample(tenant=tenant, file=file, current_user={"role":"admin",
                                                                   "permission":["grap:ingest", "graph:view"]})

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:80", "http://localhost/login.html"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(tenants_router)
app.include_router(logs_router)
app.include_router(auth_router)

@app.get("/")
async def root():
    return {
        "status": "Online",
        "message": "Welcome to Entity management for SOC"
    }

