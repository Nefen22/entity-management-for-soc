from datetime import datetime, timezone
import json
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
LOG_DIR = CURRENT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

def write_audit_log(action: str, entity_type: str, entity_id: str,time:str, change: dict | None = None):
    entry = {
        "timestamp": time,
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "change": change or {}
    }
    with open(LOG_DIR/"audit_log.json", "a") as f:
        f.write(json.dumps(entry) + ",\n")