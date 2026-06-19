from .base_parser import BaseParser, clean

class EdrPaser(BaseParser):
    @classmethod
    def from_event(cls, event: dict):
        return cls(
            source_type=event.get("source_type"),

            user=clean(lst=event.get("user")),
            host=clean(lst=event.get("destination_host"))
                  or clean(lst=event.get("source_host")),

            ip=clean(lst=event.get("destination_ip")),
            domain=clean(lst=event.get("destination_domain")),
            file_hash=clean(lst=event.get("file_hash")),

            evidence=event.get("event_id", "")
        )
#     "event_id": "evt-002",
#     "timestamp": "2024-06-01T08:05:00Z",
#     "source_type": "edr",
#     "event_type": "file_execution",
#     "user": "john.doe",
#     "destination_host": "DESKTOP-001",
#     "file_hash": "44d88612fea8a8f36de82e1278abb02f"
