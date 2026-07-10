import httpx
import pytest
from fastapi import HTTPException
from unittest.mock import patch

import enrichment.virustotal as virustotal_module
from enrichment.virustotal import filehash_enrichment_vt


def make_response(status_code, *, json_body=None, text=None):
    request = httpx.Request("GET", "https://www.virustotal.com/api/v3/files/test")
    return httpx.Response(status_code, request=request, json=json_body, text=text)


class FakeAsyncClient:
    def __init__(self, response=None, exc=None):
        self._response = response
        self._exc = exc

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url, headers=None):
        if self._exc is not None:
            raise self._exc
        return self._response


@pytest.mark.asyncio
async def test_filehash_enrichment_vt_successful_lookup():
    response = make_response(
        200,
        json_body={
            "data": {
                "attributes": {
                    "md5": "md5hash",
                    "sha1": "sha1hash",
                    "sha256": "sha256hash",
                    "meaningful_name": "sample.exe",
                    "type_description": "Win32 EXE",
                    "size": 12345,
                    "last_analysis_stats": {
                        "malicious": 2,
                        "harmless": 5,
                        "undetected": 10,
                        "suspicious": 1,
                        "timeout": 1,
                    },
                    "popular_threat_classification": {
                        "suggested_threat_label": "Trojan",
                        "popular_threat_name": [{"value": "Emotet"}],
                    },
                    "reputation": 100,
                    "last_analysis_date": "2024-01-01T00:00:00Z",
                    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6"],
                }
            }
        },
    )

    with patch.object(virustotal_module, "API_KEY", "test-key"), patch(
        "enrichment.virustotal.httpx.AsyncClient", return_value=FakeAsyncClient(response)
    ):
        result = await filehash_enrichment_vt("sha256hash")

    assert result["md5"] == "md5hash"
    assert result["malicious"] == 2
    assert result["suspicious"] == 1
    assert result["harmless"] == 5
    assert result["detection_ratio"] == "2/19"
    assert result["threat_label"] == "Trojan"
    assert result["threat_family"] == "Emotet"
    assert result["tags"] == ["tag1", "tag2", "tag3", "tag4", "tag5"]
    assert result["vt_link"] == "https://www.virustotal.com/gui/file/sha256hash"


@pytest.mark.asyncio
async def test_filehash_enrichment_vt_not_found():
    response = make_response(404)

    with patch.object(virustotal_module, "API_KEY", "test-key"), patch(
        "enrichment.virustotal.httpx.AsyncClient", return_value=FakeAsyncClient(response)
    ):
        with pytest.raises(HTTPException) as exc_info:
            await filehash_enrichment_vt("missinghash")

    assert exc_info.value.status_code == 404
    assert "missinghash" in exc_info.value.detail


@pytest.mark.asyncio
async def test_filehash_enrichment_vt_rate_limit():
    response = make_response(429)

    with patch.object(virustotal_module, "API_KEY", "test-key"), patch(
        "enrichment.virustotal.httpx.AsyncClient", return_value=FakeAsyncClient(response)
    ):
        with pytest.raises(httpx.HTTPStatusError):
            await filehash_enrichment_vt("rate-limited")


@pytest.mark.asyncio
async def test_filehash_enrichment_vt_timeout_error():
    with patch.object(virustotal_module, "API_KEY", "test-key"), patch(
        "enrichment.virustotal.httpx.AsyncClient", return_value=FakeAsyncClient(exc=httpx.TimeoutException("timed out"))
    ):
        with pytest.raises(httpx.TimeoutException):
            await filehash_enrichment_vt("timeout-hash")


@pytest.mark.asyncio
async def test_filehash_enrichment_vt_malformed_json():
    response = make_response(200, text="not-json")

    with patch.object(virustotal_module, "API_KEY", "test-key"), patch(
        "enrichment.virustotal.httpx.AsyncClient", return_value=FakeAsyncClient(response)
    ):
        with pytest.raises(ValueError):
            await filehash_enrichment_vt("bad-json")


@pytest.mark.asyncio
async def test_filehash_enrichment_vt_auth_failure():
    response = make_response(401)

    with patch.object(virustotal_module, "API_KEY", ""), patch(
        "enrichment.virustotal.httpx.AsyncClient", return_value=FakeAsyncClient(response)
    ):
        with pytest.raises(httpx.HTTPStatusError):
            await filehash_enrichment_vt("auth-fail")
