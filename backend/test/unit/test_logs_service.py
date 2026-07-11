import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from services.logs import get_event, get_logs, write_audit_log


@pytest.mark.asyncio
async def test_write_audit_log_posts_expected_payload():
    with patch("services.logs.AuditRepository.post_log") as post_log:
        await write_audit_log(
            tenant="phishing",
            action="CREATE",
            entity_type="User",
            entity_id="admin",
            time="2024-01-01T00:00:00Z",
            change={"before": {}, "after": {"value": "admin"}},
        )

    post_log.assert_called_once_with(
                tenant="phishing",
                log={
                    "timestamp": "2024-01-01T00:00:00Z",
                    "action": "CREATE",
                    "entity_type": "User",
                    "entity_id": "admin",
                    "event_id": None,  # Thêm dòng này để khớp với hàm mới cập nhật
                    "change": {"before": {}, "after": {"value": "admin"}},
                },
            )


@pytest.mark.asyncio
async def test_write_audit_log_uses_empty_change_when_missing():
    with patch("services.logs.AuditRepository.post_log") as post_log:
        await write_audit_log(
            tenant="phishing",
            action="UPDATE",
            entity_type="IP",
            entity_id="192.168.1.1",
            time="2024-01-02T00:00:00Z",
        )

    post_log.assert_called_once_with(
        tenant="phishing",
        log={
            "timestamp": "2024-01-02T00:00:00Z",
            "action": "UPDATE",
            "entity_type": "IP",
            "event_id": None,
            "entity_id": "192.168.1.1",
            "change": {},
        },
    )


@pytest.mark.asyncio
async def test_get_logs_happy_path_with_filters():
    with patch("services.logs.AuditRepository.get_logs") as get_logs_repo:
        get_logs_repo.return_value = {
            "metadata": {"total_records": 1, "current_page": 1, "limit": 50, "total_pages": 1, "has_next": False, "has_previous": False},
            "data": [{"action": "CREATE", "entity_type": "User", "entity_id": "admin"}],
        }

        result = await get_logs(
            tenant="phishing",
            page=1,
            limit=50,
            start_time="2024-01-01T00:00:00Z",
            end_time="2024-01-02T00:00:00Z",
            action="CREATE",
            entity_type="User",
            entity_id="admin",
        )

    get_logs_repo.assert_called_once_with(
        tenant="phishing",
        page=1,
        limit=50,
        start_time="2024-01-01T00:00:00Z",
        end_time="2024-01-02T00:00:00Z",
        action="CREATE",
        entity_type="User",
        entity_id="admin",
    )
    assert result["data"][0]["entity_id"] == "admin"


@pytest.mark.asyncio
async def test_get_logs_without_filters_returns_all_logs():
    with patch("services.logs.AuditRepository.get_logs") as get_logs_repo:
        get_logs_repo.return_value = {
            "metadata": {"total_records": 2, "current_page": 1, "limit": 100, "total_pages": 1, "has_next": False, "has_previous": False},
            "data": [{"action": "CREATE"}, {"action": "UPDATE"}],
        }
        result = await get_logs(tenant="phishing", page=1, limit=100)

    get_logs_repo.assert_called_once_with(
        tenant="phishing",
        page=1,
        limit=100,
        start_time=None,
        end_time=None,
        action=None,
        entity_type=None,
        entity_id=None,
    )
    assert len(result["data"]) == 2


@pytest.mark.asyncio
async def test_get_logs_combined_filters_pass_through():
    with patch("services.logs.AuditRepository.get_logs") as get_logs_repo:
        get_logs_repo.return_value = {"metadata": {"total_records": 0, "current_page": 1, "limit": 100, "total_pages": 1, "has_next": False, "has_previous": False}, "data": []}
        await get_logs(
            tenant="phishing",
            page=2,
            limit=100,
            start_time="bad",
            end_time="still-bad",
            action="DELETE",
            entity_type="Domain",
            entity_id="example.com",
        )

    get_logs_repo.assert_called_once_with(
        tenant="phishing",
        page=2,
        limit=100,
        start_time="bad",
        end_time="still-bad",
        action="DELETE",
        entity_type="Domain",
        entity_id="example.com",
    )


@pytest.mark.asyncio
async def test_get_logs_empty_result_returns_empty_data():
    with patch("services.logs.AuditRepository.get_logs") as get_logs_repo:
        get_logs_repo.return_value = {"metadata": {"total_records": 0, "current_page": 3, "limit": 50, "total_pages": 1, "has_next": False, "has_previous": True}, "data": []}
        result = await get_logs(tenant="phishing", page=3, limit=50)

    assert result["data"] == []
    assert result["metadata"]["current_page"] == 3


@pytest.mark.asyncio
async def test_get_logs_pagination_boundary_limit_500():
    with patch("services.logs.AuditRepository.get_logs") as get_logs_repo:
        get_logs_repo.return_value = {"metadata": {"total_records": 1, "current_page": 1, "limit": 500, "total_pages": 1, "has_next": False, "has_previous": False}, "data": [{"action": "CREATE"}]}
        result = await get_logs(tenant="phishing", page=1, limit=500)

    assert result["metadata"]["limit"] == 500
    assert result["data"][0]["action"] == "CREATE"


@pytest.mark.asyncio
async def test_get_event_returns_event_when_present():
    with patch("services.logs.EventsRepository.get_event", new=AsyncMock(return_value={"event_id": "01", "raw_event": {"foo": "bar"}})) as get_event_repo:
        result = await get_event(tenant="phishing", event_id="01")

    get_event_repo.assert_awaited_once_with(tenant="phishing", event_id="01")
    assert result["event_id"] == "01"


@pytest.mark.asyncio
async def test_get_event_raises_404_when_missing():
    with patch("services.logs.EventsRepository.get_event", new=AsyncMock(return_value=None)) as get_event_repo:
        with pytest.raises(Exception) as exc_info:
            await get_event(tenant="phishing", event_id="missing")

    get_event_repo.assert_awaited_once_with(tenant="phishing", event_id="missing")
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Event not found"
