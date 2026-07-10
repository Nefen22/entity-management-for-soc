# Testing Documentation

## Overview

The project uses pytest for unit and integration tests and runs them in Docker with MongoDB, Neo4j, Redis, and the FastAPI service.

---

## Test Structure

```text
backend/test/
├── conftest.py
├── integration/
│   ├── conftest.py
│   └── test_api.py
└── unit/
    ├── conftest.py
    ├── mocks/
    ├── test_auth.py
    ├── test_enrichment.py
    ├── test_entities_repo.py
    ├── test_graph_service.py
    ├── test_parser.py
    └── test_audit_logs.py
```

---

## Running Tests

### Docker (recommended)

```bash
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

This starts an isolated test environment with:
- `mongodb-test`
- `neo4j-test`
- `redis-test`
- `api-test`

The API container runs pytest with coverage output and uses `TESTING_IN_DOCKER=true` to bypass normal authentication for integration scenarios.

### Local development

```bash
pip install -r requirements.txt
pytest backend/test/ -v
```

---

## What the tests cover

- Authentication and JWT handling
- MongoDB-backed user and role loading
- Entity creation and graph repository logic
- Parser extraction for structured and free-text events
- Enrichment fallback handling
- Audit log persistence and filtering

---

## Important test environment variables

- `TESTING_IN_DOCKER=true` - bypasses normal auth checks in the test container
- `NEO4J_URI=bolt://neo4j-test:7687`
- `MONGODB_URI=mongodb://root:secret_password123@mongodb-test:27017/?authSource=admin`
- `MONGODB_DATABASE=test_db`
- `RESET_DB=true`
- `INIT_DB=true`
- `SEED_NAME=TEST`

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
