from fastapi import APIRouter, HTTPException, status
import repositories.entities as repo
from models.responses import APIResponse
from logs.audit_log import write_audit_log
from .function import format_drawing
from database.constraints import MAPPING_ENTITIES_KEY

async def post_entity(type:str, value):
    result = await check_existed_logs(type, value)
    if result is not None:
        pass
    await repo.post_entity(type, value)

async def get_entity(type:str, value):
    result = await repo.get_entity(type, value)
    if result is None:
        return None
    record = result.data()
    return {
        "id": record["label"][0]+":"+record["entity"][MAPPING_ENTITIES_KEY[record["label"][0]]],
        "type": record["label"][0],
        "properties": record["entity"]
    } 

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
    return existed