import sys
import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_valid_ip_returns_geo_data(geoip_reader):

    sys.modules.pop("enrichment.geoip", None)

    from enrichment.geoip import enrichment_ip_func, geoip2_cache

    geoip2_cache.clear()

    result = await enrichment_ip_func("8.8.8.8")

    assert result["country"] == "US"
    assert result["asn"] == 15169

@pytest.mark.asyncio
async def test_cache(geoip_reader):

    sys.modules.pop("enrichment.geoip", None)

    from enrichment.geoip import enrichment_ip_func, geoip2_cache

    geoip2_cache.clear()

    await enrichment_ip_func("1.1.1.1")
    await enrichment_ip_func("1.1.1.1")

    assert geoip_reader.city.call_count == 1

@pytest.mark.asyncio
async def test_known_hash(vt_dataset):

    with patch("json.load", return_value=vt_dataset):

        import sys
        sys.modules.pop("enrichment.virustotal_mock", None)

        from enrichment.virustotal_mock import enrichment_file_hash_func

        result = await enrichment_file_hash_func(
            "44d88612fea8a8f36de82e1278abb02f"
        )

    assert result["malicious"]