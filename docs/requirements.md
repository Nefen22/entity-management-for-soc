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

NFR-07: Code coverage for critical paths (authentication, entity management, graph queries) shall be ≥95%.

NFR-08: Integration tests shall cover all public API endpoints.

NFR-09: Authentication shall support test mode bypass via environment variable for CI/CD testing.

NFR-10: All new code shall include unit tests with minimum 80% coverage.

---

# Testing Requirements

## Test Coverage

**Target Coverage:** 95% for critical paths, 80%+ overall

**Current Status:** 89% overall coverage (58 passing tests)

### Critical Path Modules (Target: ≥95%)
- `backend/auth/jwt.py` - 95% ✅
- `backend/services/auth.py` - JWT validation and user authentication
- `backend/api/entities.py` - Entity CRUD endpoints
- `backend/parsers/` - All parser implementations

### High-Priority Modules (Target: ≥90%)
- `backend/repositories/entities.py` - Entity storage and retrieval
- `backend/repositories/graph.py` - Graph query operations
- `backend/services/enrichment.py` - Data enrichment logic
- `backend/services/graph.py` - Graph traversal operations

### Coverage by Component:

| Component | Coverage | Status |
|-----------|----------|--------|
| Auth & JWT | 95% | ✅ Excellent |
| Parsers | 92-100% | ✅ Excellent |
| Entity Management | 81-100% | ✅ Good |
| Graph Operations | 81-91% | ✅ Good |
| Enrichment | 83-92% | ✅ Good |
| API Endpoints | 73-88% | ⚠️ Fair |
| Database Layer | 100% | ✅ Excellent |
| Models | 100% | ✅ Excellent |

## Test Organization

### Unit Tests (44 tests)
- `test_auth.py` - Authentication service and JWT (8 tests)
- `test_enrichment.py` - IP/hash enrichment (3 tests)
- `test_entities_repo.py` - Entity repository CRUD (3 tests)
- `test_graph_service.py` - Graph query logic (13 tests)
- `test_parser.py` - Log parsing (18 tests)
- `test_audit_logs.py` - Audit logging (3 tests)

### Integration Tests (12 tests)
- `test_api.py` - Full API endpoint testing
- Real Neo4j database interaction
- Multi-tenant scenarios
- End-to-end data flow

### Test Environment
- Isolated Neo4j database (neo4j-test container)
- Test dataset pre-loaded
- Authentication bypass via `TESTING_IN_DOCKER=true`
- Automatic cleanup after test runs

## Authentication Testing

### JWT Token Testing
- ✅ Valid token decoding
- ✅ Expired token detection
- ✅ Invalid signature detection
- ✅ Malformed token rejection

### Login Testing
- ✅ Nonexistent user handling
- ✅ Wrong password rejection
- ✅ Correct credential acceptance
- ✅ Token expiration validation

### Test Mode Support
- Authentication bypass when `TESTING_IN_DOCKER=true`
- Admin user auto-injection with "all" tenant access
- Allows CI/CD tests without credential setup

## Continuous Integration

### Automated Testing
- Run on every pull request
- Run on main branch commits
- Coverage report generation
- Exit code indicates pass/fail

### Docker-Based Testing
```bash
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

- Runs in isolated environment
- No local dependencies required
- Reproducible test results
- CI/CD pipeline compatible

## Test Execution Standards

### Before Commit
- All unit tests passing
- No new coverage regressions
- All modified code has test coverage

### Pull Request Requirements
- All tests passing
- Coverage maintained or improved
- Test documentation updated
- No skipped/xfail tests without approval

### Release Standards
- 80%+ coverage for all code
- 95%+ coverage for critical paths
- All integration tests passing
- Performance benchmarks met

---

See [TESTING.md](TESTING.md) for comprehensive testing documentation.
