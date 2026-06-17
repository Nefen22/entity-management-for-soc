from .base_parser import BaseParser

class CloudPaser(BaseParser):
    @classmethod
    def from_event(cls, event: dict):
        return cls(
            source_type=event.get("source_type"),

            host=event.get("source_host"),

            ip=event.get("destination_ip"),
            domain=event.get("destination_domain"),

            evidence=event.get("event_id", "")
        )
