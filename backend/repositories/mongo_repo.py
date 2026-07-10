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

class AuditRepository:

    @staticmethod
    def post_log(tenant: str, log: dict):
        collection = MongoDB.collection("audit_logs")
        collection.insert_one({
            "tenant": tenant,
            **log
        })
        
    @staticmethod
    def get_logs(
        tenant: str,
        page: int = 1,
        limit: int = 100,
        start_time: str | None = None,
        end_time: str | None = None,
        action: str | None = None,
        entity_id: str | None = None,
        entity_type: str | None = None,
    ):
        collection = MongoDB.collection("audit_logs")

        query = {
            "tenant": tenant
        }

        if start_time or end_time:
            query["timestamp"] = {}
            if start_time:
                query["timestamp"]["$gte"] = start_time
            if end_time:
                query["timestamp"]["$lte"] = end_time

        if action:
            query["action"] = action

        if entity_id:
            query["entity_id"] = entity_id

        if entity_type:
            query["entity_type"] = entity_type

        total_records = collection.count_documents(query)

        logs = list(
            collection.find(query, {"_id": 0})
            .sort("timestamp", -1)
            .skip((page - 1) * limit)
            .limit(limit)
        )

        total_pages = max((total_records + limit - 1) // limit, 1)

        return {
            "metadata": {
                "total_records": total_records,
                "current_page": page,
                "limit": limit,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1,
            },
            "data": logs,
        }