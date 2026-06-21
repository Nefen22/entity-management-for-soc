from .base_parser import BaseParser, clean
from .edge_parser import Vertex
from database.constraints import MAPPING_ENTITIES_TYPE, MAPPING_REALITIONSHIPS

CLOUD_INCLUDE = {
    "hosts":["source_host"],
    "ips":["destination_ip"],
    "domains":["destination_domain"]
}

class CloudPaser(BaseParser):
    @classmethod
    def from_event(cls, event: dict):
        nodes = []
        for k, v_lst in CLOUD_INCLUDE.items():
            nodes+= list(map(lambda v: Vertex(type=MAPPING_ENTITIES_TYPE[k], value=event.get(v) if event.get(v) else None), v_lst))
        nodes=[node for node in nodes if node.value != None]
        edges = [{"source": s_node,
                   "target": t_node,
                   "type": MAPPING_REALITIONSHIPS[(s_node.type, t_node.type)] if (s_node.type, t_node.type) in MAPPING_REALITIONSHIPS.keys() else ""} 
                   for s_node in nodes for t_node in nodes]
        edges=[edge for edge in edges if edge["type"] != ""]
        return cls(
            source_type=event.get("source_type"),
            nodes=nodes,
            edges=edges,
            evidence=event.get("event_id", "")
        )
