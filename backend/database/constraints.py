import re

MAPPING_ENTITIES_TYPE={
    # existing
    "ips": "IP",
    "users": "User",
    "hosts": "Host",
    "domains": "Domain",
    "file_hashes": "FileHash",
    # new
    "urls": "URL",
    "processes": "Process",
    "cloud_resources": "CloudResource",
    "emails": "Email",
    "cves": "CVE",
    # reverse lookup (Type → Type)
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
    ("Host", "Domain"):   "RESOLVED",
    ("Domain", "IP"):     "RESOLVES_TO",
    ("Host", "URL"):      "REQUESTED",
    ("Host", "IP"):       "CONNECTED_TO", # Bổ sung Host -> IP trực tiếp

    # ===== Process =====
    ("Process", "Host"):     "RUNS_ON",
    ("Process", "User"):     "EXECUTED_BY",
    ("Process", "FileHash"): "LOADED",
    ("Process", "IP"):       "CONNECTED_TO",
    ("Process", "URL"):      "REQUESTED",
    ("Process", "Process"):  "SPAWNED",       
    ("Process", "Domain"):   "CONNECTED_TO",  # Bổ sung Process -> Domain (Cho evt-016)

    # ===== URL / Domain =====
    ("URL", "Domain"): "BELONGS_TO",

    # ===== Email =====
    ("User", "Email"):    "OWNS",
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
SIEM_INCLUDE = {
    "nodes": {
        "users":            ["user"],
        "ips":              ["source_ip"],          
        "hosts":            ["destination_host"],   
        "urls":             ["url"], 
        "sender_emails":    ["sender_email"],       
        "recipient_emails": ["recipient_email"],    
    },
    "edges": [
        ("source_ip",        "destination_host"),   
        ("user",            "destination_host"),   
        ("sender_email",    "recipient_email"),    
        ("sender_email",    "url"),                
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
        
        # Process Relations (Sửa lỗi cô lập hành vi như evt-016)
        ("parent_process",   "process_name"),     
        ("process_name",     "destination_host"), # Process RUNS_ON Host
        ("process_name",     "user"),             # Process EXECUTED_BY User
        ("process_name",     "destination_ip"),   # Process CONNECTED_TO IP
        ("process_name",     "destination_domain"),# Process CONNECTED_TO Domain

        # Vulnerability (Sửa lỗi mất CVE dữ liệu EDR)
        ("cve_id",           "destination_host"), # CVE AFFECTS Host
        ("cve_id",           "process_name"),     # CVE AFFECTS Process
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
        
        # SỬA TẠI ĐÂY: Thay "cloud_resources" bằng tên trường thực tế "resource_id"
        ("user",              "resource_id"),    # Sẽ map thành (User, CloudResource) -> ACCESSED
        ("resource_id",       "destination_ip"), # Sẽ map thành (CloudResource, IP) -> ASSIGNED_TO
        ("resource_id",       "source_host"),    # Sẽ map thành (CloudResource, Host) -> RUNS_ON
        
        # Lỗ hổng Cloud
        ("cve_id",            "resource_id"),    # Sẽ map thành (CVE, CloudResource) -> AFFECTS
    ]
}

TENANT_DATABASE = {
    "acme": "Tenant_Acme",
    "google": "Tenant_Google",
    "internal": "Tenant_Internal"
}


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

# ── Gom tất cả theo entity type ──────────────────────────────────────────────
ALL_PATTERNS: dict[str, list[re.Pattern]] = {
    "ips":            [IPV4],
    "urls":           [URL],
    "file_hashes":      HASH,
    "emails":         [EMAIL],
    "cves":           [CVE],
    "cloud_resources": CLOUD_RESOURCE,
}