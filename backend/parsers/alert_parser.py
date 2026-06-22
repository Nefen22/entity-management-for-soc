import re 
from .base_parser import BaseParser
from .edge_parser import Vertex
from database.constraints import MAPPING_REALITIONSHIPS, MAPPING_ENTITIES_TYPE
import ipaddress

DOMAIN=re.compile(r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b")

MD5=re.compile(r"\b[a-fA-F0-9]{32}\b")
SHA1=re.compile(r"\b[a-fA-F0-9]{40}\b")
SHA256=re.compile(r"\b[a-fA-F0-9]{64}\b")
HASH=[MD5, SHA1, SHA256]

def list_vertex(type:  str, lst:list):
    return [Vertex(type = MAPPING_ENTITIES_TYPE[type], value=ele) for ele in lst]

class AlertParser(BaseParser):
    @classmethod
    def from_event(cls, event: dict):
        message = event.get("message")
        list_ip=[]
        list_domain=[]
        list_hash=[]
        for token in message.split():
            try:
                ipaddress.ip_address(token)
                list_ip.append(token)
            except ValueError:
                None
        list_domain.extend(DOMAIN.findall(message))
        for pattern_hash in HASH:
            list_hash.extend(pattern_hash.findall(message))

        nodes = []
        nodes += list_vertex("ips", list_ip) +  list_vertex("domains", list_domain) + list_vertex("file_hashes", list_hash)
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
