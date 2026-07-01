import asyncio
import geoip2.database
import ipaddress
import json
from cachetools import TTLCache
from pathlib import Path

geoip2_cache = TTLCache(maxsize=1000, ttl=3600)
CURRENT_DIR = Path(__file__).resolve().parent
JSON_PATH = CURRENT_DIR / "data"

reader_city = geoip2.database.Reader(f"{JSON_PATH}/GeoLite2-City.mmdb")
reader_asn = geoip2.database.Reader(f"{JSON_PATH}/GeoLite2-ASN.mmdb")

async def enrichment_ip_func(value: str):
    try:
        ipaddress.ip_address(value)
    except ValueError:
        raise ValueError(f"Invalid IP: {value}")
    sub_dict = {}
    if value in geoip2_cache:
        sub_dict = geoip2_cache[value]
    else:
        try:
            response_city = reader_city.city(value)
            response_asn = reader_asn.asn(value)
            
            sub_dict = {
                "country": response_city.country.iso_code,
                "country_name": response_city.country.name,

                "city": response_city.city.name,

                "region": response_city.subdivisions.most_specific.name,

                "continent": response_city.continent.code,

                "latitude": response_city.location.latitude,
                "longitude": response_city.location.longitude,
                "timezone": response_city.location.time_zone,

                "network": str(response_city.traits.network),

                "asn": response_asn.autonomous_system_number,
                "organization": response_asn.autonomous_system_organization
            }
        except geoip2.errors.AddressNotFoundError:
            sub_dict = {"country": None, "note": "Private or unregistered IP"}

        geoip2_cache[value] = sub_dict
    return sub_dict

async def ip_cache_check():
    return dict(geoip2_cache)