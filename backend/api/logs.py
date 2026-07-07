from fastapi import APIRouter, HTTPException, Query, Depends
import logs.audit_log as service
from models.responses import APIResponse
from services.auth import require_permission
router = APIRouter(prefix = "/api/logs")

@router.get("")
async def get_logs(page: int = Query(default=1, ge=1, description="Trang hiện tại (bắt đầu từ 1)"),
    limit: int = Query(default=10, ge=1, le=100, description="Số lượng log trên mỗi trang"),
    current_user = Depends(require_permission("graph:view"))):
    try:
        result = await service.get_logs(page=page, limit=limit)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Không tìm thấy file audit log.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")
    return result