import re 
from .base_parser import BaseParser, clean
import ipaddress

DOMAIN=re.compile(r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b")

MD5=re.compile(r"\b[a-fA-F0-9]{32}\b")
SHA1=re.compile(r"\b[a-fA-F0-9]{40}\b")
SHA256=re.compile(r"\b[a-fA-F0-9]{64}\b")
HASH=[MD5, SHA1, SHA256]

class AlertParser(BaseParser):
    @classmethod
    def from_event(cls, event: dict):
        message = event.get("message")
        print(message)
        list_ip=[]
        list_domain=[]
        list_hash=[]
        for token in message.split():
            try:
                ipaddress.ip_address(token)
                list_ip.append(token)
            except ValueError:
                pass
        list_domain.extend(DOMAIN.findall(message))
        for pattern_hash in HASH:
            list_hash.extend(pattern_hash.findall(message))
        return cls(
            source_type=event.get("source_type"),
            ip=clean(list_ip),
            domain=clean(list_domain),
            file_hash=clean(list_hash),

            evidence=event.get("event_id", "")
        )
