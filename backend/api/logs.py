from fastapi import APIRouter, HTTPException, Query, Depends
import backend.services.logs as services
from models.responses import APIResponse
from services.auth import require_permission
router = APIRouter(prefix = "")

@router.get("/audit-logs")
async def get_logs(
    tenant: str,
    page:int | None = Query(default=1, ge=1),
    start_time: str | None = None,
    end_time: str | None = None,
    action: str | None = None,
    entity_id: str | None = None,
    entity_type: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    permission = Depends(require_permission("graph:view"))
):
    result=await services.get_logs(
        page=page,
        tenant=tenant,
        start_time=start_time,
        end_time=end_time,
        action=action,
        entity_id=entity_id,
        entity_type=entity_type,
        limit=limit,
    )
    return APIResponse(message=f"Get logs completed", data=result)

@router.get("/events/{event_id}")
async def get_event(tenant:str, event_id: str, permission=Depends(require_permission("graph:view"))):
    result = await services.get_event(tenant=tenant, event_id=event_id)
    return APIResponse(message=f"Get event {event_id} completed", data=result)