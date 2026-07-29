# Software Testing

Software testing evaluates and verifies that software meets requirements and works as expected.

## Testing Levels

### Unit Testing
Testing individual components or functions in isolation. Fast, reliable, and easy to maintain.

Example using pytest:
```python
def test_addition():
    assert add(2, 3) == 5


def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)
```

### Integration Testing
Testing how components work together. Verifies interfaces between modules.

### System Testing
Testing the complete, integrated system against requirements.

### Acceptance Testing
Validating the system meets business requirements, often done by end users.

## Testing Pyramid

```
    /\
   /  \        E2E Tests (slow, brittle)
  /    \
 / Unit \      Unit Tests (fast, reliable)
/________\
```

## Test Types

| Type | Purpose | Tools |
|------|---------|-------|
| Functional | Correct behavior | pytest, JUnit |
| Performance | Speed, scalability | Locust, k6 |
| Security | Vulnerabilities | OWASP ZAP |
| Regression | No new bugs | CI pipelines |
| Smoke | Basic functionality | Manual/automated |

## Python Testing Framework: pytest

pytest is the most popular testing framework for Python. Key features:
- Simple assertion-based testing
- Fixtures for test setup
- Parameterized tests
- Plugin ecosystem

### pytest Fixtures

```python
import pytest


@pytest.fixture
def db_connection():
    conn = Database.connect()
    yield conn
    conn.close()


def test_query(db_connection):
    results = db_connection.query("SELECT 1")
    assert results == [(1,)]
```

## Mocking

Mocking replaces real objects with test doubles. Python's `unittest.mock` provides:
- `Mock` — Generic mock object
- `MagicMock` — Mock with magic methods
- `patch` — Temporarily replace objects
- `AsyncMock` — Mock for async functions

## Test Coverage

Coverage measures which code is exercised by tests. Tools: `coverage.py`, `pytest-cov`.

## Continuous Integration

CI automatically runs tests on code changes. Popular platforms: GitHub Actions, GitLab CI, Jenkins.

## Test-Driven Development (TDD)

TDD cycle: Red (write failing test) → Green (make it pass) → Refactor (improve code).
