# Entity Management for SOC

A lightweight security investigation platform that extracts entities from security events, enriches them with threat intelligence data, and stores relationships in a Neo4j graph database for investigation and visualization.

---

## Features

### Entity Extraction

Extracts entities from structured security logs:

| Entity Type | Description |
|---|---|
| User | Account names, usernames |
| Host | Hostnames, machine names |
| IP Address | IPv4/IPv6 addresses |
| Domain | Domain names |
| File Hash | MD5, SHA1, SHA256 |
| URL | Web URLs |
| Process | Process names and paths |
| Cloud Resource | Cloud asset identifiers |
| Email | Email addresses |
| CVE | CVE identifiers |

### Custom Log Parsers

Support multiple log sources:

- **SIEM Logs** — structured security event logs
- **EDR Logs** — endpoint detection and response events
- **Cloud Audit Logs** — cloud provider activity logs

### Entity Enrichment

**IP Address:**
- GeoLite2 Country/City lookup
- ASN information

**File Hash:**
- Mock VirusTotal API (offline dataset)

All enrichment results are cached in-memory with TTL to avoid redundant lookups.

### Graph Relationship Modeling

Entities and relationships are stored in Neo4j. Example investigation path:

```
john.doe
    │
 LOGGED_IN
    │
DESKTOP-001
    │
CONNECTED_TO
    │
192.168.1.100
```

Supported relationships:

- `User -[LOGGED_IN]-> Host`
- `Host -[CONNECTED_TO]-> IP`
- `File -[EXECUTED_ON]-> Host`

Each relationship stores: `first_seen`, `last_seen`, `count`.

### Investigation

- Multi-hop graph traversal (1–2 hop)
- Entity relationship lookup
- Graph visualization via Cytoscape.js

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python |
| Database | Neo4j |
| Frontend | HTML, JavaScript, Cytoscape.js |
| Infrastructure | Docker, Docker Compose |
| Testing | Pytest |

---

## Project Structure

```
.
├── backend
│   ├── api
│   │   ├── entities.py
│   │   ├── enrichment.py
│   │   └── graph.py
│   ├── parsers
│   │   ├── base_parser.py
│   │   ├── siem_parser.py
│   │   ├── edr_parser.py
│   │   └── cloud_parser.py
│   ├── enrichment
│   │   ├── geoip.py
│   │   └── virustotal_mock.py
│   ├── graph
│   │   ├── entity_service.py
│   │   └── relationship_service.py
│   ├── database
│   │   ├── neo4j.py
│   │   └── schemas.py
│   ├── tests
│   │   ├── test_parser.py
│   │   ├── test_enrichment.py
│   │   └── test_graph.py
│   └── main.py
├── frontend
├── datasets
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- MaxMind GeoLite2 database (free account required at [maxmind.com](https://www.maxmind.com))

### Run

```bash
git clone <repo-url>
cd entity-management

docker compose up -d
```

| Service | URL |
|---|---|
| API (Swagger) | http://localhost:8000/docs |
| Neo4j Browser | http://localhost:7474 |
| Frontend | http://localhost:3000 |

### Ingest Sample Data

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d @datasets/sample_siem.json
```

---

## Sample Datasets

Included under `datasets/`:

| File | Description |
|---|---|
| `sample_siem.json` | Authentication and network events |
| `sample_edr.json` | File execution and process events |
| `sample_cloud.json` | Cloud audit log events |

---

## API Overview

| Method | Endpoint | Description |
|---|---|---|
| POST | `/ingest` | Ingest event log, extract entities and relationships |
| GET | `/entities/{type}` | List all entities of a type |
| GET | `/entities/{type}/{id}` | Get entity detail with enrichment |
| GET | `/entities/{type}/{id}/graph` | Get relationship graph for an entity |
| POST | `/entities/{type}/{id}/enrichment` | Enrich an entity |
| POST | `/relationships` | Create relationship between entities |

Full documentation available at `/docs` (Swagger UI).

---

## Roadmap

- [x] Entity Extraction
- [x] Neo4j Graph Modeling
- [x] GeoLite2 Enrichment
- [x] VirusTotal Mock Integration
- [x] Cytoscape.js Visualization
- [x] Audit Log
- [ ] Unit & Integration Tests
- [ ] CI/CD Pipeline
