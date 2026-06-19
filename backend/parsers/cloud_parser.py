from .base_parser import BaseParser, clean

class CloudPaser(BaseParser):
    @classmethod
    def from_event(cls, event: dict):
        return cls(
            source_type=event.get("source_type"),

            host=clean(lst=event.get("source_host")),

            ip=clean(lst=event.get("destination_ip")),
            domain=clean(lst=event.get("destination_domain")),

            evidence=event.get("event_id", "")
        )
