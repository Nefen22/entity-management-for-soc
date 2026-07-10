from fastapi import APIRouter, HTTPException, Query, Depends
import logs.audit_log as services
from models.responses import APIResponse
from services.auth import require_permission
router = APIRouter(prefix = "")

@router.get("")
async def get_logs(page: int = Query(default=1, ge=1, description="Trang hiện tại (bắt đầu từ 1)"),
    limit: int = Query(default=10, ge=1, le=100, description="Số lượng log trên mỗi trang")):
    try:
        result = await services.get_logs(page=page, limit=limit)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Không tìm thấy file audit log.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")
    return result

@router.get("/events/{event_id}")
async def get_event(tenant:str, event_id: str, permission=Depends(require_permission("graph:view"))):
    result = await services.get_event(tenant=tenant, event_id=event_id)
    return APIResponse(message=f"Get event {event_id} completed", data=result)