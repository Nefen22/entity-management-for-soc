# Entity Management for SOC

A lightweight SOC investigation platform that ingests security events, extracts entities, stores graph relationships in Neo4j, and keeps authentication, raw events, and audit logs in MongoDB for investigation and review.

---

## Quick Start

### Prerequisites
- Docker Compose
- Python 3.12+ (for local development)
- Optional: API keys for AbuseIPDB and VirusTotal if you want external enrichment to run

### Start the stack

```bash
git clone https://github.com/Nefen22/entity-management-for-soc
cd entity-management-for-soc
docker compose up -d
```

The compose stack starts MongoDB, Mongo Express, Neo4j, Redis, the FastAPI backend, and the frontend.

| Service | URL |
| ------- | --- |
| API Docs (Swagger) | http://localhost:8000/docs |
| Frontend | http://localhost |
| Neo4j Browser | http://localhost:7474 |
| Mongo Express | http://localhost:8081 |

### Login and ingest a sample event

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Use the returned token to call tenant-scoped endpoints such as:

```bash
POST /api/tenants/{tenant}/graphs/ingest
GET /api/tenants/{tenant}/graphs/entities/types/User/values/admin?hop=1
```

---

## Features

### Entity extraction

Supported entity types include User, Host, IP, Domain, URL, FileHash, Process, Email, CloudResource, and CVE.

### Graph investigation

- Neo4j-backed relationship storage and multi-hop traversal
- Cluster analysis, path finding, relationship filtering, and entity lookup
- Tenant-scoped graph endpoints with graph labels per tenant

### Enrichment

- IP enrichment with GeoIP and AbuseIPDB data
- File hash enrichment with VirusTotal-compatible data and a mock fallback
- Automatic and manual enrichment workflows
- Graceful fallback when external services are unavailable

### Security and access control

- MongoDB-backed authentication with users, roles, and tenant-aware permissions
- JWT-based access for API requests
- Role-based access control for graph view, ingest, and enrichment operations

### Audit and evidence

- Raw events are stored in MongoDB under the events collection
- Audit logs are stored in MongoDB and support pagination plus filtering by time range, action, entity type, and entity id
- Evidence references an event_id so the original raw event can be retrieved from MongoDB
- Event IDs are generated with ULID when missing

---

## Tech Stack

| Layer | Technology |
| ----- | ---------- |
| Backend | FastAPI |
| Graph database | Neo4j |
| Metadata store | MongoDB |
| Cache | Redis |
| Frontend | HTML, JavaScript |
| Graph UI | Cytoscape.js |
| Container | Docker Compose |

---

## Environment variables

The backend uses the following environment variables:

- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- `MONGODB_URI`, `MONGODB_DATABASE`
- `JWT_SECRET_KEY`
- `REDIS_HOST`
- `GEMINI_API_KEY`, `ABUSEIPDB_API_KEY`, `VIRUSTOTAL_API_KEY`
- `TESTING_IN_DOCKER`, `RESET_DB`, `INIT_DB`, `SEED_NAME`

---

## Project structure

```text
backend/
  api/            # FastAPI routers
  auth/           # JWT and password helpers
  database/       # Neo4j, MongoDB, and seeding logic
  repositories/   # Neo4j and MongoDB repositories
  services/       # Business logic for entities, graph, auth, logs, enrichment
  parsers/        # JSON, alert, LLM, and edge parsers
frontend/         # Static UI assets
 docs/             # Architecture, requirements, testing, and ADRs
```

---

## Testing

The project includes pytest-based unit and integration tests that exercise authentication, parser logic, enrichment, graph operations, and audit logging.

### Running tests in Docker

```bash
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

The test environment boots MongoDB, Neo4j, Redis, and the API container in isolation.

See [docs/TESTING.md](docs/TESTING.md) for more detail.

---

## Documentation

- [docs/architecture.md](docs/architecture.md)
- [docs/requirements.md](docs/requirements.md)
- [docs/TESTING.md](docs/TESTING.md)
- [docs/roadmap.md](docs/roadmap.md)

---

## Project Status

The core backend, frontend, and investigation workflow are implemented and running. The current implementation focuses on MongoDB-backed persistence, tenant-aware authorization, graph investigation, and enrichment with graceful fallback behavior.