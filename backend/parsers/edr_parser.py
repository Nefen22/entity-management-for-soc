from .base_parser import BaseParser, clean
from .edge_parser import Vertex
from database.constraints import MAPPING_ENTITIES_TYPE, MAPPING_REALITIONSHIPS

EDR_INCLUDE = {
    "users":["user"],
    "hosts":["destination_host"],
    "ips":["destination_ip"],
    "domains":["destination_domain"],
    "file_hashes": ["file_hash"]
}

class EdrPaser(BaseParser):
    @classmethod
    def from_event(cls, event: dict):
        nodes = []
        for k, v_lst in EDR_INCLUDE.items():
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
#     "event_id": "evt-002",
#     "timestamp": "2024-06-01T08:05:00Z",
#     "source_type": "edr",
#     "event_type": "file_execution",
#     "user": "john.doe",
#     "destination_host": "DESKTOP-001",
#     "file_hash": "44d88612fea8a8f36de82e1278abb02f"
