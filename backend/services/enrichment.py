from fastapi import APIRouter, HTTPException
import repositories.enrichment as repo
from models.responses import APIResponse
from logs.audit_log import write_audit_log
from backend.database.constraints import MAPPING_ENTITIES_KEY

async def enrichment_ip(value:str):
    data = await repo.enrichment_ip(value)
    record = data.data()
    write_audit_log(
            action="UPDATE",
            entity_type="IP",
            entity_id=value,
            change = record
        )
    return {
        "id": record["entity"][MAPPING_ENTITIES_KEY[record["label"][0]]],
        "type": record["label"][0],
        "properties": record["entity"]
    }

async def enrichment_file_hash(value:str):
    data = await repo.enrichment_file_hash(value)
    record = data.data()
    write_audit_log(
            action="UPDATE",
            entity_type="FileHash",
            entity_id=value,
            change = record
        )
    return {
        "id": record["entity"][MAPPING_ENTITIES_KEY[record["label"][0]]],
        "type": record["label"][0],
        "properties": record["entity"]
    }