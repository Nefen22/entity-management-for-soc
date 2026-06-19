from fastapi import APIRouter, HTTPException
import repositories.enrichment as repo
from models.responses import APIResponse
from logs.audit_log import write_audit_log

async def enrichment_ip(value:str):
    data = await repo.enrichment_ip(value)
    write_audit_log(
            action="UPDATE",
            entity_type="IP",
            entity_id=value,
            change = data
        )

async def enrichment_file_hash(value:str):
    data = repo.enrichment_hash(value)
    write_audit_log(
            action="UPDATE",
            entity_type="FileHash",
            entity_id=value,
            change = data
        )