import pytest
from unittest.mock import patch
from fastapi import HTTPException

# Điều chỉnh lại import path nếu module thật không phải "api.tenants"
from api.tenants import validate_tenant


ADMIN_USER = {"username": "admin", "role": "admin", "tenants": ["all"]}
SCOPED_USER = {"username": "analyst", "role": "user", "tenants": ["acme", "globex"]}


def _patch_tenant_db(db: dict):
    # Điều chỉnh lại target patch nếu TENANT_DATABASE được import khác trong tenants.py
    return patch("api.tenants.TENANT_DATABASE", db)


# ---------------------- happy paths ----------------------

def test_validate_tenant_allows_admin_with_all_access_regardless_of_db():
    with _patch_tenant_db({}):  # tenant thậm chí không tồn tại trong DB
        result = validate_tenant("any-tenant", current_user=ADMIN_USER, permission=None)

    assert result == "any-tenant"


def test_validate_tenant_allows_scoped_user_for_owned_tenant():
    with _patch_tenant_db({"acme": {}, "globex": {}}):
        result = validate_tenant("acme", current_user=SCOPED_USER, permission=None)

    assert result == "acme"


# ---------------------- error paths ----------------------

def test_validate_tenant_raises_404_for_unknown_tenant():
    with _patch_tenant_db({"acme": {}}):
        with pytest.raises(HTTPException) as exc_info:
            validate_tenant("unknown-tenant", current_user=SCOPED_USER, permission=None)

    assert exc_info.value.status_code == 404


def test_validate_tenant_raises_403_for_known_tenant_user_not_assigned_to():
    other_scoped_user = {"username": "analyst", "role": "user", "tenants": ["acme"]}
    with _patch_tenant_db({"acme": {}, "globex": {}}):
        with pytest.raises(HTTPException) as exc_info:
            validate_tenant("globex", current_user=other_scoped_user, permission=None)

    assert exc_info.value.status_code == 403


# ---------------------- Bug 1: "all" bị match theo substring nếu tenants là string ----------------------

@pytest.mark.xfail(
    reason="BUG: `'all' in current_user['tenants']` làm substring match khi tenants là string "
           "(không phải list), nên user với tenants='small' vẫn bị coi là có full access. "
           "Xoá xfail sau khi fix (nên ép kiểu list hoặc so sánh chính xác, vd: "
           "current_user['tenants'] == 'all' or 'all' in (current_user['tenants'] if isinstance(...))).",
    strict=True,
)
def test_validate_tenant_should_not_grant_full_access_via_substring_match():
    leaky_user = {"username": "svc-smallcorp", "role": "user", "tenants": "small"}

    with _patch_tenant_db({}):  # tenant không tồn tại và user không có quyền thật với nó
        with pytest.raises(HTTPException) as exc_info:
            validate_tenant("nonexistent-tenant", current_user=leaky_user, permission=None)

    assert exc_info.value.status_code == 404


# ---------------------- Bug 2 (nghi vấn): thứ tự check để lộ tenant có tồn tại hay không ----------------------

def test_validate_tenant_current_behavior_leaks_tenant_existence_to_unauthorized_user():
    """
    Test này mô tả hành vi HIỆN TẠI (không assert đây là đúng hay sai).
    Một user không có quyền với tenant nào trong 2 tenant dưới đây vẫn phân biệt được
    tenant nào tồn tại (403) và tenant nào không tồn tại (404) — có thể dùng để dò
    (enumerate) tên tenant hợp lệ. Nếu team xác nhận đây là bug cần fix, đảo lại thứ tự
    check quyền trước rồi mới check tồn tại, và xoá test này để thay bằng test khẳng định
    hành vi mới (cả 2 case đều trả cùng 1 status, ví dụ 404).
    """
    unauthorized_user = {"username": "outsider", "role": "user", "tenants": ["other-corp"]}

    with _patch_tenant_db({"acme": {}}):
        with pytest.raises(HTTPException) as exc_info_exists:
            validate_tenant("acme", current_user=unauthorized_user, permission=None)
        with pytest.raises(HTTPException) as exc_info_missing:
            validate_tenant("ghost-corp", current_user=unauthorized_user, permission=None)

    assert exc_info_exists.value.status_code == 403   # tenant tồn tại -> lộ "acme là tenant thật"
    assert exc_info_missing.value.status_code == 404   # tenant không tồn tại -> lộ "ghost-corp không tồn tại"