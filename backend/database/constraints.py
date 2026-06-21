MAPPING_ENTITIES_TYPE={
    "ips": "IP",
    "users": "User",
    "hosts": "Host",
    "domains": "Domain",
    "file_hashes": "FileHash",
    "IP": "IP",
    "User": "User",
    "Host": "Host",
    "Domain": "Domain",
    "FileHash": "FileHash"
}

REVERSED_TYPE= {v:k for k,v in MAPPING_ENTITIES_TYPE.items()}

MAPPING_ENTITIES_KEY={
    "ips": "value",
    "users": "username",
    "hosts": "hostname",
    "domains": "name",
    "file_hashes": "hash_value"
}

MAPPING_ENTITY= {
    "ips": "ip",
    "users": "user",
    "hosts": "host",
    "domains": "domain",
    "file_hashes": "hash"
}

MAPPING_REALITIONSHIPS={
    ("User", "Host"): "LOGGED_IN",
    ("Host", "IP"): "CONNECTED_TO",
    ("Host", "Domain"): "CONNECTED_TO",
    ("FileHash", "Host"): "EXCUTED_ON"
}
