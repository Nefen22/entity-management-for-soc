from fastapi import APIRouter, HTTPException, status, Depends
import services.enrichment as services
from models.responses import APIResponse
from api.entities import router as entities_router
from api.enrichment import router as enrichments_router
from api.graph import router as graphs_router
from database.constraints import TENANT_DATABASE

router = APIRouter(prefix = "/api/tenants")

def validate_tenant(tenant: str):
    if tenant not in TENANT_DATABASE.keys():
        print("tenants not found")
        raise HTTPException(404, "Tenant not found")
    return tenant

router.include_router(entities_router, prefix = "/{tenant}/entities", tags = ["Entities"], dependencies=[Depends(validate_tenant)])
router.include_router(enrichments_router, prefix = "/{tenant}/enrichments", tags = ["Enrichments"], dependencies=[Depends(validate_tenant)])
router.include_router(graphs_router, prefix = "/{tenant}/graphs", tags = ["Graphs"], dependencies=[Depends(validate_tenant)])

@router.get("")
def get_tenants():
    return list(TENANT_DATABASE.keys())


