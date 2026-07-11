import repositories.enrichment as repo
from .logs import write_audit_log
from database.constraints import MAPPING_ENTITIES_KEY, TENANT_DATABASE, MAPPING_ENTITIES_TYPE
from .function import format_neo4j_data
from .entities import get_entity
from models.node import Node
from datetime import datetime

async def enrich(tenant:str, type:str, value:str):
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
    await write_audit_log(tenant=tenant,
            action="UPDATE",
            entity_type=MAPPING_ENTITIES_TYPE[type],
            entity_id=value,
            change = {
                "before": node_before["root"]["properties"],
                "after": result.properties
            },
            time= str(datetime.now())
        )
    return result
    