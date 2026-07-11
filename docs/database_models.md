# Database Models & Schemas

The platform leverages **Neo4j** as a graph database for relationships, **MongoDB** as a document database for operational metadata and audit trails, and **Redis** for transient caching.

---

## 1. Neo4j Graph Database

The graph database maps entities and security connections. Each node contains a tenant-specific database label (e.g. `Tenant_acme`) and an entity type label (e.g. `IP`).

### Entity Node Types & Properties

All nodes carry specific identifier keys alongside optional properties updated by enrichment.

| Node Label | Key Property | Enrichment Properties |
| --- | --- | --- |
| **`IP`** | `value` | `country`, `country_name`, `city`, `region`, `continent`, `latitude`, `longitude`, `timezone`, `network`, `asn`, `organization`, `abuse_score`, `isp`, `usage_type`, `domain`, `last_reported`, `report_count` |
| **`User`** | `username` | N/A |
| **`Host`** | `hostname` | N/A |
| **`Domain`** | `name` | N/A |
| **`FileHash`** | `hash_value` | `md5`, `sha1`, `sha256`, `file_name`, `file_type`, `size`, `malicious`, `suspicious`, `harmless`, `undetected`, `detection_ratio`, `threat_label`, `threat_family`, `reputation`, `last_analysis`, `tags`, `vt_link` |
| **`URL`** | `url` | N/A |
| **`Process`** | `process_name` | N/A |
| **`Email`** | `address` | N/A |
| **`CloudResource`** | `resource_id` | N/A |
| **`CVE`** | `cve_id` | N/A |

### Relationships & Edge Schema

Relationships are directed and created dynamically on log ingestion.

* **Core Relationships**:
  - `(:User)-[:LOGGED_IN]->(:Host)`
  - `(:User)-[:LOGGED_IN_FROM]->(:IP)`
  - `(:Host)-[:CONNECTED_TO]->(:IP)`
  - `(:IP)-[:CONNECTED_TO]->(:Host)`
  - `(:IP)-[:CONNECTED_TO]->(:IP)`
  - `(:FileHash)-[:EXECUTED_ON]->(:Host)`
* **Network & Web**:
  - `(:Host)-[:RESOLVED]->(:Domain)`
  - `(:IP)-[:RESOLVED]->(:Domain)`
  - `(:Domain)-[:RESOLVES_TO]->(:IP)`
  - `(:Host)-[:REQUESTED]->(:URL)`
  - `(:IP)-[:REQUESTED]->(:URL)`
  - `(:Process)-[:REQUESTED]->(:URL)`
  - `(:URL)-[:BELONGS_TO]->(:Domain)`
  - `(:URL)-[:RESOLVES_TO]->(:IP)`
  - `(:URL)-[:DOWNLOADS]->(:FileHash)`
* **Process Execution**:
  - `(:Process)-[:RUNS_ON]->(:Host)`
  - `(:Process)-[:EXECUTED_BY]->(:User)`
  - `(:Process)-[:SPAWNED]->(:Process)`
  - `(:Process)-[:LOADED]->(:FileHash)`
  - `(:Process)-[:CONNECTED_TO]->(:IP)`
  - `(:Process)-[:CONNECTED_TO]->(:Domain)`
* **Email Scope**:
  - `(:User)-[:OWNS]->(:Email)`
  - `(:Email)-[:HOSTED_BY]->(:Domain)`
  - `(:Email)-[:CONTAINS]->(:URL)`
  - `(:Email)-[:ATTACHED]->(:FileHash)`
  - `(:Email)-[:SENT_TO]->(:Email)`
* **Cloud Infrastructure**:
  - `(:User)-[:ACCESSED]->(:CloudResource)`
  - `(:CloudResource)-[:RUNS_ON]->(:Host)`
  - `(:CloudResource)-[:ASSIGNED_TO]->(:IP)`
  - `(:CloudResource)-[:CONNECTED_TO]->(:Domain)`
* **Vulnerability & Threat Intel**:
  - `(:CVE)-[:AFFECTS]->(:Host)`
  - `(:CVE)-[:AFFECTS]->(:Process)`
  - `(:CVE)-[:AFFECTS]->(:CloudResource)`
  - `(:Domain)-[:HOSTS]->(:FileHash)`
  - `(:IP)-[:HOSTS]->(:FileHash)`
  - `(:URL)-[:EXPLOITS]->(:CVE)`
  - `(:Process)-[:EXPLOITS]->(:CVE)`
* **Malware & Lateral Movement**:
  - `(:FileHash)-[:LOADED_BY]->(:Process)`
  - `(:FileHash)-[:DOWNLOADED_FROM]->(:URL)`
  - `(:FileHash)-[:DOWNLOADED_FROM]->(:Domain)`
  - `(:FileHash)-[:DOWNLOADED_FROM]->(:IP)`
  - `(:Host)-[:CONNECTED_TO]->(:Host)`
  - `(:User)-[:AUTHENTICATED_TO]->(:CloudResource)`
* **IOC Context**:
  - `(:Domain)-[:RELATED_TO]->(:Domain)`
  - `(:IP)-[:CONNECTED_TO]->(:Domain)`
  - `(:Domain)-[:HOSTS]->(:URL)`

#### Edge Properties
Every edge carries standard metadata:
```json
{
  "first_seen": "datetime",
  "last_seen": "datetime",
  "count": "integer",
  "evidence": "string (event_id)"
}
```

### Database Constraints & Indexes
Indices are automatically generated on application startup for the lookup keys on each entity type:
- Index on `IP(value)`
- Index on `User(username)`
- Index on `Host(hostname)`
- Index on `Domain(name)`
- Index on `FileHash(hash_value)`
- Index on `URL(url)`
- Index on `Process(process_name)`
- Index on `Email(address)`
- Index on `CloudResource(resource_id)`
- Index on `CVE(cve_id)`

---

## 2. MongoDB Document Database

MongoDB stores user metadata, roles, audit trails, and raw log payloads.

### Collections

#### 1. `users`
Represents the system accounts.
- **Index**: `username` (Unique, ascending)
- **Document Example**:
```json
{
  "_id": "ObjectId",
  "username": "admin",
  "password": "$2b$12$...", // bcrypt hash
  "role": "admin",
  "tenants": ["all"]
}
```

#### 2. `roles`
Configures system roles and permissions (RBAC).
- **Index**: `name` (Unique, ascending)
- **Document Example**:
```json
{
  "_id": "ObjectId",
  "name": "admin",
  "permissions": [
    "graph:view",
    "graph:ingest",
    "graph:enrichment"
  ]
}
```

#### 3. `events`
Stores the original unmodified log events.
- **Indexes**:
  - `(tenant, event_id)` (Unique)
  - `(tenant, timestamp)`
- **Document Example**:
```json
{
  "_id": "ObjectId",
  "tenant": "acme",
  "event_id": "01J2HJK9...", // ULID
  "timestamp": "2026-07-11T18:40:00Z",
  "source_type": "edr",
  "raw_event": {
    "event_id": "01J2HJK9...",
    "source_type": "edr",
    "timestamp": "2026-07-11T18:40:00Z",
    "user": "hr.manager",
    "destination_host": "DESKTOP-HR01",
    "process_name": "powershell.exe",
    "file_hash": "e99a18c428cb38d5f260853678922e03"
  }
}
```

#### 4. `audit_logs`
Chronicles modification actions across the tenant graphs.
- **Indexes**:
  - `(tenant, timestamp)` (Descending)
  - `(tenant, action)`
  - `(tenant, entity_id)`
  - `(tenant, entity_type)`
- **Document Example**:
```json
{
  "_id": "ObjectId",
  "tenant": "acme",
  "timestamp": "2026-07-11 18:42:00.123456",
  "action": "UPDATE",
  "entity_type": "IP",
  "entity_id": "104.21.43.11",
  "event_id": "01J2HJK9...",
  "change": {
    "before": "{\"country\": null}",
    "after": "{\"country\": \"US\", \"abuse_score\": 0, \"asn\": 13335}"
  }
}
```

---

## 3. Redis Caching Model

Redis stores the output of IP and FileHash enrichments in memory.

- **Cache Keys**:
  - **IP Key**: `IP:{ip_address}` (e.g. `IP:104.21.43.11`)
  - **FileHash Key**: `HASH:{hash_value}` (e.g. `HASH:e99a18c428cb38d5f260853678922e03`)
- **Key TTL**: 3600 seconds (1 hour).
- **Stored Format**: JSON string representing the combined enrichment fields of the entity.
