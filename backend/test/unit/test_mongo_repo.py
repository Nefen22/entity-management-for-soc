import pytest
from unittest.mock import MagicMock, patch
from pymongo.errors import DuplicateKeyError, PyMongoError

from repositories.mongo_repo import (
    AuditRepository,
    EventsRepository,
    UserRepository,
)


def test_get_user_returns_document():
    collection = MagicMock()
    collection.find_one.return_value = {"username": "admin", "role": "admin"}

    with patch("repositories.mongo_repo.MongoDB.collection", return_value=collection):
        result = UserRepository.get_user("admin")

    collection.find_one.assert_called_once_with({"username": "admin"})
    assert result == {"username": "admin", "role": "admin"}


def test_get_user_raises_when_collection_unavailable():
    with patch("repositories.mongo_repo.MongoDB.collection", side_effect=RuntimeError("DB not initialized")):
        with pytest.raises(RuntimeError, match="DB not initialized"):
            UserRepository.get_user("admin")


def test_get_permission_returns_document():
    collection = MagicMock()
    collection.find_one.return_value = {"name": "admin", "permissions": ["graph:view"]}

    with patch("repositories.mongo_repo.MongoDB.collection", return_value=collection):
        result = UserRepository.get_permission("admin")

    collection.find_one.assert_called_once_with({"name": "admin"})
    assert result["permissions"] == ["graph:view"]


@pytest.mark.asyncio
async def test_get_event_returns_document_without_id():
    collection = MagicMock()
    collection.find_one.return_value = {"tenant": "phishing", "event_id": "01", "raw_event": {"foo": "bar"}}

    with patch("repositories.mongo_repo.MongoDB.collection", return_value=collection):
        result = await EventsRepository.get_event("phishing", "01")

    collection.find_one.assert_called_once_with(
        {"tenant": "phishing", "event_id": "01"},
        {"_id": 0},
    )
    assert result["raw_event"] == {"foo": "bar"}


@pytest.mark.asyncio
async def test_post_event_upserts_document_with_defaults():
    collection = MagicMock()
    collection.update_one.return_value = {"ok": 1}
    event = {"event_id": "01", "timestamp": "2024-01-01T00:00:00Z", "payload": {"a": 1}}

    with patch("repositories.mongo_repo.MongoDB.collection", return_value=collection):
        result = await EventsRepository.post_event("phishing", event)

    collection.update_one.assert_called_once_with(
        {"tenant": "phishing", "event_id": "01"},
        {"$setOnInsert": {
            "tenant": "phishing",
            "event_id": "01",
            "timestamp": "2024-01-01T00:00:00Z",
            "source_type": "unknown",
            "raw_event": event,
        }},
        upsert=True,
    )
    assert result == {"ok": 1}


@pytest.mark.asyncio
async def test_post_event_raises_on_write_error():
    collection = MagicMock()
    collection.update_one.side_effect = PyMongoError("write failure")
    event = {"event_id": "01", "timestamp": "2024-01-01T00:00:00Z"}

    with patch("repositories.mongo_repo.MongoDB.collection", return_value=collection):
        with pytest.raises(PyMongoError, match="write failure"):
            await EventsRepository.post_event("phishing", event)


@pytest.mark.asyncio
async def test_post_event_raises_for_missing_timestamp():
    collection = MagicMock()
    event = {"event_id": "01"}

    with patch("repositories.mongo_repo.MongoDB.collection", return_value=collection):
        with pytest.raises(KeyError):
            await EventsRepository.post_event("phishing", event)


def test_post_log_inserts_document():
    collection = MagicMock()
    log = {"action": "CREATE", "entity_type": "User", "entity_id": "admin"}

    with patch("repositories.mongo_repo.MongoDB.collection", return_value=collection):
        AuditRepository.post_log("phishing", log)

    collection.insert_one.assert_called_once_with(
        {"tenant": "phishing", **log}
    )


def test_post_log_raises_duplicate_key_error():
    collection = MagicMock()
    collection.insert_one.side_effect = DuplicateKeyError("duplicate key")

    with patch("repositories.mongo_repo.MongoDB.collection", return_value=collection):
        with pytest.raises(DuplicateKeyError):
            AuditRepository.post_log("phishing", {"action": "CREATE"})


def test_get_logs_returns_paginated_metadata_and_data_with_filters():
    collection = MagicMock()
    cursor = MagicMock()
    cursor.sort.return_value = cursor
    cursor.skip.return_value = cursor
    cursor.limit.return_value = [
        {"timestamp": "2024-01-02T00:00:00Z", "action": "CREATE"},
        {"timestamp": "2024-01-01T00:00:00Z", "action": "UPDATE"},
    ]
    collection.count_documents.return_value = 2
    collection.find.return_value = cursor

    with patch("repositories.mongo_repo.MongoDB.collection", return_value=collection):
        result = AuditRepository.get_logs(
            tenant="phishing",
            page=1,
            limit=1,
            start_time="2024-01-01T00:00:00Z",
            end_time="2024-01-02T00:00:00Z",
            action="CREATE",
            entity_id="admin",
            entity_type="User",
        )

    collection.count_documents.assert_called_once()
    assert collection.find.call_args[0][0] == {
        "tenant": "phishing",
        "timestamp": {"$gte": "2024-01-01T00:00:00Z", "$lte": "2024-01-02T00:00:00Z"},
        "action": "CREATE",
        "entity_id": "admin",
        "entity_type": "User",
    }
    assert result["metadata"] == {
        "total_records": 2,
        "current_page": 1,
        "limit": 1,
        "total_pages": 2,
        "has_next": True,
        "has_previous": False,
    }
    assert result["data"] == [
        {"timestamp": "2024-01-02T00:00:00Z", "action": "CREATE"},
        {"timestamp": "2024-01-01T00:00:00Z", "action": "UPDATE"},
    ]


def test_get_logs_returns_empty_metadata_when_no_records():
    collection = MagicMock()
    cursor = MagicMock()
    cursor.sort.return_value = cursor
    cursor.skip.return_value = cursor
    cursor.limit.return_value = []
    collection.count_documents.return_value = 0
    collection.find.return_value = cursor

    with patch("repositories.mongo_repo.MongoDB.collection", return_value=collection):
        result = AuditRepository.get_logs(tenant="phishing")

    assert result["metadata"]["total_records"] == 0
    assert result["metadata"]["total_pages"] == 1
    assert result["metadata"]["has_next"] is False
    assert result["metadata"]["has_previous"] is False
    assert result["data"] == []
