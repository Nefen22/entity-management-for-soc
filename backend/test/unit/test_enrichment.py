import sys
import pytest
import fakeredis.aioredis
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_valid_ip_returns_geo_data(geoip_reader):
    sys.modules.pop("enrichment.enrich", None)
    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    await fake_redis.flushdb()
    with patch("enrichment.enrich.redis_client" ,fake_redis):
        from enrichment.enrich import ips_enrich

        await fake_redis.flushdb()

        result = await ips_enrich("8.8.8.8")

        assert result["country"] == "US"
        assert result["asn"] == 15169

@pytest.mark.asyncio
async def test_cache(geoip_reader):
    sys.modules.pop("enrichment.enrich", None)
    
    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    await fake_redis.flushdb()
    
    mock_geoip_func = AsyncMock(return_value={"country": "US", "city": "Local"})
    
    with patch("enrichment.enrich.redis_client", fake_redis), \
         patch("enrichment.enrich.enrichment_ip_func", mock_geoip_func):
         
        from enrichment.enrich import ips_enrich
        
        await fake_redis.flushdb()
        
        await ips_enrich("1.1.1.1")
        
        await ips_enrich("1.1.1.1")
        
        assert mock_geoip_func.call_count == 1


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