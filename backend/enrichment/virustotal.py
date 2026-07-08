import httpx
import os
from fastapi import HTTPException,status

API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")

async def filehash_enrichment_vt(file_hash: str):
    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"

    headers = {
        "x-apikey": API_KEY,
        "accept": "application/json"
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, headers=headers)

    if response.status_code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Can not find {file_hash} in Virutotal")
    response.raise_for_status()
    data = response.json()["data"]["attributes"]
    stats = data.get("last_analysis_stats", {})
    threat = data.get("popular_threat_classification", {})

    total_detection = (
        stats.get("malicious", 0)
        + stats.get("harmless", 0)
        + stats.get("undetected", 0)
        + stats.get("suspicious", 0)
        + stats.get("timeout", 0)
    )

    result = {
            # Hash
            "md5": data.get("md5"),
            "sha1": data.get("sha1"),
            "sha256": data.get("sha256"),

            # File information
            "file_name": data.get("meaningful_name"),
            "file_type": data.get("type_description"),
            "size": data.get("size"),

            # Detection
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
            "harmless": stats.get("harmless", 0),
            "undetected": stats.get("undetected", 0),
            "detection_ratio": f"{stats.get('malicious',0)}/{total_detection}",

            # Threat intelligence
            "threat_label": threat.get("suggested_threat_label"),
            "threat_family": (
                threat.get("popular_threat_name", [{}])[0].get("value")
                if threat.get("popular_threat_name")
                else None
            ),

            # Community reputation
            "reputation": data.get("reputation"),

            # Metadata
            "last_analysis": data.get("last_analysis_date"),

            # Tags
            "tags": data.get("tags", [])[:5],

            # VirusTotal GUI
            "vt_link": f"https://www.virustotal.com/gui/file/{data.get('sha256')}"
        }
    return {k:v for k, v in result.items() if v is not None}