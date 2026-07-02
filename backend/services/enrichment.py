from fastapi import APIRouter, HTTPException
import repositories.enrichment as repo
from models.responses import APIResponse
from logs.audit_log import write_audit_log
from database.constraints import MAPPING_ENTITIES_KEY, TENANT_DATABASE
from .function import format_neo4j_data
from .entities import get_entity
from models.node import Node
from datetime import datetime

async def enrichment_ip(tenant: str, value:str):
    node_before = await get_entity(tenant=tenant, type='ips', value=value)
    if node_before == None:
        return None
    data = await repo.enrichment_ip(tenant, value)
    record = data.data()
    write_audit_log(
            action="UPDATE",
            entity_type="IP",
            entity_id=value,
            change = {
                "before": node_before.json(),
                "after": record
            },
            time= str(datetime.now())
        )
    labels=[label for label in record["label"] if label not in TENANT_DATABASE.values()]
    return {
        "id": record["entity"][MAPPING_ENTITIES_KEY[labels[0]]],
        "type": labels[0],
        "properties": format_neo4j_data(record["entity"])
    }

async def enrichment_file_hash(tenant: str, value:str):
    node_before = await get_entity(tenant=tenant, type='ips', value=value)
    if not node_before:
        return None
    data = await repo.enrichment_file_hash(tenant, value)
    record = data.data()
    write_audit_log(
            action="UPDATE",
            entity_type="FileHash",
            entity_id=value,
            change = {
                "before": node_before,
                "after": record
            },
            time= datetime.now()
        )
    labels=[label for label in record["label"] if label not in TENANT_DATABASE.values()]
    return {
        "id": record["entity"][MAPPING_ENTITIES_KEY[labels[0]]],
        "type": labels[0],
        "properties": format_neo4j_data(record["entity"])
    }