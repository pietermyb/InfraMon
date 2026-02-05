# Test Coverage Strategy for 80% Target

## Current Status (Live)

- **Total Lines of Code:** 2,934
- **Lines Covered:** ~1,568
- **Lines Missing:** ~1,366
- **Tests Passing:** 201 (all passing)
- **Current Coverage:** 47%
- **CI Threshold:** 45% (fail_under)
- **Target Coverage:** 80% (+33% remaining)

---

## Progress Tracking

### ✅ Completed Phases

- [x] **P1: Authentication & Authorization** - Core auth, security, exceptions, middleware
- [x] **P2: API Router & Container Operations** - Container endpoints, groups, stats, main app

### 🔄 Current Phase

- [ ] **P3: Docker Service Integration** - Container lifecycle with Docker daemon

### ⏳ Pending Phases

- [ ] **P4: Stats Service Integration** - System and container statistics
- [ ] **P5: Repository & Database** - CRUD operations, session management
- [ ] **P6: Services** - Auth, container, metrics services
- [ ] **P7: User Management API** - User CRUD and activation/deactivation

---

## Coverage by Module

### ✅ Fully Covered (80%+)
| Module | Lines | Coverage | Status |
|--------|-------|----------|--------|
| app/models/* | 104 | 100% | Complete |
| app/schemas/container.py | 166 | 100% | Complete |
| app/schemas/stats.py | 178 | 100% | Complete |
| app/schemas/docker_compose.py | 68 | 100% | Complete |
| app/core/config.py | 38 | 100% | Complete |
| app/api/__init__.py | 2 | 100% | Complete |
| app/api/v1/__init__.py | 2 | 100% | Complete |
| app/services/__init__.py | 5 | 100% | Complete |
| app/schemas/user.py | 72 | 93% | Near Complete |
| app/core/exceptions.py | 38 | 100% | Complete |

### 🔄 Partial Coverage (35-80%)
| Module | Lines | Coverage | Missing |
|--------|-------|----------|---------|
| app/core/security.py | 108 | 73% | 25 lines |
| app/core/middleware.py | 55 | 48% | 26 lines |
| app/api/v1/router.py | 406 | 46% | 190 lines |
| app/api/v1/auth.py | 46 | ~50% | 23 lines |

### ⏳ Low Coverage (<35%)
| Module | Lines | Coverage | Missing |
|--------|-------|----------|---------|
| app/api/v1/users.py | 92 | 0% | 92 lines |
| app/core/auth.py | 97 | 57% | 34 lines |
| app/db/container_repository.py | 25 | 56% | 11 lines |
| app/db/user_repository.py | 35 | 46% | 17 lines |
| app/services/container_service.py | 59 | 34% | 34 lines |
| app/db/database.py | 20 | 45% | 11 lines |
| app/db/repository.py | 56 | 26% | 39 lines |
| app/services/auth_service.py | 37 | 26% | 25 lines |
| app/services/docker_service.py | 587 | 32% | 384 lines |
| app/services/stats_service.py | 377 | 19% | 289 lines |
| app/services/metrics_collector.py | 51 | 0% | 51 lines |
| app/db/base.py | 14 | 0% | 14 lines |
| app/main.py | 96 | 30% | 65 lines |

---

## Detailed Progress

### ✅ P1: Critical - Authentication & Authorization
| Component | Before | After | Status |
|-----------|--------|-------|--------|
| app/api/v1/auth.py | 0% | ~50% | [x] |
| app/core/auth.py | 46% | 57% | [x] |
| app/core/security.py | 63% | 73% | [x] |
| app/core/exceptions.py | 0% | 100% | [x] |
| app/core/middleware.py | 0% | 48% | [x] |

### ✅ P2: API Router & Container Operations
| Component | Tests | Status |
|-----------|-------|--------|
| test_api_auth.py | 18 tests | [x] |
| test_api_containers.py | 30+ tests | [x] |
| test_core_auth.py | 15 tests | [x] |
| test_core_security.py | 15 tests | [x] |
| test_core_exceptions.py | 20 tests | [x] |
| test_core_middleware.py | 10 tests | [x] |
| test_main.py | 13 tests | [x] |
| test_stats_service_full.py | 21 tests | [x] |
| test_services.py | 13 tests | [x] |

---

## Remaining Work

### 🔄 P3: Docker Service Integration
**Target:** +10% coverage (32% → 42%)

- [ ] Container lifecycle operations with Docker daemon
- [ ] Container inspection and monitoring
- [ ] Docker compose operations
- [ ] Requires: Docker daemon access or mocking

### ⏳ P4: Stats Service Integration
**Target:** +5% coverage (19% → 24%)

- [ ] System statistics collection (CPU, memory, disk, network)
- [ ] Container statistics
- [ ] Historical data retrieval
- [ ] Requires: psutil or mocking

### ⏳ P5: Repository & Database
**Target:** +3% coverage (26% → 29%)

- [ ] Base repository CRUD operations
- [ ] User repository methods
- [ ] Container repository methods
- [ ] Database connection handling

### ⏳ P6: Additional Services
**Target:** +2% coverage (34% → 36%)

- [ ] Auth service methods
- [ ] Container service methods
- [ ] Metrics collection

### ⏳ P7: User Management API
**Target:** +8% coverage (0% → 8%)

- [ ] GET /users (list, filter, pagination)
- [ ] GET /users/{user_id} (get user, not found)
- [ ] POST /users (create, validation)
- [ ] PUT /users/{user_id} (update)
- [ ] DELETE /users/{user_id} (delete)
- [ ] User activation/deactivation

---

## Test File Structure

```
tests/
├── unit/
│   ├── test_api_auth.py ✅ (18 tests)
│   ├── test_api_containers.py ✅ (30+ tests)
│   ├── test_core_auth.py ✅ (15 tests)
│   ├── test_core_security.py ✅ (15 tests)
│   ├── test_core_exceptions.py ✅ (20 tests)
│   ├── test_core_middleware.py ✅ (10 tests)
│   ├── test_main.py ✅ (13 tests)
│   ├── test_stats_service_full.py ✅ (21 tests)
│   ├── test_services.py ✅ (13 tests)
│   └── test_repositories.py ⏳ (pending)
├── integration/
│   ├── test_docker_service.py ⏳ (pending)
│   ├── test_stats_service.py ⏳ (pending)
│   └── test_database.py ⏳ (pending)
└── e2e/
    ├── test_auth_flow.py ⏳ (pending)
    ├── test_container_operations.py ⏳ (pending)
    └── test_stats_operations.py ⏳ (pending)
```

---

### Coverage Progress

| Phase | Tests | Coverage Gain | Status |
|-------|-------|--------------|--------|
| P1: Auth & Core | ~78 tests | +11% | ✅ Complete |
| P2: API Router | ~77 tests | +3% | ✅ Complete |
| P3: Docker Service | ~20 tests | +10% | 🔄 In Progress |
| P4: Stats Service | ~15 tests | +5% | ⏳ Pending |
| P5: Repositories | ~15 tests | +3% | ⏳ Pending |
| P6: Services | ~10 tests | +2% | ⏳ Pending |
| P7: Users API | ~25 tests | +8% | ⏳ Pending |

**Current:** 201 tests, 47% coverage (CI threshold: 45%)
**Target:** 80% coverage (+33% remaining)
**Tests needed:** ~95 additional tests

---

## Running Tests

```bash
# Run all tests with coverage
pytest --cov=app --cov-report=term-missing

# Run only unit tests
pytest tests/unit/

# Run with HTML coverage report
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Run specific test file
pytest tests/unit/test_api_auth.py -v

# Run with Makefile
make test-backend

# Check coverage only
pytest --cov=app --cov-report=term

# Run in fail-fast mode
pytest --tb=short -x
```

---

## Summary

| Metric | Value |
|--------|-------|
| Total Lines | 2,934 |
| Lines Covered | ~1,568 |
| Coverage | 47% |
| CI Threshold | 45% |
| Total Tests | 201 |
| Passing | 201 (100%) |
| Phases Complete | P1, P2 |
| Phase In Progress | P3 |
| Phases Pending | P4-P7 |
| Coverage Needed | +33% to reach 80% |

---

*Last updated: 2026-02-05*
*Note: Coverage is measured on `backend/app/` module (2,934 lines).
       CI threshold set to 45% (fail_under = 45).*
