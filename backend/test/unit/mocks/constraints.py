import sys
import types


MAPPING_ENTITIES_TYPE = {
    "users": "User",
    "hosts": "Host",
    "ips": "IP",
    "domains": "Domain",
    "file_hashes": "FileHash",
    "urls": "URL",
    "processes": "Process",
    "emails": "Email",
    "cloud_resources": "CloudResource",
    "cves": "CVE",
}

REVERSED_TYPE = {v: k for k, v in MAPPING_ENTITIES_TYPE.items()}

MAPPING_ENTITIES_KEY = {
    "User": "username",
    "Host": "hostname",
    "IP": "value",
    "Domain": "name",
    "FileHash": "hash_value",
}

TENANT_DATABASE = {
    "default": "default",
    "acme": "acme",
    "google": "google_db",
    "internal": "internal_db",
}

SIEM_INCLUDE = {
    "nodes": {
        "users":            ["user"],
        "ips":              ["source_ip"],          
        "hosts":            ["destination_host"],   
        "urls":             ["url"], 
        "sender_emails":    ["sender_email"],       
        "recipient_emails": ["recipient_email"],
        "file_hashes":      ["file_hash"] 
    },
    "edges": [
        ("source_ip",        "destination_host"),   
        ("user",            "destination_host"),   
        ("sender_email",    "recipient_email"),    
        ("sender_email",    "url"),
        ("sender_email",    "file_hash"), # Khôi phục liên kết Email -> File độc hại đính kèm (ATTACHED)
        ("user",            "sender_email") # Khôi phục mối liên kết User -> Email (OWNS) khi gửi mail
    ]
}

# ── EDR ───────────────────────────────────────────────────────────────────────
EDR_INCLUDE = {
    "nodes": {
        "users":            ["user"],
        "hosts":            ["destination_host"],
        "ips":              ["destination_ip"],
        "domains":          ["destination_domain"],
        "file_hashes":      ["file_hash"],
        "processes":        ["process_name"],
        "parent_processes": ["parent_process"],
        "cves":             ["cve_id"],
        "urls":             ["url"]
    },
    "edges": [
        # Core & Network
        ("user",             "destination_host"), 
        ("file_hash",        "destination_host"), 
        ("destination_host", "destination_ip"),
        ("destination_host", "destination_domain"),
        ("destination_host", "url"),
        
        # Process Relations
        ("parent_process",   "process_name"),     # (Process, Process) -> SPAWNED
        ("process_name",     "destination_host"), # (Process, Host) -> RUNS_ON
        ("process_name",     "user"),             # (Process, User) -> EXECUTED_BY
        ("process_name",     "file_hash"),        # (Process, FileHash) -> LOADED (Quan trọng!)
        ("process_name",     "destination_ip"),   # (Process, IP) -> CONNECTED_TO
        ("process_name",     "destination_domain"),# (Process, Domain) -> CONNECTED_TO

        # Vulnerability
        ("cve_id",           "destination_host"), 
        ("cve_id",           "process_name"),     
    ]
}

# ── Cloud ─────────────────────────────────────────────────────────────────────
CLOUD_INCLUDE = {
    "nodes": {
        "users":           ["user"],               
        "hosts":           ["source_host"],
        "ips":             ["destination_ip"],
        "domains":         ["destination_domain"],
        "urls":            ["url"],
        "cloud_resources": ["resource_id"],        
        "cves":            ["cve_id"],             
    },
    "edges": [
        ("source_host",       "destination_ip"),     
        ("source_host",       "destination_domain"), 
        ("destination_domain", "destination_ip"),     
        ("source_host",       "url"),
        
        # Cloud Access & Mapping
        ("user",              "resource_id"),    # (User, CloudResource) -> ACCESSED
        ("resource_id",       "destination_ip"), # (CloudResource, IP) -> ASSIGNED_TO
        ("resource_id",       "source_host"),    # (CloudResource, Host) -> RUNS_ON
        
        # Lỗ hổng Cloud
        ("cve_id",            "resource_id"),    # (CVE, CloudResource) -> AFFECTS
    ]
}

def install():

    mod = types.ModuleType("backend.database.constraints")

    mod.MAPPING_ENTITIES_TYPE = MAPPING_ENTITIES_TYPE
    mod.REVERSED_TYPE = REVERSED_TYPE
    mod.MAPPING_ENTITIES_KEY = MAPPING_ENTITIES_KEY
    mod.TENANT_DATABASE = TENANT_DATABASE

    sys.modules["backend.database.constraints"] = mod