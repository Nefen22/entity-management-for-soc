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
    ("User", "Host"): "LOGGED_IN",
    ("Host", "IP"): "CONNECTED_TO",
    ("FileHash", "Host"): "EXECUTED_ON",

    # ===== Network =====
    ("Host", "Domain"): "RESOLVED",
    ("Domain", "IP"): "RESOLVES_TO",
    ("Host", "URL"): "REQUESTED",

    # ===== Process =====
    ("Process", "Host"): "RUNS_ON",
    ("Process", "User"): "EXECUTED_BY",
    ("Process", "FileHash"): "LOADED",
    ("Process", "IP"): "CONNECTED_TO",
    ("Process", "URL"): "REQUESTED",

    # ===== URL / Domain =====
    ("URL", "Domain"): "BELONGS_TO",

    # ===== Email =====
    ("User", "Email"): "OWNS",
    ("Email", "Domain"): "HOSTED_BY",
    ("Email", "URL"): "CONTAINS",
    ("Email", "FileHash"): "ATTACHED",

    # ===== Cloud =====
    ("CloudResource", "IP"): "ASSIGNED_TO",
    ("CloudResource", "Host"): "RUNS_ON",
    ("CloudResource", "User"): "OWNED_BY",

    ("User", "CloudResource"): "ACCESSED",

    # ===== Vulnerability =====
    ("CVE", "Host"): "AFFECTS",
    ("CVE", "Process"): "AFFECTS",
    ("CVE", "CloudResource"): "AFFECTS",
    ("CVE", "FileHash"): "EXPLOITS",
}

SIEM_INCLUDE = {
    # existing
    "users":  ["user"],
    "hosts":  ["destination_host"],
    "ips":    ["source_ip"],
    # new
    "urls":   ["url", "request_url"],
    "emails": ["sender_email", "recipient_email"],
}

CLOUD_INCLUDE = {
    # existing
    "hosts":   ["source_host"],
    "ips":     ["destination_ip"],
    "domains": ["destination_domain"],
    # new
    "urls":            ["resource_url"],
    "cloud_resources": ["resource_id", "instance_id", "bucket_name"],
    "emails":          ["user_email"],
    "cves":            ["vulnerability_id"],
}

EDR_INCLUDE = {
    # existing
    "users":       ["user"],
    "hosts":       ["destination_host"],
    "ips":         ["destination_ip"],
    "domains":     ["destination_domain"],
    "file_hashes": ["file_hash"],
    # new
    "urls":        ["url", "request_url"],
    "processes":   ["process_name", "parent_process"],
    "cves":        ["cve_id"],
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