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
    ("User", "Host"):          "LOGGED_IN",
    ("User", "IP"):            "LOGGED_IN_FROM",

    ("Host", "IP"):            "CONNECTED_TO",
    ("IP", "Host"):            "CONNECTED_TO",
    ("IP", "IP"):              "CONNECTED_TO",

    ("FileHash", "Host"):      "EXECUTED_ON",

    # ===== Network =====
    ("Host", "Domain"):        "RESOLVED",
    ("IP", "Domain"):          "RESOLVED",
    ("Domain", "IP"):          "RESOLVES_TO",

    ("Host", "URL"):           "REQUESTED",
    ("IP", "URL"):             "REQUESTED",
    ("Process", "URL"):        "REQUESTED",

    ("URL", "Domain"):         "BELONGS_TO",
    ("URL", "IP"):             "RESOLVES_TO",
    ("URL", "FileHash"):       "DOWNLOADS",

    # ===== Process =====
    ("Process", "Host"):       "RUNS_ON",
    ("Process", "User"):       "EXECUTED_BY",
    ("Process", "Process"):    "SPAWNED",
    ("Process", "FileHash"):   "LOADED",
    ("Process", "IP"):         "CONNECTED_TO",
    ("Process", "Domain"):     "CONNECTED_TO",

    # ===== Email =====
    ("User", "Email"):         "OWNS",
    ("Email", "Domain"):       "HOSTED_BY",
    ("Email", "URL"):          "CONTAINS",
    ("Email", "FileHash"):     "ATTACHED",
    ("Email", "Email"):        "SENT_TO",

    # ===== Cloud =====
    ("User", "CloudResource"):     "ACCESSED",
    ("CloudResource", "Host"):     "RUNS_ON",
    ("CloudResource", "IP"):       "ASSIGNED_TO",
    ("CloudResource", "Domain"):   "CONNECTED_TO",

    # ===== Vulnerability =====
    ("CVE", "Host"):               "AFFECTS",
    ("CVE", "Process"):            "AFFECTS",
    ("CVE", "CloudResource"):      "AFFECTS",

    # ===== Threat Intelligence =====
    ("Domain", "FileHash"):        "HOSTS",
    ("IP", "FileHash"):            "HOSTS",
    ("URL", "CVE"):                "EXPLOITS",
    ("Process", "CVE"):            "EXPLOITS",

    # ===== Malware =====
    ("FileHash", "Process"):       "LOADED_BY",
    ("FileHash", "URL"):           "DOWNLOADED_FROM",
    ("FileHash", "Domain"):        "DOWNLOADED_FROM",
    ("FileHash", "IP"):            "DOWNLOADED_FROM",

    # ===== Lateral Movement =====
    ("Host", "Host"):              "CONNECTED_TO",
    ("User", "CloudResource"):     "AUTHENTICATED_TO",

    # ===== IOC =====
    ("Domain", "Domain"):          "RELATED_TO",
    ("IP", "Domain"):              "CONNECTED_TO",
    ("Domain", "URL"):             "HOSTS",
}

ALERT_RELATIONSHIPS = {
    ("User", "Host"): "RELATED_TO",
    ("User", "IP"): "RELATED_TO",

    ("Host", "IP"): "RELATED_TO",

    ("Host", "Domain"): "RELATED_TO",
    ("Host", "URL"): "RELATED_TO",

    ("IP", "Domain"): "RELATED_TO",
    ("IP", "URL"): "RELATED_TO",

    ("Domain", "URL"): "RELATED_TO",

    ("Process", "Host"): "RELATED_TO",
    ("Process", "User"): "RELATED_TO",
    ("Process", "FileHash"): "RELATED_TO",

    ("Email", "URL"): "RELATED_TO",
    ("Email", "FileHash"): "RELATED_TO",
    ("Email", "Email"): "RELATED_TO",

    ("CloudResource", "Host"): "RELATED_TO",
    ("CloudResource", "IP"): "RELATED_TO",

    ("CVE", "Host"): "RELATED_TO",
    ("CVE", "Process"): "RELATED_TO",
}
# ── SIEM ──────────────────────────────────────────────────────────────────────
SIEM_SCHEMA = {
    "nodes": {
        "users": [
            "user"
        ],
        "ips": [
            "source_ip",
            "destination_ip"
        ],
        "hosts": [
            "destination_host"
        ],
        "domains": [
            "destination_domain"
        ],
        "urls": [
            "url"
        ],
        "sender_emails": [
            "sender_email"
        ],
        "recipient_emails": [
            "recipient_email"
        ],
        "file_hashes": [
            "file_hash"
        ]
    },

    "edges": [
        # Network
        ("source_ip", "destination_ip"),
        ("source_ip", "destination_host"),
        ("destination_host", "destination_ip"),
        ("destination_host", "destination_domain"),
        ("source_ip", "url"),
        ("destination_host", "url"),

        # User
        ("user", "destination_host"),
        ("user", "sender_email"),

        # Email
        ("sender_email", "recipient_email"),
        ("sender_email", "url"),
        ("sender_email", "file_hash"),
    ]
}

# ── EDR ───────────────────────────────────────────────────────────────────────
EDR_SCHEMA = {
    "nodes": {
        "users":            ["user"],
        "hosts":            ["destination_host", "source_host"],
        "ips":              ["destination_ip"],
        "domains":          ["destination_domain"],
        "urls":             ["url"],
        "file_hashes":      ["file_hash"],
        "processes":        ["process_name"],
        "parent_processes": ["parent_process"],
        "cves":             ["cve_id"],
    },

    "edges": [
        # Core & Network
        ("user", "destination_host"),
        ("user", "source_host"),                   # THÊM TỪ CANONICAL
        ("file_hash", "destination_host"),
        ("destination_host", "destination_ip"),
        ("destination_host", "destination_domain"),
        ("destination_host", "url"),
        
        # Mối quan hệ bổ sung từ Network Canonical (do EDR có chứa source_host)
        ("source_host", "destination_host"),       # THÊM TỪ CANONICAL
        ("source_host", "destination_ip"),         # THÊM TỪ CANONICAL
        ("source_host", "destination_domain"),     # THÊM TỪ CANONICAL
        ("source_host", "url"),                    # THÊM TỪ CANONICAL

        # Process
        ("parent_process", "process_name"),
        ("process_name", "destination_host"),
        ("process_name", "user"),
        ("process_name", "file_hash"),
        ("process_name", "destination_ip"),
        ("process_name", "destination_domain"),
        ("process_name", "url"),                   # GIỮ NGUYÊN (Không có trong Canonical)

        # Vulnerability
        ("cve_id", "destination_host"),
        ("cve_id", "process_name"),
    ]
}


# ── CLOUD ─────────────────────────────────────────────────────────────────────
CLOUD_SCHEMA = {
    "nodes": {
        "users":            ["user"],
        "hosts":            ["source_host"],
        "ips":              ["destination_ip"],
        "domains":          ["destination_domain"],
        "urls":             ["url"],
        "cloud_resources":  ["resource_id"],
        "cves":             ["cve_id"],
    },

    "edges": [
        # Network
        ("source_host", "destination_ip"),
        ("source_host", "destination_domain"),
        ("destination_domain", "destination_ip"),
        ("source_host", "url"),

        # Cloud
        ("user", "resource_id"),
        ("user", "source_host"),                   # THÊM TỪ CANONICAL
        ("resource_id", "destination_ip"),
        ("resource_id", "source_host"),

        # Vulnerability
        ("cve_id", "resource_id"),
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
        ("cve_id",              "resource_id"),
        
        ("source_ip",           "file_hash"), # IP tải/chứa file hash
        ("destination_domain",  "file_hash"), # Domain phân phối file hash
        ("process_name",        "file_hash"),
        ("file_hash",           "destination_host"),
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
    r"(?:com|net|org|edu|gov|mil|int|io|co|biz|info|vn|xyz|me|online|live|tech|ru)\b",
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