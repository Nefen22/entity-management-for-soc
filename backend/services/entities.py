from fastapi import APIRouter, HTTPException, status
import repositories.entities as repo
from models.responses import APIResponse
from logs.audit_log import write_audit_log
from database.constraints import MAPPING_ENTITIES_KEY, TENANT_DATABASE,MAPPING_ENTITIES_TYPE

async def post_entity(tenant: str, type:str, value:str):
    result = await check_existed_logs(tenant=tenant, type=type, value=value)
    if result is not None:
        pass
    await repo.post_entity(tenant, type, value)

async def get_all_entities(tenant: str):
    result = await repo.get_all_entities(tenant=tenant)
    return [{
        "id": record["node"][MAPPING_ENTITIES_KEY[[label for label in record["label"] if label not in TENANT_DATABASE.values()][0]]],
        "label": [label for label in record["label"] if label not in TENANT_DATABASE.values()][0],
        "properties": record["node"]
    } for record in result]

async def get_entity(tenant: str, type:str, value: str):
    result = await repo.get_entity(tenant=tenant, type=type, value=value)
    if result is None:
        return None
    record = result.data()
    labels=[label for label in record["label"] if label not in TENANT_DATABASE.values()]
    return {
        "id": record["entity"][MAPPING_ENTITIES_KEY[labels[0]]],
        "type": labels[0],
        "properties": record["entity"]
    } 

async def get_list_entity(tenant: str,type:str, relationship:str | None = None):
    result = await repo.get_list_entity(tenant=tenant, type=type, relationship=relationship)
    return [{
        "id": record["node"][MAPPING_ENTITIES_KEY[[label for label in record["label"] if label not in TENANT_DATABASE.values()][0]]],
        "label": [label for label in record["label"] if label not in TENANT_DATABASE.values()][0],
        "properties": record["node"]
    } for record in result]

async def check_existed_logs(tenant: str, type:str, value:str, merge = False):
    existed = await get_entity(tenant=tenant, type=type, value=value)
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