from pymongo import MongoClient
import os

class MongoDB:
    _client = None
    _db = None

    @classmethod
    def connect(cls):
        cls._client = MongoClient(os.getenv("MONGODB_URI"))
        cls._db = cls._client[os.getenv("MONGODB_DATABASE")]
        cls.create_indexes()

    @classmethod
    def create_indexes(cls):
        users = cls.collection("users")
        roles = cls.collection("roles")
        events = cls.collection("events")
        users.create_index("username", unique=True)
        roles.create_index("name", unique=True)
        events.create_index([("tenant", 1), ("event_id", 1)], unique=True)
        events.create_index([("tenant", 1), ("timestamp", 1)])

    @classmethod
    def collection(cls, name: str):
        return cls._db[name]