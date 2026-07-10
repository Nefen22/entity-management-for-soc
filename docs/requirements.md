# Functional Requirements

## V1
- FR-01: Ingest SIEM, EDR, cloud audit, and structured alert events from JSON input.
- FR-02: Extract entities from logs and alerts, including User, Host, IP, Domain, URL, FileHash, Process, Email, CloudResource, and CVE.
- FR-03: Store entities and relationships in Neo4j with tenant-specific graph labels.
- FR-04: Query entity relationships using multi-hop traversal and path-finding workflows.
- FR-05: Enrich IP entities with GeoIP and AbuseIPDB data when available.
- FR-06: Enrich file hash entities using VirusTotal-compatible data with mock fallback.
- FR-07: Visualize graph relationships for a selected entity.
- FR-08: Support configurable parsers for different log sources, including LLM-assisted free-text extraction.
- FR-09: Maintain relationship metadata including first_seen, last_seen, count, and evidences.

## V2
- FR-10: Support tenant-aware authorization with MongoDB-backed users, roles, and permissions.
- FR-11: Persist raw events in MongoDB and expose them through event lookup endpoints.
- FR-12: Persist audit logs in MongoDB and support filtering and pagination in the audit-log API.
- FR-13: Support both automatic and manual enrichment workflows.
- FR-14: Support graceful degradation when external enrichment services are unavailable.
- FR-15: Generate ULID-based event identifiers when the source payload omits one.

# Non-Functional Requirements

- NFR-01: The system shall support tenant-scoped graph ingestion and investigation.
- NFR-02: Enrichment failures shall not prevent entity storage or graph creation.
- NFR-03: The system shall be deployable using Docker Compose.
- NFR-04: The system shall expose API documentation through Swagger UI.
- NFR-05: Authentication shall support test mode bypass for CI/CD testing via the TESTING_IN_DOCKER environment variable.
- NFR-06: New behavior shall be covered by pytest-based unit and integration tests.

---

# Testing Requirements

## Test Coverage

The current implementation is validated through pytest-based tests covering auth, parsers, enrichment, graph operations, and audit logging.

### Test Environment
- Isolated MongoDB, Neo4j, and Redis services in Docker for integration runs
- Test dataset seeding via the `SEED_NAME=TEST` environment variable
- Authentication bypass via `TESTING_IN_DOCKER=true`

### Test Execution

```bash
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

### Key Areas Covered
- Authentication and JWT handling
- Entity and graph repository behavior
- Parser extraction logic
- Enrichment fallback behavior
- Audit log persistence and filtering

See [TESTING.md](TESTING.md) for detailed test documentation.
