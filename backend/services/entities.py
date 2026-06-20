from fastapi import APIRouter, HTTPException, status
import repositories.entities as repo
from models.responses import APIResponse
from logs.audit_log import write_audit_log

async def post_entity(type:str, value):
    await check_existed_logs(type, value)
    await repo.post_entity(type, value)

async def get_entity(type:str, value):
    result = await repo.get_entity(type, value)
    return result.data()

async def check_existed_logs(type:str, value, merge = False):
    existed = await get_entity(type, value)
    if not existed:
        action = "CREATE"
    elif merge:
        action = "MERGE"
    else:
        action = "UPDATE"
    write_audit_log(
            action=action,
            entity_type=type,
            entity_id=value,
            change = existed.data() if existed else {}
        )