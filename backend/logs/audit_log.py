import json
from pathlib import Path
import aiofiles
from fastapi import HTTPException
CURRENT_DIR = Path(__file__).resolve().parent
LOG_DIR = CURRENT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

def write_audit_log(action: str, entity_type: str, entity_id: str,time:str, change: dict | None = None):
    entry = {
        "timestamp": time,
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "change": change or {}
    }
    with open(LOG_DIR/"audit_log.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")

async def get_logs(
    page: int,
    limit: int 
):
    logs = []
    total_logs = 0
    start_index = (page - 1) * limit
    end_index = start_index + limit

    try:
        async with aiofiles.open(LOG_DIR / "audit_log.jsonl", "r") as f:
            lines = await f.readlines()

        # Bỏ dòng rỗng
        lines = [line.strip() for line in lines if line.strip()]

        # Mới nhất lên đầu
        lines.reverse()

        total_logs = len(lines)
        total_pages = (total_logs + limit - 1) // limit if total_logs else 1

        page_lines = lines[start_index:end_index]

        logs = []
        for line in page_lines:
            try:
                logs.append(json.loads(line))
            except json.JSONDecodeError:
                continue

        return {
            "metadata": {
                "total_records": total_logs,
                "current_page": page,
                "limit": limit,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            },
            "data": logs
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Không tìm thấy file audit log.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {e}")