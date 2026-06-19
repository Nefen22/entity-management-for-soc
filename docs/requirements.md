#Functinal Requirements 

##V1
FR-01: Ingest SIEM logs from JSON input.

FR-02: Ingest EDR logs from JSON input.

FR-03: Ingest Cloud Audit logs from JSON input.

FR-04: Ingest security alerts in structured JSON format.

FR-05: Extract entities from logs and alerts.
        Supported entity types:
        - User
        - Host
        - IP
        - Domain
        - File Hash
        
FR-06: Store entities and relationships in Neo4j graph database.

FR-07: Query entity relationships up to N-hop traversal.

FR-08: Enrich IP entities using offline GeoIP database.

FR-09: Enrich file hash entities using VirusTotal-compatible mock service.

FR-10: Visualize graph relationships for a selected entity.

FR-11: Support custom parsers for different log sources
        (SIEM, EDR, Cloud Audit Log).

FR-12: Maintain relationship metadata including:
        - first_seen
        - last_seen
        - count
        - evidence

##V2
FR-13: Support more entities:
        - URL
        - Process
        - Cloud resource
        - Email
        - CVE

FR-14: Extract entities from free-text alerts and incident descriptions using LLMs.

FR-15: Support advanced enrichment sources:
        - WHOIS
        - AbuseIPDB
        - AlienVault OTX
        - VirusTotal API

FR-16: Support interactive graph exploration:
        - expand node
        - pivot node
        - filter by relationship type
        - filter by time range

FR-17: Support path finding between arbitrary entities.

FR-18: Support entity deduplication and merge.

FR-19: Support graph export to JSON and image formats.

#Non-Functional Requirements

NFR-01: The system shall support at least 10,000 entities.

NFR-02: The system shall support at least 1,000,000 relationships.

NFR-03: Graph query response time shall be less than 3 seconds for 4-hop traversal on the sample dataset.

NFR-04: Enrichment failures shall not prevent entity storage.

NFR-05: The system shall be deployable using Docker Compose.

NFR-06: The system shall expose API documentation through Swagger UI.