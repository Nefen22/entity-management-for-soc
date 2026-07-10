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
    
class EventsRepository:
    @staticmethod
    async def get_event(tenant: str, event_id: str):
        collection = MongoDB.collection("events")
        return collection.find_one(
            {"tenant":tenant,
            "event_id": event_id},
            {"_id": 0}
        )
        
    @staticmethod
    async def post_event(tenant: str, event: dict):
        collection = MongoDB.collection("events")

        document = {
            "tenant": tenant,
            "event_id": event["event_id"],
            "timestamp": event["timestamp"],
            "source_type": event.get("source_type", "unknown"),
            "raw_event": event
        }

        return collection.update_one(
            {
                "tenant": tenant,
                "event_id": event["event_id"]
            },
            {
                "$setOnInsert": document
            },
            upsert=True
        )