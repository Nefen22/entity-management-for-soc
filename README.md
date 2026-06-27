# Entity Management for SOC

A lightweight SOC investigation platform that extracts entities from security events, enriches threat intelligence data, and stores relationships inside Neo4j for graph-based investigation and visualization.

---

## Getting Started

```bash
git clone https://github.com/Nefen22/entity-management-for-soc
cd entity-management-for-soc
docker-compose up -d
```

| Service | URL |
| ------- | --- |
| API Docs (Swagger) | http://localhost:8000/docs |
| Frontend | http://localhost |
| Neo4j Browser | http://localhost:7474 |

### Quick Demo

```bash
# Ingest sample data
POST /api/tenants/{tenant}/graphs/ingest/sample

# Query entity graph (4-hop)
GET /api/tenants/{tenant}/graphs/ip/8.8.8.8/graph/4
```

---

## Features

### Entity Extraction

Supported entities:

| Entity        | Example                                     |
| ------------- | ------------------------------------------- |
| User          | admin                                       |
| Host          | FILE-SERVER-01                              |
| IP            | 192.168.1.100                               |
| Domain        | malicious.ru                                |
| URL           | http://malicious.ru/payload.exe             |
| FileHash      | MD5 / SHA1 / SHA256                         |
| Process       | powershell.exe                              |
| Email         | admin@corp.local                            |
| CloudResource | EC2 instance, VM                            |
| CVE           | CVE-2024-1234                               |

---

### Flexible JSON Parser

The platform supports custom JSON-based event ingestion.

Supported sources:

* SIEM events
* EDR events
* Cloud audit logs
* Custom JSON formats

Parser logic is configurable and easy to extend.

---

### Entity Enrichment

#### IP Enrichment

* GeoIP lookup
* ASN information

#### File Hash Enrichment

* Mock VirusTotal dataset
* Malware detection information

Enrichment results are cached with TTL.

---

### Relationship Modeling

Core relationships:

* User → LOGGED_IN → Host
* Host → CONNECTED_TO → IP
* FileHash → EXECUTED_ON → Host

Additional relationships:

* Process → Host
* Email → User
* CVE → Host
* CloudResource → IP
* URL → Domain

Relationship metadata:

* first_seen
* last_seen
* count
* evidences

---

### Investigation Features

* Entity lookup
* Relationship exploration
* Multi-hop traversal
* N-hop investigation
* Relationship filtering
* Entity type filtering

---

### Graph Visualization

Powered by Cytoscape.js.

Supported layouts:

* Force-directed
* Breadth First Tree
* Dagre Tree
* Concentric

Features:

* Dynamic filtering
* Expand subgraphs
* Node details panel
* Relationship metadata display
* Interactive navigation

---

### Multi-Tenant Support

Each tenant is isolated using graph labels.

Example:

* acme
* google
* internal

API examples:

```
/api/tenants/{tenant}/entities
/api/tenants/{tenant}/graphs
/api/tenants/{tenant}/enrichments
```

---

### Performance

* Neo4j indexes
* Relationship aggregation
* Cached enrichment
* Optimized N-hop queries

---

## Tech Stack

| Layer     | Technology       |
| --------- | ---------------- |
| Backend   | FastAPI          |
| Database  | Neo4j            |
| Frontend  | HTML, JavaScript |
| Graph UI  | Cytoscape.js     |
| Container | Docker           |

---

## Architecture

```
Event
  ↓
Parser (SIEM / EDR / Cloud / Custom JSON)
  ↓
Service Layer
  ↓
Neo4j (label-based multi-tenant)
  ↓
Visualization (Cytoscape.js)
```

* Service layer architecture
* API layer separation
* Parser abstraction
* Multi-tenant routing
* Graph-based investigation model

---

## Implemented Features

* [x] Entity extraction (10 entity types)
* [x] Graph relationship modeling
* [x] Multi-hop investigation
* [x] GeoIP enrichment
* [x] Mock VirusTotal enrichment
* [x] Relationship metadata (first_seen, last_seen, count, evidence)
* [x] Graph visualization
* [x] Multiple layouts
* [x] Dynamic filtering
* [x] Audit log
* [x] Multi-tenant support (label-based)
* [x] Neo4j indexing
* [x] REST API with Swagger docs
* [x] Docker Compose deployment

---

## Roadmap

* [ ] Unit and integration tests
* [ ] CI/CD pipeline
* [ ] Path finding between arbitrary entities
* [ ] Entity deduplication and merge
* [ ] Export graph to PNG/JSON
* [ ] Time-based graph filtering
* [ ] Kafka batch ingestion
* [ ] LLM-based entity extraction from free-text alerts

---

## Project Status

**MVP Complete** — backend, frontend, and core investigation features are implemented and running.

Remaining: test coverage, CI/CD, and optional advanced features listed in the roadmap above.