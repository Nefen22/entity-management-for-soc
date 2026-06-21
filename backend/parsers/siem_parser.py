from .base_parser import BaseParser
from .edge_parser import Vertex
from database.constraints import MAPPING_ENTITIES_TYPE, MAPPING_REALITIONSHIPS

SIEM_INCLUDE = {
    "users" : ["user"],
    "hosts" : ["destination_host"],
    "ips"   : ["source_ip"]
}   

class SiemPaser(BaseParser):
    @classmethod
    def from_event(cls, event: dict):
        nodes, edges = cls.split_nodes_edges(cls, event=event, include=SIEM_INCLUDE)
        return cls(
            source_type=event.get("source_type"),
            nodes=nodes,
            edges=edges,
            evidence=event.get("event_id", "")
        )
