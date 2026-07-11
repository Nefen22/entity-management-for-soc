from fastapi import APIRouter, HTTPException, status
import repositories.entities as repo
from models.responses import APIResponse
from .logs import write_audit_log
from database.constraints import MAPPING_ENTITIES_KEY, TENANT_DATABASE
from .function import format_neo4j_data, format_drawing
from repositories.graph import get_relationship_n_hop
from models.node import Node
from datetime import datetime

async def write_node_create_log(tenant:str,node: Node, action = 'CREATE', before_node: Node | None = None):
    label = node.type
    await write_audit_log(tenant=tenant,
        action=action,
        entity_type=label,
        entity_id=node.id,
        change={"before": {},
                "after": node.model_dump_json()}
                if not before_node else
                {"before": before_node.model_dump_json(),
                 "after": node.model_dump_json()},
        time= str(datetime.now())
    )

async def post_entity(tenant: str, type:str, value:str, time: str):
    if (await check_existed_logs(tenant=tenant, type=type, value=value)):
        result = await repo.post_entity(tenant, type, value)
        label = [label for label in result["label"] if label not in TENANT_DATABASE.values()][0]
        node = Node(id = result[label], type = result["label"], properties=result["properties"])
        await write_node_create_log(tenant=tenant,node=node)
        

async def get_entity(tenant: str, type:str, value: str):
    type = "file_hashes" if type == "file-hashes" else type 
    result = await get_relationship_n_hop(tenant=tenant,type=type, value=value, hop=1)
    if not result: 
        return None
    record = result.data()
    return await format_drawing(record)

async def get_list_entity(tenant: str,type:str, relationship:str | None = None, start:str | None = None, end:str | None = None):
    result = await repo.get_list_entity(tenant=tenant, type=type, relationship = relationship, start=start, end=end)
    return [Node(
            id = record["node"][MAPPING_ENTITIES_KEY[[label for label in record["label"] if label not in TENANT_DATABASE.values()][0]]],
            type = [label for label in record["label"] if label not in TENANT_DATABASE.values()][0],
            properties = format_neo4j_data(record["node"])
        ) for record in result]

async def check_existed_logs(tenant: str, type:str, value:str, merge = False):
    existed = await get_entity(tenant=tenant, type=type, value=value)
    if existed:
        return False
    return True