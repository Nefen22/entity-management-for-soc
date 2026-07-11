# Functional & Non-Functional Requirements

This document outlines the functional and non-functional requirements implemented in the Entity Management for SOC platform (v2.0.0).

---

## 1. Functional Requirements

### Event Ingestion & Parsing
- **FR-01: Multi-Source Ingestion**: Ingest security events and logs from SIEM, EDR, Cloud Audit, and Alert sources via single-event or batch JSON payloads.
- **FR-02: Parser Fallback Pipeline**:
  1. **JsonParser**: Matches structured EDR, SIEM, or Cloud sources based on config mappings.
  2. **LLMParser**: Uses a Large Language Model (Gemini 2.5 Flash) with variable substitution (`<ips_0>`, etc.) to parse free-text/unstructured alerts.
  3. **AlertParser**: Regex fallback to extract IOCs from text using `iocextract` if JSON and LLM parsing fail.
- **FR-03: Entity Extraction**: Extract 10 distinct entity types: User, Host, IP, Domain, URL, FileHash, Process, Email, CloudResource, and CVE.
- **FR-04: Relationship Mapping**: Dynamically construct directed relationships (e.g. `CONNECTED_TO`, `LOGGED_IN`, `EXECUTED_ON`) based on node occurrences.
- **FR-05: ULID Validation**: Automatically generate a unique ULID for any event that does not contain a pre-existing `event_id`.

### Database & Storage
- **FR-06: Property Graph Storage**: Store entities and relationships in Neo4j under tenant-prefixed labels.
- **FR-07: Log Archiving**: Persist the raw incoming event payloads inside the MongoDB `events` collection.
- **FR-08: Audit Log Auditing**: Store every node/relationship creation or update transaction inside the MongoDB `audit_logs` collection.

### Traversal, Enrichment, & Query
- **FR-09: Multi-Hop Traversal**: Query n-hop connections and find shortest paths between suspicious entities.
- **FR-10: Caching Enrichment**: Orchestrate enrichment for IPs (GeoIP, AbuseIPDB) and FileHashes (VirusTotal API with a local Mock JSON fallback) with 1-hour Redis TTL cache.
- **FR-11: Graceful Enrichment Fallback**: If external APIs fail, bypass enrichment without blocking the core event ingestion pipeline.

### Authentication & Tenant Isolation
- **FR-12: JWT & RBAC**: Enforce username/password JWT authentication and role-based permissions (`graph:ingest`, `graph:view`, `graph:enrichment`).
- **FR-13: Multi-Tenant Scoping**: Restrict data visibility and ingestion parameters based on user's authorized tenants, enforced at both the API and database levels.

---

## 2. Non-Functional Requirements

- **NFR-01: Performance & Caching**: Cache all enrichment requests in Redis to limit database querying and avoid API throttling.
- **NFR-02: Security & Encryption**: Store passwords using bcrypt hashes. Protect REST endpoints using RS256/HS256 signed JWT tokens.
- **NFR-03: Deployment**: Package the entire stack (API, Nginx, Neo4j, MongoDB, Redis, Mongo Express) in a single unified `docker-compose.yml` configuration.
- **NFR-04: API Documentation**: Automatically generate and serve OpenAPI documentation via Swagger UI.
- **NFR-05: Test Auth Bypass**: Support `TESTING_IN_DOCKER=true` to skip normal JWT signature validation inside the testing containers, allowing mock-free integration tests.
