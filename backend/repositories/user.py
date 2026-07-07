USERS = {
    "admin": {
        "password": "admin123",
        "role": "admin",
        "tenants": "all",
        "permissions": [
            "graph:view",
            "graph:ingest"
        ]
    },
    "user":{
        "password": "user123",
        "role": "user",
        "tenants": ["google","internal"],
        "permissions": [
            "graph:view"
        ]
    }
}

class UserRepository:
    @staticmethod
    def get_user(username: str):
        return USERS.get(username)