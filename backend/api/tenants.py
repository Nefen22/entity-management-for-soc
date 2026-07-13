from fastapi import APIRouter, HTTPException, status, Depends
import services.enrichment as services
from models.responses import APIResponse
from api.entities import router as entities_router
from api.enrichment import router as enrichments_router
from api.graph import router as graphs_router
from api.logs import router as logs_router
from database.constraints import TENANT_DATABASE
from services.auth import authenticate_user, require_permission

router = APIRouter(prefix = "/api/tenants")

def validate_tenant(tenant: str, current_user = Depends(authenticate_user), permission = Depends(require_permission("graph:view"))):
    if tenant not in TENANT_DATABASE.keys():
        raise HTTPException(404, "Tenant not found")
    if  "all" in current_user["tenants"]:
        return tenant
    if tenant not in current_user["tenants"]:
        raise HTTPException(403, "Forbidden tenant")
    return tenant

router.include_router(entities_router, prefix = "/{tenant}/entities", tags = ["Entities"], dependencies=[Depends(validate_tenant)])
router.include_router(enrichments_router, prefix = "/{tenant}/enrichments", tags = ["Enrichments"], dependencies=[Depends(validate_tenant)])
router.include_router(graphs_router, prefix = "/{tenant}/graphs", tags = ["Graphs"], dependencies=[Depends(validate_tenant)])
router.include_router(logs_router, prefix = "/{tenant}/logs", tags = ["Logs"], dependencies=[Depends(validate_tenant)])

@router.get("")
def get_tenants(current_user = Depends(authenticate_user), permission = Depends(require_permission("graph:view"))):
    tenants = list(TENANT_DATABASE.keys())
    user_tenant = current_user["tenants"]
    if "all" in user_tenant:
        return APIResponse(message="GET tenants completed", data=tenants)
    return APIResponse(message="GET tenants completed", data=[tenant for tenant in tenants if tenant in user_tenant])


