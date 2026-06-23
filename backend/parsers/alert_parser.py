import re 
from .base_parser import BaseParser
from .edge_parser import Vertex
from backend.database.constraints import MAPPING_RELATIONSHIPS, MAPPING_ENTITIES_TYPE, ALL_PATTERNS
import ipaddress


def list_vertex(type:  str, lst:list):
    return [Vertex(type = MAPPING_ENTITIES_TYPE[type], value=ele) for ele in lst]

class AlertParser(BaseParser):
    @classmethod
    def from_event(cls, event: dict):
        message = event.get("message")
        lst = []
        for k,v in ALL_PATTERNS:
            list(map(lambda x: lst.extend(x), v))
        nodes = [list_vertex(k, lst) for k, lst in ALL_PATTERNS]
        edges = [{"source": s_node,
                   "target": t_node,
                   "type": MAPPING_RELATIONSHIPS[s_node.type][t_node.type] if t_node.type in MAPPING_RELATIONSHIPS.keys() else ""}
                   for s_node in nodes for t_node in nodes]
        edges=[edge for edge in edges if edge["type"] != ""]
        return cls(
            source_type=event.get("source_type"),
            nodes=nodes,
            edges=edges,
            evidence=event.get("event_id", "")
        )
