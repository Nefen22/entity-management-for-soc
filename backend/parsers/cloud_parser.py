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
        nodes, edges = cls.split_nodes_edges(cls, event=event, include=CLOUD_INCLUDE)
        return cls(
            source_type=event.get("source_type"),
            nodes=nodes,
            edges=edges,
            evidence=event.get("event_id", "")
        )
