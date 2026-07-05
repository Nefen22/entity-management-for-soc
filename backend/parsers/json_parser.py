from .base_parser import BaseParser, clean
from .edge_parser import Vertex
from database.constraints import CANONICAL_SCHEMA, EDR_SCHEMA, SIEM_SCHEMA, CLOUD_SCHEMA

json_format={
    "edr": EDR_SCHEMA,     #format for EDR
    "siem": SIEM_SCHEMA,   #format for SIEM
    "cloud": CLOUD_SCHEMA,  #format for CLOUD
    "canonical": CANONICAL_SCHEMA
}

class JsonParser(BaseParser):
    @classmethod
    def from_event(cls, event: dict, key_word :str):
        if key_word not in json_format:
            raise ValueError(f"Unsupported log source: {key_word}")
        nodes, edges = cls.split_nodes_edges(cls, event=event, include=json_format[key_word])
        if nodes == [] and edges == []:
            raise ValueError("No nodes or edges found in the event.")
        return cls(
            source_type=event.get("source_type"),
            nodes=nodes,
            edges=edges,
            evidence=event.get("event_id", "")
        )