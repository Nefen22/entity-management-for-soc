import repositories.enrichment as repo
from .logs import write_audit_log
from database.constraints import MAPPING_ENTITIES_KEY, TENANT_DATABASE, MAPPING_ENTITIES_TYPE
from .function import format_neo4j_data, normalize_dict
from .entities import get_entity
from models.node import Node
from datetime import datetime

async def enrich(tenant:str, type:str, value:str, event_id: str | None = None):
    if type not in ["IP", "ips", "FileHash", "file_hashes", "file-hashes"]:
        return None
    type = "file_hashes" if type == "file-hashes" else type 
    node_before = await get_entity(tenant=tenant, type=type, value=value)
    if node_before == None:
        return None
    data = await repo.enrich(tenant=tenant,type=type, value=value)
    if not data:
        return None
    record = data.data()
    labels=[label for label in record["label"] if label not in TENANT_DATABASE.values()]
    result= Node(
                id= record["entity"][MAPPING_ENTITIES_KEY[labels[0]]],
                type= labels[0],
                properties= format_neo4j_data(record["entity"])
            )
    properties_before = normalize_dict(node_before["root"]["properties"])
    properties_after = normalize_dict(result.properties)
    if properties_before != properties_after:
        await write_audit_log(tenant=tenant,
                action="UPDATE",
                entity_type=MAPPING_ENTITIES_TYPE[type],
                entity_id=value,
                event_id=event_id,
                change = {
                    "before": properties_before,
                    "after": properties_after
                },
                time= str(datetime.now())
            )
    return result
    