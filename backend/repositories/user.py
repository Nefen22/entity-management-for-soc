USERS = {
    "admin": {
        "password": "admin123",
        "role": "admin",
        "tenants": "all",
        "permissions": [
            "graph:view",
            "graph:ingest",
            "graph:enrichment"
        ]
    },
    "user":{
        "password": "user123",
        "role": "user",
        "tenants": ["google","internal"],
        "permissions": [
            "graph:view",
            "graph:enrichment"
        ]
    }
}

class UserRepository:
    @staticmethod
    def get_user(username: str):
        return USERS.get(username)