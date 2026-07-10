import os
import pytest

from database.constraints import TENANT_DATABASE
from database.seed import MongoDB

@pytest.fixture(autouse=True)
def ensure_tenant_labels():
    for tenant in ("tenant-a", "tenant-b"):
        TENANT_DATABASE.setdefault(tenant, f"Tenant_{tenant}")
    yield


@pytest.fixture(autouse=True)
def audit_collection():
    MongoDB.connect()
    collection = MongoDB.collection("audit_logs")
    collection.delete_many({})
    yield collection
    collection.delete_many({})


def _seed_audit_logs(collection):
    logs = [
        {
            "tenant": "tenant-a",
            "timestamp": "2024-01-01T00:00:00Z",
            "action": "CREATE",
            "entity_type": "User",
            "entity_id": "entity-a-1",
            "change": {"field": "name"},
        },
        {
            "tenant": "tenant-a",
            "timestamp": "2024-01-01T00:01:00Z",
            "action": "UPDATE",
            "entity_type": "Host",
            "entity_id": "entity-a-2",
            "change": {"field": "status"},
        },
        {
            "tenant": "tenant-a",
            "timestamp": "2024-01-01T00:02:00Z",
            "action": "CREATE",
            "entity_type": "Domain",
            "entity_id": "entity-a-3",
            "change": {"field": "value"},
        },
        {
            "tenant": "tenant-a",
            "timestamp": "2024-01-01T00:03:00Z",
            "action": "UPDATE",
            "entity_type": "User",
            "entity_id": "entity-a-4",
            "change": {"field": "role"},
        },
        {
            "tenant": "tenant-a",
            "timestamp": "2024-01-01T00:04:00Z",
            "action": "CREATE",
            "entity_type": "Host",
            "entity_id": "entity-a-5",
            "change": {"field": "owner"},
        },
        {
            "tenant": "tenant-b",
            "timestamp": "2024-01-01T00:05:00Z",
            "action": "UPDATE",
            "entity_type": "User",
            "entity_id": "entity-b-1",
            "change": {"field": "role"},
        },
        {
            "tenant": "tenant-b",
            "timestamp": "2024-01-01T00:06:00Z",
            "action": "CREATE",
            "entity_type": "Domain",
            "entity_id": "entity-b-2",
            "change": {"field": "name"},
        },
    ]
    collection.insert_many(logs)
    return logs


def _audit_logs_url(tenant: str):
    return f"/api/tenants/{tenant}/logs/audit-logs"


def test_get_logs_pagination_page_one_and_page_two(api, audit_collection):
    _seed_audit_logs(audit_collection)

    page_one = api.get(_audit_logs_url("tenant-a"), params={"page": 1, "limit": 2})
    assert page_one.status_code == 200

    page_one_payload = page_one.json()["data"]
    assert page_one_payload["metadata"]["total_records"] == 5
    assert page_one_payload["metadata"]["total_pages"] == 3
    assert page_one_payload["metadata"]["has_next"] is True
    assert page_one_payload["metadata"]["has_previous"] is False
    assert len(page_one_payload["data"]) == 2
    assert page_one_payload["data"][0]["entity_id"] == "entity-a-5"

    page_two = api.get(_audit_logs_url("tenant-a"), params={"page": 2, "limit": 2})
    assert page_two.status_code == 200

    page_two_payload = page_two.json()["data"]
    assert page_two_payload["metadata"]["total_records"] == 5
    assert page_two_payload["metadata"]["total_pages"] == 3
    assert page_two_payload["metadata"]["has_next"] is True
    assert page_two_payload["metadata"]["has_previous"] is True
    assert len(page_two_payload["data"]) == 2
    assert page_two_payload["data"][0]["entity_id"] == "entity-a-3"


def test_get_logs_filter_by_entity_id(api, audit_collection):
    _seed_audit_logs(audit_collection)

    response = api.get(_audit_logs_url("tenant-a"), params={"entity_id": "entity-a-2"})
    assert response.status_code == 200

    payload = response.json()["data"]
    assert payload["metadata"]["total_records"] == 1
    assert payload["data"][0]["entity_id"] == "entity-a-2"
    assert payload["data"][0]["action"] == "UPDATE"


def test_get_logs_filter_by_entity_type(api, audit_collection):
    _seed_audit_logs(audit_collection)

    response = api.get(_audit_logs_url("tenant-a"), params={"entity_type": "User"})
    assert response.status_code == 200

    payload = response.json()["data"]
    assert payload["metadata"]["total_records"] == 2
    assert {item["entity_type"] for item in payload["data"]} == {"User"}


def test_get_logs_filter_by_action(api, audit_collection):
    _seed_audit_logs(audit_collection)

    response = api.get(_audit_logs_url("tenant-a"), params={"action": "CREATE"})
    assert response.status_code == 200

    payload = response.json()["data"]
    assert payload["metadata"]["total_records"] == 3
    assert {item["action"] for item in payload["data"]} == {"CREATE"}


def test_get_logs_filter_by_time_range_including_boundaries(api, audit_collection):
    _seed_audit_logs(audit_collection)

    response = api.get(
        _audit_logs_url("tenant-a"),
        params={
            "start_time": "2024-01-01T00:00:00Z",
            "end_time": "2024-01-01T00:02:00Z",
        },
    )
    assert response.status_code == 200

    payload = response.json()["data"]
    assert payload["metadata"]["total_records"] == 3
    timestamps = [item["timestamp"] for item in payload["data"]]
    assert timestamps == [
        "2024-01-01T00:02:00Z",
        "2024-01-01T00:01:00Z",
        "2024-01-01T00:00:00Z",
    ]


def test_get_logs_filter_combined_filters(api, audit_collection):
    _seed_audit_logs(audit_collection)

    response = api.get(
        _audit_logs_url("tenant-a"),
        params={
            "action": "CREATE",
            "entity_type": "Host",
            "entity_id": "entity-a-5",
            "start_time": "2024-01-01T00:03:00Z",
            "end_time": "2024-01-01T00:05:00Z",
        },
    )
    assert response.status_code == 200

    payload = response.json()["data"]
    assert payload["metadata"]["total_records"] == 1
    assert payload["data"][0]["entity_id"] == "entity-a-5"
    assert payload["data"][0]["entity_type"] == "Host"
    assert payload["data"][0]["action"] == "CREATE"


def test_get_logs_tenant_isolation(api, audit_collection):
    _seed_audit_logs(audit_collection)

    response = api.get(_audit_logs_url("tenant-a"))
    assert response.status_code == 200

    payload = response.json()["data"]
    assert payload["metadata"]["total_records"] == 5
    assert all(item["tenant"] == "tenant-a" for item in payload["data"])


def test_get_logs_limit_boundaries_and_invalid_page(api, audit_collection):
    _seed_audit_logs(audit_collection)

    limit_one = api.get(_audit_logs_url("tenant-a"), params={"limit": 1})
    assert limit_one.status_code == 200
    assert len(limit_one.json()["data"]["data"]) == 1

    limit_max = api.get(_audit_logs_url("tenant-a"), params={"limit": 500})
    assert limit_max.status_code == 200
    assert len(limit_max.json()["data"]["data"]) == 5

    limit_too_large = api.get(_audit_logs_url("tenant-a"), params={"limit": 501})
    assert limit_too_large.status_code == 422

    page_zero = api.get(_audit_logs_url("tenant-a"), params={"page": 0, "limit": 1})
    assert page_zero.status_code == 422

    negative_page = api.get(_audit_logs_url("tenant-a"), params={"page": -1, "limit": 1})
    assert negative_page.status_code == 422
