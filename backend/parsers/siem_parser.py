from .base_parser import BaseParser, clean

class SiemPaser(BaseParser):
    @classmethod
    def from_event(cls, event: dict):
        return cls(
            source_type=event.get("source_type"),

            user=clean(lst=event.get("user")),
            ip=clean(lst=event.get("source_ip")),
            host=clean(lst=event.get("destination_host")),

            evidence=event.get("event_id", "")
        )
