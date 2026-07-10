import re 
from .base_parser import BaseParser
from .edge_parser import Vertex, EdgePaser
from database.constraints import MAPPING_ENTITIES_TYPE, MAPPING_RELATIONSHIPS, DOMAIN, CVE
import iocextract
import json

def extract_enitty(message:str):
    result = {}
    
    ips = list(iocextract.extract_ipv4s(message))
    if ips:
        result['ips'] = ips
        
    urls = list(iocextract.extract_urls(message))
    if urls:
        result['urls'] = urls
        
    emails = list(iocextract.extract_emails(message))
    if emails:
        result['emails'] = emails
        
    hashes = list(iocextract.extract_hashes(message))
    if hashes:
        result['file_hashes'] = hashes
    domains = DOMAIN.findall(message)
    if domains:
        result["domains"] = domains

    cves = CVE.findall(message)
    if cves:
        result["cves"] = cves

    return result

def list_vertex(type:  str, lst:list):
    return [Vertex(type = MAPPING_ENTITIES_TYPE[type], value=ele) for ele in lst]

class AlertParser(BaseParser):
    @classmethod
    def from_event(cls, event: dict):
        message = event.get("message") if event.get("message") else json.dumps(event)
        lst = []
        time = str(event.get("timestamp"))
        nodes= []
        extract = extract_enitty(message)
        for k, v in extract.items():
            for ele in v:
                nodes.append(Vertex(type = MAPPING_ENTITIES_TYPE[k], value = ele))
        edges = [(EdgePaser(src=s_node,
                    dest=t_node,
                    connect_type=MAPPING_RELATIONSHIPS[(s_node.type,
                                                    t_node.type)] if (s_node.type,
                                                    t_node.type) in MAPPING_RELATIONSHIPS.keys() else "",
                    time=time,
                    evidence=event["event_id"]))
                   for s_node in nodes for t_node in nodes if s_node != t_node]
        edges=[edge for edge in edges if edge.connect_type != ""]
        return cls(
            source_type=event.get("source_type"),
            nodes=nodes,
            edges=edges,
            evidence=event.get("event_id", "")
        )