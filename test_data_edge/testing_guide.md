# Software Testing Guide

## Unit Testing with pytest
```python
import pytest


def test_addition():
    assert 1 + 1 == 2


def test_string():
    assert "hello".upper() == "HELLO"
```

## Fixtures
```python
@pytest.fixture
def db():
    conn = Database()
    yield conn
    conn.close()
```

## Mocking
```python
from unittest.mock import Mock


def test_service():
    mock_db = Mock()
    mock_db.query.return_value = [1, 2, 3]
    result = service.get_data(mock_db)
    assert result == [1, 2, 3]
```
