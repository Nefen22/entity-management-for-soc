"""
Unit tests for enrichment layer.
- enrichment_ip_func: GeoIP lookup, cache, invalid IP
- VirusTotal mock lookup
"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock

# ══════════════════════════════════════════════════════════════════════════════
#  GeoIP enrichment
# ══════════════════════════════════════════════════════════════════════════════

class TestGeoIPEnrichment:

    def _make_mock_city(self, iso_code="US", country_name="United States",
                        city_name="Chicago", region="Illinois",
                        continent="NA", lat=41.85, lon=-87.65,
                        tz="America/Chicago", network="8.8.8.0/24"):
        m = MagicMock()
        m.country.iso_code = iso_code
        m.country.name = country_name
        m.city.name = city_name
        m.subdivisions.most_specific.name = region
        m.continent.code = continent
        m.location.latitude = lat
        m.location.longitude = lon
        m.location.time_zone = tz
        m.traits.network = network
        return m

    def _make_mock_asn(self, asn=15169, org="Google LLC"):
        m = MagicMock()
        m.autonomous_system_number = asn
        m.autonomous_system_organization = org
        return m

    @pytest.mark.asyncio
    async def test_valid_ip_returns_geo_data(self):
        mock_city = self._make_mock_city()
        mock_asn  = self._make_mock_asn()

        with patch("geoip2.database.Reader") as mock_reader_cls:
            mock_reader = MagicMock()
            mock_reader.city.return_value = mock_city
            mock_reader.asn.return_value  = mock_asn
            mock_reader_cls.return_value  = mock_reader

            # Import sau khi patch để tránh module-level reader init
            import importlib, sys
            sys.modules.pop("enrichment.geoip", None)
            with patch("geoip2.database.Reader", mock_reader_cls):
                from enrichment.geoip import enrichment_ip_func, geoip2_cache
                geoip2_cache.clear()

                result = await enrichment_ip_func("8.8.8.8")

        assert result["country"] == "US"
        assert result["country_name"] == "United States"
        assert result["asn"] == 15169
        assert result["organization"] == "Google LLC"
        assert result["timezone"] == "America/Chicago"

    @pytest.mark.asyncio
    async def test_invalid_ip_raises_value_error(self):
        with patch("geoip2.database.Reader"):
            import sys
            sys.modules.pop("enrichment.geoip", None)
            from enrichment.geoip import enrichment_ip_func
            with pytest.raises(ValueError, match="Invalid IP"):
                await enrichment_ip_func("not-an-ip")

    @pytest.mark.asyncio
    async def test_result_is_cached(self):
        mock_city = self._make_mock_city()
        mock_asn  = self._make_mock_asn()

        with patch("geoip2.database.Reader") as mock_reader_cls:
            mock_reader = MagicMock()
            mock_reader.city.return_value = mock_city
            mock_reader.asn.return_value  = mock_asn
            mock_reader_cls.return_value  = mock_reader

            import sys
            sys.modules.pop("enrichment.geoip", None)
            with patch("geoip2.database.Reader", mock_reader_cls):
                from enrichment.geoip import enrichment_ip_func, geoip2_cache
                geoip2_cache.clear()

                await enrichment_ip_func("1.1.1.1")
                await enrichment_ip_func("1.1.1.1")  # lần 2 từ cache

        # city.call_count phải là 1 (lần 2 từ cache, không gọi lại)
        assert mock_reader.city.call_count == 1

    @pytest.mark.asyncio
    async def test_private_ip_returns_note(self):
        import geoip2.errors

        with patch("geoip2.database.Reader") as mock_reader_cls:
            mock_reader = MagicMock()
            mock_reader.city.side_effect = geoip2.errors.AddressNotFoundError("not found")
            mock_reader_cls.return_value = mock_reader

            import sys
            sys.modules.pop("enrichment.geoip", None)
            with patch("geoip2.database.Reader", mock_reader_cls):
                from enrichment.geoip import enrichment_ip_func, geoip2_cache
                geoip2_cache.clear()
                result = await enrichment_ip_func("192.168.1.1")

        assert "note" in result
        assert result.get("country") is None

    @pytest.mark.asyncio
    async def test_cache_check_returns_dict(self):
        with patch("geoip2.database.Reader"):
            import sys
            sys.modules.pop("enrichment.geoip", None)
            from enrichment.geoip import ip_cache_check
            result = await ip_cache_check()
            assert isinstance(result, dict)


# ══════════════════════════════════════════════════════════════════════════════
#  VirusTotal mock enrichment
# ══════════════════════════════════════════════════════════════════════════════

class TestVirusTotalMock:
    """
    virustotal_mock.py dùng dataset offline từ file JSON.
    Ta mock file JSON để không cần file thật.
    """

    MOCK_VT_DATA = {
        "44d88612fea8a8f36de82e1278abb02f": {
            "malicious": True,
            "family": "Eicar-Test-File",
            "detections": 52
        }
    }

    async def test_known_hash_returns_malicious_info(self):
        import json
        with patch("builtins.open", unittest_mock_open(json.dumps(self.MOCK_VT_DATA))):
            with patch("json.load", return_value=self.MOCK_VT_DATA):
                import sys
                sys.modules.pop("enrichment.virustotal_mock", None)
                from enrichment.virustotal_mock import enrichment_file_hash_func
                result = await enrichment_file_hash_func("44d88612fea8a8f36de82e1278abb02f")

        assert result.get("malicious") is True
        assert "family" in result

    async def test_unknown_hash_returns_not_found(self):
        with patch("json.load", return_value=self.MOCK_VT_DATA):
            import sys
            sys.modules.pop("enrichment.virustotal_mock", None)
            from enrichment.virustotal_mock import enrichment_file_hash_func
            result = await enrichment_file_hash_func("0" * 32)

        # Không tìm thấy → trả về dict rỗng hoặc có key "not_found"
        assert isinstance(result, dict)
        assert result.get("malicious") is not True


def unittest_mock_open(read_data=""):
    """Helper: mock open() trả về string data."""
    from unittest.mock import mock_open
    return mock_open(read_data=read_data)