from pymongo import MongoClient
import os

class MongoDB:
    _client = None
    _db = None

    @classmethod
    def connect(cls):
        if cls._client is None:
            cls._client = MongoClient(os.getenv("MONGODB_URI"))
            cls._db = cls._client[os.getenv("MONGODB_DATABASE")]

    @classmethod
    def collection(cls, name: str):
        return cls._db[name]