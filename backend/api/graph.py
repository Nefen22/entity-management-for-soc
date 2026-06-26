from fastapi import APIRouter, HTTPException
import json
from models.responses import APIResponse
import services.graph as services

router = APIRouter()

@router.post("/ingest")
async def ingest(tenant: str,events: dict):
    print(tenant)
    await services.ingest(tenant, events)
    return APIResponse(message="Ingest completed")

@router.post("/ingest/sample")
async def ingest_sample(tenant: str, file:str):
    print(tenant, file)
    await services.ingest_sample(tenant, file)
    return APIResponse(message="Sample data ingested!")

@router.get("/all-types")
async def get_types(tenant: str, relationship:str | None = None):
    result = await services.get_types(tenant, relationship)
    return APIResponse(message=f"Get all types: Completed", data=result)

@router.get("/all-relationships")
async def get_relationships(tenant: str, type:str | None = None):
    result = await services.get_relationships(tenant, type)
    return APIResponse(message=f"Get all relationships: Completed", data=result)

@router.get("/filter")
async def get_all_entities(tenant: str, type:str | None=None, relationship:str | None=None):
    result = await services.get_entities_follow(tenant, type, relationship)
    return APIResponse(message=f"Get all success!", data=result)

@router.get("/explore")
async def explore_entites(tenant: str, type:str | None=None, relationship:str | None=None):
    result = await services.explore_entites(tenant, type, relationship)
    return APIResponse(message=f"Get all success!", data=result)

@router.get("/{type}/{value}/{hop}")
async def get_relationship_n_hop(tenant: str, type:str, value:str, hop:int):
    result = await services.get_relationship_n_hop(tenant=tenant, type=type, value=value, hop=hop)
    return APIResponse(message=f"Get query {hop} hop frrom {value} completed", data=result)