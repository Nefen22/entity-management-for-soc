from .base_parser import BaseParser

class SiemPaser(BaseParser):
    @classmethod
    def from_event(cls, event: dict):
        return cls(
            source_type=event.get("source_type"),

            user=event.get("user"),
            ip=event.get("source_ip"),
            host=event.get("destination_host"),

            evidence=event.get("event_id", "")
        )
