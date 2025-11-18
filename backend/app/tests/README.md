# Backend Tests

This directory contains all tests for the ChirpNeighbors backend API.

## Quick Start

```bash
# Run all tests
pytest -v

# Run with coverage
pytest -v --cov=app --cov-report=html

# Run specific test file
pytest -v test_api_devices.py
```

## Test Files

### Core Tests
- `test_main.py` - Application-level tests (health checks, docs)
- `test_models.py` - Database model tests

### API Endpoint Tests
- `test_api_devices.py` - Device management endpoints
- `test_audio_upload.py` - Audio upload and processing endpoints
- `test_api_birds.py` - Bird identification endpoints (if exists)

### Integration Tests
- `test_integration_esp32.py` - Full ESP32 device workflow tests

### Test Infrastructure
- `conftest.py` - Pytest fixtures and configuration
- `factories.py` - Test data factories

## Test Structure

Each test file follows this pattern:

```python
"""Tests for [component name]."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.factories import DeviceFactory


class TestComponentName:
    """Tests for specific component."""

    def test_something(self, test_client: TestClient) -> None:
        """Test description."""
        # Arrange
        payload = {...}

        # Act
        response = test_client.post("/api/v1/endpoint", json=payload)

        # Assert
        assert response.status_code == 200
```

## Fixtures

Available fixtures (from `conftest.py`):

- `db_session` - Async database session for tests
- `test_client` - FastAPI TestClient for making requests
- `async_client` - Async HTTP client
- `temp_storage_dir` - Temporary directory for file storage

## Factories

Use factories to create test data:

```python
from app.tests.factories import DeviceFactory, AudioRecordingFactory

# Create test device
device = await DeviceFactory.create(db_session, device_id="CHIRP-TEST")

# Create test audio recording
recording = await AudioRecordingFactory.create(db_session, device=device)
```

## Test Markers

- `@pytest.mark.asyncio` - Async tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow-running tests

Run specific markers:
```bash
pytest -v -m integration
pytest -v -m "not slow"
```

## Coverage

Generate coverage report:
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

Current coverage goal: **>80%**

## Writing New Tests

1. Create test file: `test_[component].py`
2. Import necessary fixtures and factories
3. Create test classes for logical grouping
4. Write individual test functions
5. Use AAA pattern (Arrange, Act, Assert)
6. Add docstrings
7. Run tests and verify coverage

Example:
```python
@pytest.mark.asyncio
async def test_new_feature(db_session: AsyncSession, test_client: TestClient) -> None:
    """Test that new feature works correctly."""
    # Arrange
    device = await DeviceFactory.create(db_session)

    # Act
    response = test_client.get(f"/api/v1/devices/{device.device_id}")

    # Assert
    assert response.status_code == 200
    assert response.json()["device_id"] == device.device_id
```

## Running Tests in CI/CD

Tests run automatically on every push via GitHub Actions. See `.github/workflows/tests.yml` for configuration.

## Troubleshooting

### Database Connection Issues
Ensure PostgreSQL is running:
```bash
docker-compose up -d postgres
```

### Import Errors
Ensure dependencies are installed:
```bash
pip install -r requirements.txt -r requirements-dev.txt
```

### Slow Tests
Run with warnings about slow tests:
```bash
pytest --durations=10
```

## Resources

- [Full Testing Guide](/TESTING_GUIDE.md)
- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
