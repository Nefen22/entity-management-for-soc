from backend.database.mongodb import MongoDB

class UserRepository:
    @staticmethod
    def get_user(username: str):
        collection = MongoDB.collection("users")
        return collection.find_one(
            {"username": username}
        )
    
    @staticmethod
    def get_permission(role: str):
        collection = MongoDB.collection("roles")
        return collection.find_one(
            {"name": role}
        )