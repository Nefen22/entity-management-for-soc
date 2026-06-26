from fastapi import APIRouter, HTTPException
import repositories.enrichment as repo
from models.responses import APIResponse
from logs.audit_log import write_audit_log
from backend.database.constraints import MAPPING_ENTITIES_KEY, TENANT_DATABASE
from .function import format_drawing

async def enrichment_ip(tenant: str, value:str):
    data = await repo.enrichment_ip(value)
    record = data.data()
    write_audit_log(
            action="UPDATE",
            entity_type="IP",
            entity_id=value,
            change = record
        )
    labels=[label for label in record["label"] if label not in TENANT_DATABASE.values]
    return {
        "id": labels[0]+":"+record["entity"][MAPPING_ENTITIES_KEY[labels[0]]],
        "type": labels[0],
        "properties": record["entity"]
    }

async def enrichment_file_hash(tenant: str, value:str):
    data = await repo.enrichment_file_hash(value)
    record = data.data()
    write_audit_log(
            action="UPDATE",
            entity_type="FileHash",
            entity_id=value,
            change = record
        )
    labels=[label for label in record["label"] if label not in TENANT_DATABASE.values]
    return {
        "id": labels[0]+":"+record["entity"][MAPPING_ENTITIES_KEY[labels[0]]],
        "type": labels[0],
        "properties": record["entity"]
    }