from database.constraints import MAPPING_RELATIONSHIPS, ALERT_RELATIONSHIPS

def check_rels(rels: str):
    if rels is None:
        return True
    clean_rel = rels.lstrip(':')
    valid_rels = set(MAPPING_RELATIONSHIPS.values()) | set(ALERT_RELATIONSHIPS.values())
    return clean_rel in valid_rels