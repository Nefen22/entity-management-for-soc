from fastapi import APIRouter, HTTPException
import repositories.enrichment as repo
from models.responses import APIResponse
from logs.audit_log import write_audit_log

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
        "id": record["label"][0]+":"+record["entity"]["value"],
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
        "id": record["label"][0]+":"+record["entity"]["value"],
        "type": record["label"][0],
        "properties": record["entity"]
    }