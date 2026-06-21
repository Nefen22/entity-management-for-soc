from .base_parser import BaseParser, clean
from .edge_parser import Vertex

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
        nodes, edges = cls.split_nodes_edges(cls, event=event, include=EDR_INCLUDE)
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
