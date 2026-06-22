from .base_parser import BaseParser, clean
from .edge_parser import Vertex
from database.constraints import EDR_INCLUDE, SIEM_INCLUDE, CLOUD_INCLUDE

json_format={
    "edr": EDR_INCLUDE,     #format for EDR
    "siem": SIEM_INCLUDE,   #format for SIEM
    "cloud": CLOUD_INCLUDE  #format for CLOUD
}

class JsonParser(BaseParser):
    @classmethod
    def from_event(cls, event: dict, key_word :str):
        if key_word not in json_format:
            raise ValueError(f"Unsupported log source: {key_word}")
        nodes, edges = cls.split_nodes_edges(cls, event=event, include=json_format[key_word])
        return cls(
            source_type=event.get("source_type"),
            nodes=nodes,
            edges=edges,
            evidence=event.get("event_id", "")
        )