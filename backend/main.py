from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.tenants import router as tenants_router
from contextlib import asynccontextmanager
from pathlib import Path
from database.neo4j import indexing_for_entities, driver
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):

    Path("/app/backend/logs/audit_log.json").write_text("")
    await wait_for_neo4j()
    await indexing_for_entities()

    yield

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

