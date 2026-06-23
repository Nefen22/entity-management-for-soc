from fastapi import APIRouter, HTTPException, status
import repositories.entities as repo
from models.responses import APIResponse
from logs.audit_log import write_audit_log
from .function import format_drawing

async def post_entity(type:str, value):
    await check_existed_logs(type, value)
    await repo.post_entity(type, value)

async def get_entity(type:str, value):
    result = await repo.get_entity(type, value)
    return await format_drawing(result) if result else None

async def check_existed_logs(type:str, value, merge = False):
    existed = await get_entity(type, value)
    action = ""
    if not existed:
        action = "CREATE"
        write_audit_log(
                action=action,
                entity_type=type,
                entity_id=value,
                change = existed.data() if existed else {}
            )