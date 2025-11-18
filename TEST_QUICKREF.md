# ChirpNeighbors Testing Quick Reference

Quick commands for running tests. For detailed guide, see [TESTING_GUIDE.md](TESTING_GUIDE.md).

## Backend Tests

```bash
cd backend

# Run all tests
pytest -v

# Run with coverage
make test-coverage

# Run only unit tests
pytest -v -m "not integration"

# Run only integration tests
pytest -v -m integration

# Run specific test file
pytest -v app/tests/test_api_devices.py

# Run specific test
pytest -v app/tests/test_api_devices.py::TestDeviceRegistration::test_register_new_device

# Watch mode (re-run on changes)
pytest-watch -v

# Show slowest tests
pytest --durations=10
```

## Firmware Tests

```bash
cd firmware

# Run all tests (native, fast)
pio test -e native

# Run tests on ESP32 hardware
pio test -e test

# Run specific test
pio test -f test_beamformer

# Build firmware
pio run -e esp32-s3

# Check firmware size
pio run -e esp32-s3 -t size
```

## Integration Tests

```bash
# Mock ESP32 client
python scripts/mock_esp32_client.py --simulate

# Custom backend
python scripts/mock_esp32_client.py --backend-url http://localhost:8000 --register

# Full workflow
python scripts/mock_esp32_client.py --backend-url http://localhost:8000 --simulate --cycles 3
```

## Code Quality

```bash
cd backend

# Linting
make lint
# or
ruff check app/

# Format code
make format
# or
ruff format app/

# Type checking
mypy app/ --ignore-missing-imports

# Security check
bandit -r app/ -ll
```

## All Tests

```bash
# Run everything from project root
./scripts/run_all_tests.sh

# Or with Docker
docker-compose up -d
docker-compose exec backend pytest -v
```

## Make Commands (Backend)

```bash
make help              # Show all commands
make install           # Install dependencies
make test              # Run all tests
make test-unit         # Unit tests only
make test-integration  # Integration tests only
make test-coverage     # Tests with HTML coverage
make lint              # Run linting
make format            # Format code
make clean             # Clean generated files
make run               # Run dev server
```

## Useful Flags

```bash
# Pytest flags
-v                     # Verbose output
-s                     # Show print statements
-x                     # Stop on first failure
--lf                   # Run last failed tests
--ff                   # Run failed first
-k "test_name"         # Run tests matching pattern
-m "marker"            # Run tests with marker
--cov=app              # Measure coverage
--durations=10         # Show 10 slowest tests

# PlatformIO flags
-e native              # Native environment
-e test                # Test environment
-f test_name           # Filter specific test
-v                     # Verbose output
```

## Test Markers

```python
@pytest.mark.asyncio        # Async test
@pytest.mark.integration    # Integration test
@pytest.mark.slow           # Slow test
```

Run specific markers:
```bash
pytest -v -m integration
pytest -v -m "not slow"
```

## Coverage

```bash
# HTML report
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Terminal report
pytest --cov=app --cov-report=term-missing

# Check minimum coverage
pytest --cov=app --cov-fail-under=80
```

## CI/CD

```bash
# View in GitHub
# Go to: https://github.com/yourusername/ChirpNeighbors/actions

# Run locally with act
act push
act pull_request
act -j backend-tests
```

## Debugging

```bash
# Run test with debugger
pytest --pdb test_file.py::test_name

# Drop into debugger on failure
pytest --pdb -x

# Verbose test output
pytest -vv -s

# Show local variables on failure
pytest -l
```

## Common Issues

```bash
# Database connection
docker-compose up -d postgres

# Missing dependencies
cd backend
pip install -r requirements.txt -r requirements-dev.txt

# Clean test cache
pytest --cache-clear
rm -rf .pytest_cache

# Reset database
dropdb chirpneighbors_test
createdb chirpneighbors_test
```

## Quick Test File Template

```python
"""Tests for [component]."""

import pytest
from app.tests.factories import DeviceFactory


@pytest.mark.asyncio
async def test_something(db_session, test_client):
    """Test description."""
    # Arrange
    device = await DeviceFactory.create(db_session)

    # Act
    response = test_client.get(f"/api/v1/devices/{device.device_id}")

    # Assert
    assert response.status_code == 200
```

## Resources

- 📖 [Full Testing Guide](TESTING_GUIDE.md)
- 🔧 [Backend Tests README](backend/app/tests/README.md)
- 🛠️ [Firmware Tests README](firmware/test/README.md)
- 🤖 [CI/CD Workflows](.github/workflows/README.md)
