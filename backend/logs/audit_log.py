from datetime import datetime, timezone
import json
from pathlib import Path

PATH = Path("/app/backend/logs/audit_log.json")
PATH.parent.mkdir(parents=True, exist_ok=True)

def write_audit_log(action: str, entity_type: str, entity_id: str, change: dict | None = None):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "change": change or {}
    }
    with open(PATH, "a") as f:
        f.write(json.dumps(entry) + ",\n")