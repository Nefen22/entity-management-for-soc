from fastapi import APIRouter, HTTPException, status
import repositories.entities as repo
from models.responses import APIResponse
from logs.audit_log import write_audit_log
from database.constraints import MAPPING_ENTITIES_KEY, TENANT_DATABASE,MAPPING_ENTITIES_TYPE
from .function import format_neo4j_data
from models.node import Node
from datetime import datetime

async def write_node_create_log(node: Node, action = 'CREATE', before_node: Node | None = None):
    label = node.type
    write_audit_log(
        action=action,
        entity_type=label,
        entity_id=node.id,
        change={"before": {},
                "after": node.json()}
                if not before_node else
                {"before": before_node.json(),
                 "after": node.json()},
        time= str(datetime.now())
    )

async def post_entity(tenant: str, type:str, value:str, time: str):
    if (await check_existed_logs(tenant=tenant, type=type, value=value)):
        result = await repo.post_entity(tenant, type, value)
        label = [label for label in result["label"] if label not in TENANT_DATABASE.values()][0]
        node = Node(id = result[label], type = result["label"], properties=result["properties"])
        await write_node_create_log(node=node)
        

async def get_entity(tenant: str, type:str, value: str):
    result = await repo.get_entity(tenant=tenant, type=type, value=value)
    if result is None:
        return None
    record = result.data()
    labels=[label for label in record["label"] if label not in TENANT_DATABASE.values()]
    properties = format_neo4j_data(record["entity"])
    properties["first_seen"] = format_neo4j_data(record["first_seen"])
    properties["last_seen"] = format_neo4j_data(record["last_seen"])
    properties["count"] = record["count"]
    return Node(
        id= record["entity"][MAPPING_ENTITIES_KEY[labels[0]]],
        type= labels[0],
        properties= properties
    )

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