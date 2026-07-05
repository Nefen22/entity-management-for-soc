USERS = {
    "admin": {
        "password": "admin123",
        "role": "admin",
        "tenants": "all"
    },
    "user":{
        "password": "user123",
        "role": "user",
        "tenants": ["google","internal"]
    }
}

class UserRepository:
    @staticmethod
    def get_user(username: str):
        return USERS.get(username)