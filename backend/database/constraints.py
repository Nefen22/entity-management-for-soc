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

MAPPING_REALITIONSHIPS = {
    # existing
    ("User",    "Host"):    "LOGGED_IN",
    ("Host",    "IP"):      "CONNECTED_TO",
    ("Host",    "Domain"):  "CONNECTED_TO",
    ("FileHash","Host"):    "EXECUTED_ON",      # fixed typo EXCUTED → EXECUTED
    # URL
    ("Host",    "URL"):     "REQUESTED",
    ("Domain",  "URL"):     "HOSTS",
    ("IP",      "URL"):     "RESOLVES_TO",
    ("URL",     "Domain"):  "BELONGS_TO",
    # Process
    ("Process", "Host"):    "RUNS_ON",
    ("Process", "User"):    "EXECUTED_BY",
    ("Process", "FileHash"):"LOADED",
    ("Process", "IP"):      "CONNECTED_TO",
    ("Process", "URL"):     "REQUESTED",
    ("Process", "Domain"):  "RESOLVED",
    # CloudResource
    ("CloudResource", "IP"):   "ASSIGNED_TO",
    ("CloudResource", "User"): "OWNED_BY",
    ("CloudResource", "Host"): "RUNS_ON",
    ("User", "CloudResource"): "ACCESSED",
    # Email
    ("Email",   "User"):    "BELONGS_TO",
    ("Email",   "Domain"):  "HOSTED_BY",
    ("User",    "Email"):   "SENT",
    ("Email",   "URL"):     "CONTAINS",
    ("Email",   "FileHash"):"ATTACHED",
    # CVE
    ("CVE",     "Host"):        "AFFECTS",
    ("CVE",     "Process"):     "AFFECTS",
    ("CVE",     "CloudResource"):"AFFECTS",
    ("CVE",     "FileHash"):    "EXPLOITS",
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