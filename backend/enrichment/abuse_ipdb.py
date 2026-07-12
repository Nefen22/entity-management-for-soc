import os
import httpx
import json

ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY", "")

url = "https://api.abuseipdb.com/api/v2/check"

headers = {
    "Key": ABUSEIPDB_API_KEY,
    "Accept": "application/json"
}

async def ips_enrichment_abuseipdb(value:str):
    params = {
        "ipAddress": {value},
        "maxAgeInDays": 90
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=headers, params=params)
    except Exception as e:
        raise e
    data = response.json()["data"]
    return {
        "abuse_score": data.get("abuseConfidenceScore", 0),
        "country_code": data.get("countryCode", "Unknown"),
        "isp": data.get("isp", "Unknown"),
        "usage_type": data.get("usageType", "Unknown"),
        "domain": data.get("domain", "Unknown"),
        "last_reported": data.get("lastReportedAt"),
        "report_count": data.get("totalReports", 0)
    }