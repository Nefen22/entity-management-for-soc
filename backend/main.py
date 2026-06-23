from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.entities import router as entites_router
from api.enrichment import router as enrichment_router
from api.graph import router as graph_router
from contextlib import asynccontextmanager
from pathlib import Path

@asynccontextmanager
async def lifespan(app: FastAPI):

    Path("/app/backend/logs/audit_log.json").write_text("")

    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(entites_router, prefix = "/api/entities", tags = ["Entities"])

app.include_router(enrichment_router, prefix = "/api/enrichment", tags = ["Enrichment"])

app.include_router(graph_router, prefix = "/api/graph", tags = ["Graph"])

@app.get("/")
def root():
    return {
        "status": "Online",
        "message": "Welcome to Entity management for SOC"
    }

