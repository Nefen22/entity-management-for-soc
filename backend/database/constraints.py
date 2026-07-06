import re

MAPPING_ENTITIES_TYPE={
    # existing
    "ips": "IP",
    "users": "User",
    "hosts": "Host",
    "domains": "Domain",
    "file_hashes": "FileHash",
    "urls": "URL",
    "processes": "Process",
    "cloud_resources": "CloudResource",
    "emails": "Email",
    "cves": "CVE",
    "IP": "IP",
    "User": "User",
    "Host": "Host",
    "Domain": "Domain",
    "FileHash": "FileHash",
    "URL": "URL",
    "Process": "Process",
    "CloudResource": "CloudResource",
    "Email": "Email",
    "CVE": "CVE",
    
    "sender_emails":    "Email",
    "recipient_emails": "Email",
    "parent_processes": "Process",
}

REVERSED_TYPE = {v: k for k, v in MAPPING_ENTITIES_TYPE.items()}

MAPPING_ENTITIES_KEY={
    # existing
    "ips": "value",
    "users": "username",
    "hosts": "hostname",
    "domains": "name",
    "file_hashes": "hash_value",
    "IP": "value",
    "User": "username",
    "Host": "hostname",
    "Domain": "name",
    "FileHash": "hash_value",
    # new
    "urls": "url",
    "processes": "process_name",
    "cloud_resources": "resource_id",
    "emails": "address",
    "cves": "cve_id",
    "URL": "url",
    "Process": "process_name",
    "CloudResource": "resource_id",
    "Email": "address",
    "CVE": "cve_id",
    
}

MAPPING_ENTITIES_KEY_CLEAN={
    # existing
    "IP": "value",
    "User": "username",
    "Host": "hostname",
    "Domain": "name",
    "FileHash": "hash_value",
    # new
    "URL": "url",
    "Process": "process_name",
    "CloudResource": "resource_id",
    "Email": "address",
    "CVE": "cve_id",
}

MAPPING_ENTITY = {
    # existing
    "ips": "ip",
    "users": "user",
    "hosts": "host",
    "domains": "domain",
    "file_hashes": "hash",
    # new
    "urls": "url",
    "processes": "process",
    "cloud_resources": "cloud_resource",
    "emails": "email",
    "cves": "cve",
}

MAPPING_RELATIONSHIPS = {
    # ===== Core =====
    ("User", "Host"):     "LOGGED_IN",
    ("Host", "IP"):       "CONNECTED_TO",
    ("IP", "Host"):       "CONNECTED_TO",
    ("FileHash", "Host"): "EXECUTED_ON",

    # ===== Network =====
    ("Host", "IP"):       "CONNECTED_TO",
    ("IP", "Host"):       "CONNECTED_TO",
    ("IP", "IP"):         "CONNECTED_TO",

    ("Host", "Domain"):   "RESOLVED",
    ("IP", "Domain"):     "RESOLVED",
    ("Domain", "IP"):     "RESOLVES_TO",

    ("Host", "URL"):      "REQUESTED",
    ("IP", "URL"):        "REQUESTED",

    # ===== Process =====
    ("Process", "Host"):     "RUNS_ON",
    ("Process", "User"):     "EXECUTED_BY",
    ("Process", "FileHash"): "LOADED",
    ("Process", "IP"):       "CONNECTED_TO",
    ("Process", "URL"):      "REQUESTED",
    ("Process", "Process"):  "SPAWNED",     
    ("Process", "Domain"):   "CONNECTED_TO",

    # ===== URL / Domain =====
    ("URL", "Domain"): "BELONGS_TO",

    # ===== Email =====
    ("User", "Email"):     "OWNS",
    ("Email", "Domain"):  "HOSTED_BY",
    ("Email", "URL"):     "CONTAINS",
    ("Email", "FileHash"): "ATTACHED",
    ("Email", "Email"):   "SENT_TO",         

    # ===== Cloud =====
    ("User", "CloudResource"): "ACCESSED",
    ("CloudResource", "IP"):   "ASSIGNED_TO",
    ("CloudResource", "Host"): "RUNS_ON",

    # ===== Vulnerability =====
    ("CVE", "Host"):          "AFFECTS",
    ("CVE", "Process"):       "AFFECTS",
    ("CVE", "CloudResource"): "AFFECTS",
}

# ── SIEM ──────────────────────────────────────────────────────────────────────
SIEM_SCHEMA = {
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
        ("sender_email",    "file_hash"),
        ("user",            "sender_email") 
    ]
}

# ── EDR ───────────────────────────────────────────────────────────────────────
EDR_SCHEMA = {
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
        ("user",             "destination_host"), 
        ("file_hash",        "destination_host"), 
        ("destination_host", "destination_ip"),
        ("destination_host", "destination_domain"),
        ("destination_host", "url"),
        
        ("parent_process",   "process_name"),     # (Process, Process) -> SPAWNED
        ("process_name",     "destination_host"), # (Process, Host) -> RUNS_ON
        ("process_name",     "user"),             # (Process, User) -> EXECUTED_BY
        ("process_name",     "file_hash"),        # (Process, FileHash) -> LOADED 
        ("process_name",     "destination_ip"),   # (Process, IP) -> CONNECTED_TO
        ("process_name",     "destination_domain"),# (Process, Domain) -> CONNECTED_TO

        ("cve_id",           "destination_host"), 
        ("cve_id",           "process_name"),     
    ]
}

# ── Cloud ─────────────────────────────────────────────────────────────────────
CLOUD_SCHEMA = {
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
        
        ("user",              "resource_id"),    
        ("resource_id",       "destination_ip"), 
        ("resource_id",       "source_host"),    
        # Lỗ hổng Cloud
        ("cve_id",            "resource_id"),   
    ]
}

CANONICAL_SCHEMA = {
    "nodes": {
        # Identity
        "users":              ["user"],

        # Network
        "ips":                ["source_ip", "destination_ip"],
        "hosts":              ["source_host", "destination_host"],
        "domains":            ["source_domain", "destination_domain"],
        "urls":               ["url"],

        # Email
        "sender_emails":      ["sender_email"],
        "recipient_emails":   ["recipient_email"],

        # Endpoint
        "processes":          ["process_name"],
        "parent_processes":   ["parent_process"],
        "file_hashes":        ["file_hash"],

        # Cloud
        "cloud_resources":    ["resource_id"],

        # Vulnerability
        "cves":               ["cve_id"]
    },

    "edges": [

        # ---------- Network ----------

        ("source_ip", "destination_ip"),
        ("source_ip", "destination_domain"),
        ("source_ip", "url"),
        ("source_ip", "destination_host"),

        ("source_host", "destination_host"),
        ("source_host", "destination_ip"),
        ("source_host", "destination_domain"),
        ("source_host", "url"),

        ("destination_domain", "destination_ip"),

        # ---------- User ----------
        ("user",                "destination_host"),
        ("user",                "source_host"),
        ("user",                "sender_email"),
        ("user",                "resource_id"),

        # ---------- Email ----------
        ("sender_email",        "recipient_email"),
        ("sender_email",        "url"),
        ("sender_email",        "file_hash"),

        # ---------- Endpoint ----------
        ("parent_process",      "process_name"),
        ("process_name",        "destination_host"),
        ("process_name",        "user"),
        ("process_name",        "file_hash"),
        ("process_name",        "destination_ip"),
        ("process_name",        "destination_domain"),

        # ---------- File ----------
        ("file_hash",           "destination_host"),

        # ---------- Host ----------
        ("destination_host",    "destination_ip"),
        ("destination_host",    "destination_domain"),
        ("destination_host",    "url"),

        # ---------- Cloud ----------
        ("resource_id",         "destination_ip"),
        ("resource_id",         "source_host"),

        # ---------- Vulnerability ----------
        ("cve_id",              "destination_host"),
        ("cve_id",              "process_name"),
        ("cve_id",              "resource_id")
    ]
}

TENANT_DATABASE = {}

# ── IP ───────────────────────────────────────────────────────────────────────
IPV4 = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}"
    r"(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
)

# ── URL ──────────────────────────────────────────────────────────────────────
URL = re.compile(
    r"https?://"
    r"(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}"
    r"(?::\d{1,5})?"
    r"(?:/[^\s\"'<>]*)?"
)

# ── File Hash ────────────────────────────────────────────────────────────────
MD5    = re.compile(r"\b[a-fA-F0-9]{32}\b")
SHA1   = re.compile(r"\b[a-fA-F0-9]{40}\b")
SHA256 = re.compile(r"\b[a-fA-F0-9]{64}\b")
HASH   = [MD5, SHA1, SHA256]

# ── Email ────────────────────────────────────────────────────────────────────
EMAIL = re.compile(
    r"\b[a-zA-Z0-9._%+\-]+@"
    r"(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b"
)

# ── CVE ──────────────────────────────────────────────────────────────────────
CVE = re.compile(r"\bCVE-\d{4}-\d{4,}\b", re.IGNORECASE)

# ── Cloud Resource (chỉ các định dạng chuẩn) ─────────────────────────────────
AWS_ARN      = re.compile(r"\barn:[a-z0-9\-]+:[a-z0-9\-]+:[a-z0-9\-]*:\d{12}:[^\s\"']+")
AWS_S3       = re.compile(r"\bs3://[a-z0-9.\-]+(?:/[^\s\"']*)?\b")
AWS_INSTANCE = re.compile(r"\bi-[0-9a-f]{8,17}\b")
CLOUD_RESOURCE = [AWS_ARN, AWS_S3, AWS_INSTANCE]

DOMAIN = re.compile(
    r"\b(?!(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b)"
    r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"
    r"(?:com|net|org|edu|gov|mil|int|io|co|biz|info|vn|xyz|me|online|live|tech)\b",
    re.IGNORECASE
)


# ── Gom tất cả theo entity type ──────────────────────────────────────────────
ALL_PATTERNS: dict[str, list[re.Pattern]] = {
    "ips":            [IPV4],
    "domains":         [DOMAIN],
    "urls":           [URL],
    "file_hashes":      HASH,
    "emails":         [EMAIL],
    "cves":           [CVE],
    "cloud_resources": CLOUD_RESOURCE,
}