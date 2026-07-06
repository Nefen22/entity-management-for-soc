# Testing Documentation

## Overview

Entity Management for SOC includes comprehensive unit and integration tests with pytest framework and Docker-based test environment.

**Current Status:**
- ✅ 58 passing tests
- 📊 89% code coverage
- 🚀 Automated test execution via Docker Compose

---

## Test Structure

```
backend/test/
├── conftest.py                 # Global test fixtures
├── integration/
│   ├── conftest.py            # Integration test fixtures
│   └── test_api.py            # API endpoint tests (12 tests)
└── unit/
    ├── conftest.py            # Unit test fixtures & mocks
    ├── mocks/                 # Mock implementations
    │   ├── neo4j.py
    │   ├── constraints.py
    │   ├── datasets.py
    │   ├── enrichment.py
    │   └── audit_log.py
    ├── test_auth.py           # Authentication tests (8 tests)
    ├── test_enrichment.py      # Enrichment service tests (3 tests)
    ├── test_entities_repo.py   # Entity repository tests (3 tests)
    ├── test_graph_service.py   # Graph service tests (13 tests)
    ├── test_parser.py          # Parser tests (18 tests)
    └── test_audit_logs.py      # Audit logging tests (3 tests)
```

---

## Running Tests

### Docker (Recommended)

Run all tests in isolated Docker environment:

```bash
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

This will:
1. Build the test image
2. Start Neo4j test database
3. Run pytest with coverage reporting
4. Display test results and coverage report

**Environment Variables:**
- `TESTING_IN_DOCKER=true` - Enables test authentication bypass
- `NEO4J_URI=bolt://neo4j-test:7687` - Test database connection
- `RESET_DB=true` - Clear database before tests
- `SEED_NAME=TEST` - Load test dataset

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest backend/test/ -v

# Run specific test file
pytest backend/test/unit/test_auth.py -v

# Run with coverage report
pytest backend/test/ --cov=backend --cov-report=html
```

---

## Test Coverage by Module

### ✅ Excellent Coverage (>95%)

| Module | Coverage | Tests |
|--------|----------|-------|
| `backend/auth/jwt.py` | 95% | 4 |
| `backend/api/entities.py` | 100% | - |
| `backend/database/` | 100% | - |
| `backend/enrichment/` | 83-92% | 3 |
| `backend/models/` | 100% | - |
| `backend/parsers/edge_parser.py` | 100% | 5 |
| `backend/parsers/json_parser.py` | 100% | 9 |
| `backend/repositories/user.py` | 100% | - |

### 🎯 Good Coverage (80-94%)

| Module | Coverage | Key Tests |
|--------|----------|-----------|
| `backend/api/enrichment.py` | 88% | Entity enrichment |
| `backend/api/graph.py` | 81% | Graph queries |
| `backend/parsers/alert_parser.py` | 92% | Alert parsing |
| `backend/parsers/base_parser.py` | 92% | Base parser logic |
| `backend/repositories/entities.py` | 81% | Entity CRUD ops |
| `backend/repositories/graph.py` | 91% | Graph operations |
| `backend/services/enrichment.py` | 92% | Enrichment service |
| `backend/services/entities.py` | 86% | Entity service |
| `backend/services/graph.py` | 84% | Graph service |

### ⚠️ Moderate Coverage (60-79%)

| Module | Coverage | Notes |
|--------|----------|-------|
| `backend/api/auth.py` | 73% | API auth endpoints |
| `backend/api/tenants.py` | 78% | Tenant routing |
| `backend/parsers/llm_client.py` | 61% | LLM integration |
| `backend/services/auth.py` | 40% | Auth service logic |

---

## Authentication & Test Mode

### Test Authentication

The authentication system supports test mode for integration testing:

**Feature:** When `TESTING_IN_DOCKER=true` environment variable is set:
- All authentication is bypassed
- Test requests receive admin user with "all" tenant access
- No JWT token required for test API calls

**Implementation:** [backend/services/auth.py](../backend/services/auth.py)

```python
async def authenticate_user(request: Request):
    # Allow test mode to bypass authentication
    if os.getenv("TESTING_IN_DOCKER") == "true":
        return {
            "username": "test_user",
            "role": "admin",
            "tenants": "all"
        }
    # ... normal JWT validation
```

**Test Cases:**
- `test_decode_expired_token` - Expired JWT handling
- `test_decode_invalid_token_signature` - Invalid JWT detection
- `test_decode_malformed_token` - Malformed JWT rejection
- `test_decode_valid_token` - Valid JWT acceptance
- `test_login_nonexistent_user` - Non-existent user handling
- `test_login_wrong_password` - Wrong password handling
- `test_verify_password_correct` - Password verification success
- `test_verify_password_incorrect` - Password verification failure

---

## Entity Repository Tests

### MERGE/Upsert Logic

Test: `test_post_entity_merge_existing`
- Verifies Neo4j MERGE clause execution
- Ensures duplicate entities are handled correctly
- Tests entity creation with properties

### Lookup Operations

Test: `test_get_entity_not_found`
- Tests null result handling for non-existent entities
- Verifies proper error states

Test: `test_get_entity_found_with_relationships`
- Tests entity retrieval with relationship metadata
- Verifies first_seen, last_seen, and count fields

---

## Parser Tests

### Alert Parser

Covers free-text security alert parsing:
- IP address extraction (including private IPs)
- Domain name extraction
- File hash detection (MD5)
- Entity type classification
- Multiple entity extraction

### JSON Parser

Covers structured log parsing from:
- SIEM events - User, IP, Host extraction
- EDR events - Process, hash, user extraction
- Cloud audit logs - Cloud resources, hosts
- Custom JSON formats

### Base Parser

Covers generic parsing functionality:
- Node and edge extraction
- Relationship mapping
- Timestamp handling
- Evidence tracking

---

## Audit Log Tests

Tests for audit logging functionality:

1. **test_write_audit_log_missing_change_field**
   - Logs with optional change field omitted
   - Tests graceful handling of missing data

2. **test_write_audit_log_with_change_payload**
   - Logs with complete change tracking
   - Tests before/after state preservation

3. **test_write_audit_log_with_all_fields**
   - Full audit entry with all fields
   - Tests complete logging capability

---

## Integration Tests

### API Endpoints Tested

All 12 integration tests validate actual API responses:

- `/api/tenants` - Tenant listing
- `/api/tenants/{tenant}/entities/lists` - Entity enumeration
- `/api/tenants/{tenant}/entities/lists?type=X` - Type filtering
- `/api/tenants/{tenant}/entities/types/X/values/Y` - Entity lookup
- `/api/tenants/{tenant}/graphs/entities/...?hop=1` - 1-hop traversal
- `/api/tenants/{tenant}/graphs/entities/...?hop=2` - 2-hop traversal
- `/api/tenants/{tenant}/graphs/get-types` - Type listing
- `/api/tenants/{tenant}/graphs/filter-relationships` - Relationship filtering
- `/api/tenants/{tenant}/graphs/clusters` - Cluster analysis
- `/api/tenants/{tenant}/graphs/clusters/types/X` - Type clustering
- `/api/tenants/{tenant}/enrichments/types/ips/values/X` - IP enrichment
- `/api/tenants/{tenant}/enrichments/types/file-hashes/values/X` - Hash enrichment

---

## Fixtures & Mocks

### Key Test Fixtures

**Global Fixtures** (`backend/test/conftest.py`):
- `api` - FastAPI TestClient for API testing
- Path mocking to prevent file system writes

**Unit Test Fixtures** (`backend/test/unit/conftest.py`):
- `geoip_reader` - Mock GeoIP2 reader
- `vt_dataset` - VirusTotal mock data
- Database mocks for Neo4j
- Constraint mocks for tenant database

**Integration Fixtures** (`backend/test/integration/conftest.py`):
- Real Neo4j connection
- Test dataset loading
- Tenant seeding

### Mock Modules

Located in `backend/test/unit/mocks/`:
- `neo4j.py` - Mock Neo4j driver
- `constraints.py` - Mock database constraints
- `datasets.py` - Mock seed datasets
- `enrichment.py` - Mock enrichment services
- `audit_log.py` - Mock audit logging

---

## Coverage Goals

### Target: 95%+ for Critical Paths

**Phase 1 (Current):** 89%
- ✅ Authentication & JWT
- ✅ Entity repositories
- ✅ Parsers (all types)
- ✅ Core API endpoints

**Phase 2 (Upcoming):**
- Auth API endpoints (api/auth.py)
- Logs API endpoints (api/logs.py)
- Advanced graph operations
- Error scenarios

---

## Best Practices

### Test Organization

1. **Arrange-Act-Assert (AAA) Pattern**
   ```python
   def test_something():
       # Arrange
       test_data = create_test_data()
       
       # Act
       result = function_under_test(test_data)
       
       # Assert
       assert result == expected_value
   ```

2. **Use Descriptive Names**
   - Test class: `TestComponentFeature`
   - Test method: `test_specific_behavior_with_condition`
   - Docstrings: Explain what is being tested

3. **Mock External Dependencies**
   - Database calls
   - API calls
   - File I/O
   - HTTP requests

4. **Async Test Support**
   ```python
   @pytest.mark.asyncio
   async def test_async_function():
       result = await async_function()
       assert result is not None
   ```

---

## Troubleshooting

### Common Issues

**Test fails with "ImportError"**
- Ensure PYTHONPATH includes backend directory
- Check conftest.py path adjustments
- Verify mock module imports

**Database connection errors in tests**
- Check NEO4J_URI environment variable
- Ensure neo4j-test container is running
- Verify network configuration

**Coverage reports incomplete**
- Run tests with `--cov=backend` flag
- Check file exclusions in pytest.ini
- Verify pytest-cov is installed

### Debug Mode

```bash
# Verbose output
pytest backend/test/ -vv

# Show print statements
pytest backend/test/ -s

# Show local variables on failure
pytest backend/test/ -l

# Stop on first failure
pytest backend/test/ -x
```

---

## CI/CD Integration

Tests are designed to run in CI/CD pipelines:

**Docker Compose Test Environment:**
- Isolated test database (Neo4j)
- Pre-loaded test datasets
- Automatic cleanup after tests
- Exit code indicates pass/fail

**GitHub Actions:**
- Run on PR creation
- Run on main branch commits
- Generate coverage reports
- Publish test results

---

## Contributing Tests

When adding new features, include tests:

1. **Unit Tests** - Test business logic in isolation
2. **Integration Tests** - Test API endpoints
3. **Fixtures** - Create reusable test data
4. **Documentation** - Document test purpose

Minimum coverage requirement: **80%** for new code
Target coverage: **95%** for critical paths

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/advanced/testing-events/)
- [Neo4j Testing Guide](https://neo4j.com/developer/python/)
