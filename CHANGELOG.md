# Changelog

All notable changes to the Entity Management for SOC project are documented in this file.

---

## [2.0.0] - 2026-07-11

### Added
- **MongoDB Persistence**: Transitioned user accounts, roles, raw events, and audit logs to MongoDB collections (`users`, `roles`, `events`, `audit_logs`).
- **Redis Enrichment Caching**: Added Redis caching with a 1-hour TTL for AbuseIPDB, GeoIP, and VirusTotal lookup queries.
- **Dynamic Readiness Probe**: Implemented `/health/ready` check verifying live database connections.
- **Audit Diff Logging**: Audit logs now calculate and store Pydantic JSON serialization property diffs (`before` vs `after` states) dynamically in MongoDB.
- **LLM Token Substitution**: Built IP, hash, and domain placeholder substitution logic inside `LLMParser` before submitting logs to Google Gemini.
- **Docker Integration Testing**: Setup isolated `docker-compose.test.yml` workflows using test container databases.

### Changed
- Refactored `backend/services/graph.py` and `backend/services/entities.py` to write and retrieve audit entries directly via MongoDB repository drivers.
- Switched default token permission resolution checks from file-based seeding maps to MongoDB dynamic query matches.
- Increased total coverage target metrics to 96% with 129 passing test suites.

---

## [1.0.0] - 2026-06-15

### Added
- Initial release containing FastAPI and Neo4j integration.
- Cypher model mappings and multi-tenant labels (`Tenant_{name}`).
- Structured event parsers for SIEM, EDR, and Cloud schemas.
- Interactive graph explorer using Cytoscape.js.
- Basic mock GeoIP enrichment provider.
