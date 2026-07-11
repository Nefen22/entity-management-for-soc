from fastapi import HTTPException
from repositories.mongo_repo import EventsRepository, AuditRepository

async def write_audit_log(
    tenant: str,
    action: str,
    entity_type: str,
    entity_id: str,
    time: str,
    event_id:str | None = None,
    change: dict | None = None,
):
    AuditRepository.post_log(
        tenant=tenant,
        log={
            "timestamp": time,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "event_id": event_id,
            "change": change or {}
        }
    )


async def get_logs(
    tenant: str,
    page: int,
    limit: int,
    start_time: str | None = None,
    end_time: str | None = None,
    action: str | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
):
    return AuditRepository.get_logs(
        tenant=tenant,
        page=page,
        limit=limit,
        start_time=start_time,
        end_time=end_time,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
    )

async def get_event(tenant: str, event_id: str):
    result = await EventsRepository.get_event(
        tenant=tenant,
        event_id=event_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    return result