# Testing Documentation

This document explains the testing structure, strategy, and execution steps for the Entity Management for SOC platform.

---

## 1. Test Structure

The codebase utilizes `pytest` to orchestrate both unit and integration tests under the `backend/test/` directory.

```text
backend/test/
├── conftest.py               # Shared global fixtures (MongoDB, Redis, API Client)
├── integration/
│   ├── conftest.py
│   └── test_api.py           # Endpoint integration tests (auth, tenants, graphs, entities, enrich, logs)
└── unit/
    ├── conftest.py
    ├── mocks/                # Mock packages for drivers & settings
    ├── test_audit_logs.py    # MongoDB audit log operations
    ├── test_auth.py          # JWT, bcrypt, & RBAC checks
    ├── test_enrichment.py    # Redis cache & external enrichment handlers
    ├── test_entities_repo.py # Neo4j Node/Relationship operations
    ├── test_graph_service.py # Event ingestion & traversal pipelines
    └── test_parser.py        # JsonParser, AlertParser, and LLMParser variable subst.
```

---

## 2. Test Execution

### Docker Compose (Recommended)
This runs the entire test suite inside a dedicated, isolated environment containing mock-ready databases.

```bash
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

This commands spins up:
- `mongodb-test`: Isolated MongoDB container.
- `neo4j-test`: Isolated Neo4j container.
- `redis-test`: Isolated Redis container.
- `api-test`: The backend test execution image that runs the `pytest` runner.

### Local Development Running
Ensure you have the required databases (MongoDB, Neo4j, Redis) running locally or configured, then run:

```bash
pip install -r requirements.txt
pytest backend/test/ -v --cov=backend
```

---

## 3. Important Test Environment Variables

- `TESTING_IN_DOCKER=true`: Disables normal signature validation checks on incoming bearer JWT tokens for test routes.
- `NEO4J_URI=bolt://neo4j-test:7687`: Target test graph db instance.
- `MONGODB_URI=mongodb://root:secret_password123@mongodb-test:27017/?authSource=admin`: Target metadata db.
- `MONGODB_DATABASE=test_db`: Isolated database name for tests.
- `RESET_DB=true`: Forces graph repository initialization on startup.
- `INIT_DB=true`: Automatic seeding.
- `SEED_NAME=TEST`: Loads test datasets.

---

## 4. Test Coverage & Metrics

The project maintains high testing standards to prevent regressions in security analytics parsing and multi-tenant isolation routing.

### Current Test Execution Summary:
- **Total Tests**: 129 passed, 1 expected failure (`xfailed`).
- **Statement Coverage**: **96%** (covers API routing, repositories, parse pipelines, and audit logs).

### Coverage Areas Covered:
- **Authentication**: JWT token encoding, parsing, expiration, role mapping, and permission checks.
- **Parsers**: Custom JSON parsing rules, regex alert extraction, and LLM substitution validation.
- **Enrichments**: GeoIP, AbuseIPDB, and VirusTotal enrichment mapping combined with Redis caching hits and TTL validation.
- **Audit Logs**: Correct document insertion and retrieval on updates/creates with MongoDB filter limits.
- **Readiness Probes**: Dynamic connection check for database pings.
