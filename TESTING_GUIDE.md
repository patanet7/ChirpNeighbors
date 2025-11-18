# ChirpNeighbors Testing Guide

Comprehensive guide for testing the ChirpNeighbors bird sound identification system.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Backend API Tests](#backend-api-tests)
- [Integration Tests](#integration-tests)
- [Firmware Tests](#firmware-tests)
- [Running Tests](#running-tests)
- [CI/CD Pipeline](#cicd-pipeline)
- [Coverage Goals](#coverage-goals)
- [Writing New Tests](#writing-new-tests)
- [Troubleshooting](#troubleshooting)

## Overview

The ChirpNeighbors project has three main testing layers:

1. **Backend API Tests** - FastAPI endpoint and database tests (Python/pytest)
2. **Integration Tests** - End-to-end ESP32 to backend workflow tests
3. **Firmware Tests** - ESP32 firmware unit tests (C++/Unity)

### Test Coverage Goals

- **Backend**: >80% code coverage
- **Integration**: All critical user flows
- **Firmware**: Core audio processing and API communication

## Test Structure

```
ChirpNeighbors/
├── backend/
│   ├── app/
│   │   └── tests/
│   │       ├── conftest.py           # Test fixtures and configuration
│   │       ├── factories.py          # Test data factories
│   │       ├── test_main.py          # App-level tests
│   │       ├── test_api_devices.py   # Device endpoint tests
│   │       ├── test_audio_upload.py  # Audio upload tests
│   │       ├── test_models.py        # Database model tests
│   │       └── test_integration_esp32.py  # ESP32 integration tests
│   ├── pytest.ini                    # Pytest configuration
│   └── Makefile                      # Quick test commands
├── firmware/
│   └── test/
│       ├── test_beamformer.cpp       # Beamforming tests
│       ├── test_audio_capture.cpp    # Audio capture tests
│       └── test_api_client.cpp       # API client tests
├── scripts/
│   └── mock_esp32_client.py          # Mock ESP32 for integration testing
└── .github/
    └── workflows/
        ├── tests.yml                 # Main CI/CD test workflow
        └── pre-commit.yml            # Pre-commit checks
```

## Backend API Tests

### Quick Start

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Run all tests
pytest -v

# Run with coverage
pytest -v --cov=app --cov-report=html

# Run specific test file
pytest -v app/tests/test_api_devices.py

# Run specific test
pytest -v app/tests/test_api_devices.py::TestDeviceRegistration::test_register_new_device
```

### Using Make Commands

```bash
make test              # Run all tests
make test-unit         # Run unit tests only
make test-integration  # Run integration tests only
make test-coverage     # Run tests with HTML coverage report
make lint              # Run linting
make format            # Format code
```

### Test Categories

#### 1. Unit Tests

Test individual components in isolation:

```python
# Example: Testing device model
@pytest.mark.asyncio
async def test_create_device(db_session: AsyncSession) -> None:
    device = Device(
        device_id="CHIRP-TEST123",
        firmware_version="1.0.0",
        model="ReSpeaker-Lite",
    )
    db_session.add(device)
    await db_session.commit()

    assert device.id is not None
```

#### 2. API Tests

Test API endpoints:

```python
def test_register_device(test_client: TestClient) -> None:
    payload = {
        "device_id": "CHIRP-TEST001",
        "firmware_version": "1.0.0",
        "model": "ReSpeaker-Lite",
    }
    response = test_client.post("/api/v1/devices/register", json=payload)
    assert response.status_code == 201
```

#### 3. Database Tests

Test database models and relationships:

```python
@pytest.mark.asyncio
async def test_device_relationships(db_session: AsyncSession) -> None:
    device = await DeviceFactory.create(db_session)
    recording = await AudioRecordingFactory.create(db_session, device=device)

    await db_session.refresh(device)
    assert len(device.audio_recordings) == 1
```

### Test Fixtures

Common fixtures available in `conftest.py`:

- `db_session` - Database session for tests
- `test_client` - FastAPI test client
- `async_client` - Async HTTP client
- `temp_storage_dir` - Temporary file storage

### Test Factories

Use factories to create test data easily:

```python
from app.tests.factories import DeviceFactory, AudioRecordingFactory

# Create a device
device = await DeviceFactory.create(db_session, device_id="CHIRP-TEST")

# Create an audio recording
recording = await AudioRecordingFactory.create(db_session, device=device)

# Create a bird identification
identification = await BirdIdentificationFactory.create(
    db_session,
    audio_recording=recording,
    common_name="American Crow"
)
```

## Integration Tests

Integration tests simulate the complete ESP32 device workflow using the mock ESP32 client.

### Running Integration Tests

```bash
# Run all integration tests
pytest -v -m integration app/tests/test_integration_esp32.py

# Run specific integration test
pytest -v app/tests/test_integration_esp32.py::TestESP32Integration::test_full_device_workflow
```

### Using Mock ESP32 Client

The mock ESP32 client simulates device behavior:

```bash
# Register device
python scripts/mock_esp32_client.py --register

# Send heartbeat
python scripts/mock_esp32_client.py --heartbeat

# Upload audio
python scripts/mock_esp32_client.py --upload

# Full simulation (3 cycles)
python scripts/mock_esp32_client.py --simulate --cycles 3

# Custom backend URL
python scripts/mock_esp32_client.py --backend-url http://localhost:8000 --simulate
```

### Integration Test Example

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_device_workflow(test_client, db_session: AsyncSession) -> None:
    """Test complete ESP32 workflow: register -> heartbeat -> upload"""

    # 1. Register device
    response = await client.post("/api/v1/devices/register", json=payload)
    assert response.status_code == 201

    # 2. Send heartbeat
    response = await client.post(f"/api/v1/devices/{device_id}/heartbeat", ...)
    assert response.status_code == 200

    # 3. Upload audio
    response = await client.post("/api/v1/audio/upload", files=files, data=data)
    assert response.status_code == 201
```

## Firmware Tests

ESP32 firmware tests use PlatformIO and the Unity testing framework.

### Running Firmware Tests

```bash
# Navigate to firmware directory
cd firmware

# Run all tests (native environment)
pio test -e native

# Run all tests (on ESP32 hardware)
pio test -e test

# Run specific test
pio test -f test_beamformer

# Run with verbose output
pio test -v
```

### Test Environments

- **native** - Native environment (no hardware, faster)
- **test** - ESP32 hardware environment (requires connected device)
- **esp32-s3** - Build for ESP32-S3 (for manual testing)

### Writing Firmware Tests

Example test structure:

```cpp
#include <unity.h>
#include "../include/Beamformer.h"

Beamformer* beamformer = nullptr;

void setUp(void) {
    beamformer = new Beamformer();
}

void tearDown(void) {
    delete beamformer;
}

void test_beamformer_init(void) {
    bool result = beamformer->begin();
    TEST_ASSERT_TRUE(result);
}

void setup() {
    delay(2000);
    UNITY_BEGIN();
    RUN_TEST(test_beamformer_init);
    UNITY_END();
}

void loop() {}
```

### Common Assertions

```cpp
TEST_ASSERT_TRUE(condition)
TEST_ASSERT_FALSE(condition)
TEST_ASSERT_EQUAL(expected, actual)
TEST_ASSERT_NOT_NULL(pointer)
TEST_ASSERT_GREATER_THAN(threshold, actual)
TEST_ASSERT_FLOAT_WITHIN(delta, expected, actual)
```

## Running Tests

### Local Development

#### Backend Tests

```bash
# Quick test run
cd backend
pytest -v

# With coverage
pytest -v --cov=app --cov-report=html
open htmlcov/index.html

# Watch mode (auto re-run on changes)
pytest-watch -v

# Specific markers
pytest -v -m "not integration"  # Skip integration tests
pytest -v -m integration         # Only integration tests
```

#### Firmware Tests

```bash
cd firmware

# Native tests (fast, no hardware)
pio test -e native

# Hardware tests (requires ESP32)
pio test -e test

# Build and check size
pio run -e esp32-s3 -t size
```

### Docker Environment

```bash
# Start services
docker-compose up -d

# Run backend tests in container
docker-compose exec backend pytest -v

# Run with coverage
docker-compose exec backend pytest -v --cov=app
```

## CI/CD Pipeline

Tests run automatically on every push and pull request via GitHub Actions.

### Workflow Overview

1. **Backend Tests**
   - Linting (ruff)
   - Type checking (mypy)
   - Unit tests
   - Coverage reporting (>80% required)

2. **Integration Tests**
   - Full ESP32 workflow simulation
   - Database integration

3. **Firmware Tests**
   - Build verification
   - Native unit tests
   - Firmware size check

4. **Code Quality**
   - Security checks (bandit)
   - Code formatting
   - Pre-commit hooks

5. **Docker Build**
   - Backend image build test

### Viewing Test Results

- **GitHub**: Check the "Actions" tab on your repository
- **Coverage**: View coverage reports in PR comments
- **Codecov**: Detailed coverage analysis at codecov.io

### Required Checks

All these checks must pass before merging:
- ✅ Backend tests (>80% coverage)
- ✅ Integration tests
- ✅ Firmware build
- ✅ Code quality checks
- ✅ Docker build

## Coverage Goals

### Current Coverage Targets

| Component | Target | Current |
|-----------|--------|---------|
| Backend API | 80% | TBD |
| Database Models | 90% | TBD |
| Integration | 100% critical flows | TBD |
| Firmware | 70% | TBD |

### Viewing Coverage

```bash
# Generate HTML coverage report
cd backend
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Terminal coverage report
pytest --cov=app --cov-report=term-missing

# XML for CI/CD
pytest --cov=app --cov-report=xml
```

### Coverage Exclusions

Some code is excluded from coverage requirements:
- Configuration files
- Migration scripts
- Development utilities
- Type stubs

## Writing New Tests

### Backend Test Checklist

When adding a new API endpoint:

1. ✅ Test successful request
2. ✅ Test validation errors (400)
3. ✅ Test not found errors (404)
4. ✅ Test authentication/authorization
5. ✅ Test database side effects
6. ✅ Test edge cases (empty, null, large data)

### Test Naming Convention

```python
# Good test names
def test_register_device_success()
def test_register_device_missing_fields()
def test_register_device_duplicate_id()

# Bad test names
def test_register()
def test_1()
def test_device()
```

### Test Structure (AAA Pattern)

```python
def test_something():
    # Arrange - Set up test data
    device = DeviceFactory.create(...)

    # Act - Perform the action
    response = test_client.post("/api/v1/devices/register", json=payload)

    # Assert - Verify results
    assert response.status_code == 201
    assert response.json()["device_id"] == "CHIRP-TEST"
```

### Using Markers

Mark tests for organization:

```python
@pytest.mark.asyncio
async def test_async_function():
    ...

@pytest.mark.integration
def test_integration_workflow():
    ...

@pytest.mark.slow
def test_long_running():
    ...
```

Run specific markers:
```bash
pytest -v -m integration
pytest -v -m "not slow"
```

## Troubleshooting

### Common Issues

#### Database Connection Errors

```bash
# Ensure PostgreSQL is running
docker-compose up -d postgres

# Check connection
psql -h localhost -U postgres -d chirpneighbors_test

# Reset test database
dropdb chirpneighbors_test
createdb chirpneighbors_test
```

#### Import Errors

```bash
# Ensure you're in the correct directory
cd backend

# Reinstall dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Set PYTHONPATH if needed
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Fixture Not Found

```bash
# Check conftest.py is in the right place
ls app/tests/conftest.py

# Run pytest with verbose import
pytest -v --import-mode=importlib
```

#### Firmware Test Failures

```bash
# Clean and rebuild
cd firmware
pio run --target clean
pio test -e native

# Check serial monitor
pio device monitor

# Update PlatformIO
pio upgrade
```

### Getting Help

- **Documentation**: Check inline test documentation
- **Examples**: Look at existing tests in `app/tests/`
- **CI Logs**: Review GitHub Actions logs for detailed errors
- **Community**: Ask in project discussions or issues

## Best Practices

### Do's

- ✅ Write tests before fixing bugs
- ✅ Use factories for test data
- ✅ Keep tests independent and isolated
- ✅ Test one thing per test
- ✅ Use descriptive test names
- ✅ Mock external dependencies
- ✅ Clean up after tests (fixtures handle this)

### Don'ts

- ❌ Don't test implementation details
- ❌ Don't share state between tests
- ❌ Don't skip tests without good reason
- ❌ Don't ignore failing tests
- ❌ Don't commit without running tests
- ❌ Don't test third-party libraries

## Performance

### Test Speed Optimization

```bash
# Run tests in parallel (faster)
pytest -v -n auto

# Run only failed tests from last run
pytest --lf

# Run tests that failed first
pytest --ff

# Stop on first failure
pytest -x
```

### Measuring Test Performance

```bash
# Show slowest tests
pytest --durations=10

# Profile tests
pytest --profile
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [PlatformIO Testing](https://docs.platformio.org/en/latest/advanced/unit-testing/)
- [Unity Testing Framework](https://github.com/ThrowTheSwitch/Unity)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html)

## Quick Reference

### Common Commands

```bash
# Backend
cd backend
make test              # Run all tests
make test-coverage     # With HTML coverage
make lint              # Run linting
make format            # Format code

# Firmware
cd firmware
pio test -e native     # Run tests
pio run -e esp32-s3    # Build for ESP32-S3

# Integration
python scripts/mock_esp32_client.py --simulate

# CI/CD
git push               # Triggers all tests
```

### Environment Variables

```bash
# Backend testing
export TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/chirpneighbors_test"
export ENVIRONMENT="testing"
export DEBUG="false"

# Firmware testing
export PLATFORMIO_UPLOAD_PORT="/dev/ttyUSB0"
```

---

**Happy Testing!** 🧪🐦

For questions or issues, please open a GitHub issue or check the project documentation.
