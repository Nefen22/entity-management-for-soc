import re 
from .base_parser import BaseParser
from .edge_parser import Vertex, EdgePaser
from database.constraints import MAPPING_ENTITIES_TYPE, ALERT_RELATIONSHIPS, DOMAIN, CVE
import iocextract
import json

EMAIL_RE = re.compile(
    r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
)

def clean_email(value: str) -> str:
    m = EMAIL_RE.search(value)
    return m.group(0) if m else value

def normalize_url(value: str) -> str:
    if not value:
        return value

    value = value.strip()

    value = value.strip("<>\"'")

    value = re.sub(r'\[\.\]|\(\.\)|\{\.\}', '.', value)
    value = re.sub(r'\[:\]|\(:\)|\{:\}', ':', value)

    value = re.sub(r'^hxxps?', lambda m: m.group(0).replace("hxxp", "http"), value, flags=re.IGNORECASE)

    value = re.sub(r'^(https?)\s*:\s*//', r'\1://', value, flags=re.IGNORECASE)

    value = re.sub(r'\s+', '', value)

    return value

def extract_enitty(message:str):
    result = {}
    
    ips = set(iocextract.extract_ipv4s(message))
    if ips:
        result['ips'] = ips
        
    urls = set(iocextract.extract_urls(message))
    if urls:
        result['urls'] = {normalize_url(url) for url in urls}
        
    emails = set(iocextract.extract_emails(message))
    if emails:
        result['emails'] =  {
                clean_email(email)
                for email in emails
            }
        
    hashes = set(iocextract.extract_hashes(message))
    if hashes:
        result['file_hashes'] = hashes
    domains = set(DOMAIN.findall(message))
    if domains:
        result["domains"] = domains

    cves = set(CVE.findall(message))
    if cves:
        result["cves"] = cves
    print("iocextract", result)
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
                    connect_type=ALERT_RELATIONSHIPS[(s_node.type,
                                                    t_node.type)] if (s_node.type,
                                                    t_node.type) in ALERT_RELATIONSHIPS.keys() else "",
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