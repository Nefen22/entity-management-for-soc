from fastapi import APIRouter, HTTPException, Depends
import json
from models.responses import APIResponse
import services.graph as services
from services.auth import authenticate_user, require_permission

router = APIRouter()

@router.post("/ingest")
async def ingest(tenant: str,events: dict, current_user = Depends(require_permission("graph:ingest"))):
    result = await services.ingest(tenant, events)
    return APIResponse(message="Ingest completed", data=result)

@router.post("/ingest/batch")
async def batch_sample(tenant: str, file:str | list[dict], current_user = Depends(require_permission("graph:ingest"))):
    result = await services.batch_sample(tenant, file)
    return APIResponse(message="Batch data ingested!", data=result)

@router.get("/get-types")
async def get_types(tenant: str, relationship:str | None = None, ):
    result = await services.get_types(tenant, relationship)
    return APIResponse(message=f"Get all types: Completed", data=result)

@router.get("/filter-relationships")
async def filter_relationship(tenant: str, type:str | None = None):
    result = await services.filter_relationship(tenant=tenant, type=type)
    return APIResponse(message=f"Get filter {type} relationship with completed", data=result)

@router.get("/clusters")
async def clusters(tenant: str):
    result = await services.clusters(tenant)
    return APIResponse(message=f"Get all clusters success!", data=result)

@router.get("/clusters/types/{type}")
async def entities_types_in_cluster(tenant: str, type: str):
    result = await services.entities_types_in_cluster(tenant, type)
    return APIResponse(message=f"Get all entity from cluster_{type} success!", data=result)

@router.get("/entities/types/{type}/values/{value:path}")
async def get_relationship_n_hop(tenant: str, type:str, value:str, hop:int | None = 1):
    result = await services.get_relationship_n_hop(tenant=tenant, type=type, value=value, hop=hop)
    return APIResponse(message=f"Get {hop}-hop graph from {value} successfully", data=result)

@router.get("/path/types/{type}/values/{value:path}/dest-types/{dest_type}/dest-values/{dest_value:path}")
async def path_finding(tenant: str, type: str, value:str, dest_type:str, dest_value:str):
    result = await services.path_finding(tenant=tenant, type=type, value=value, dest_type=dest_type, dest_value=dest_value)
    return APIResponse(message=f"Get path from {value} to {dest_value} successfully", data=result)
