from .base_parser import BaseParser
from .edge_parser import Vertex
from database.constraints import MAPPING_ENTITIES_TYPE, MAPPING_REALITIONSHIPS

class SiemPaser(BaseParser):
    @classmethod
    def from_event(cls, event: dict):
        nodes = []
        nodes.append(Vertex(type = MAPPING_ENTITIES_TYPE["users"], value=event.get("user")))
        nodes.append(Vertex(type = MAPPING_ENTITIES_TYPE["hosts"], value=event.get("destination_host")))
        nodes.append(Vertex(type = MAPPING_ENTITIES_TYPE["ips"], value=event.get("source_ip")))
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
