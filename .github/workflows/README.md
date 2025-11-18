# GitHub Actions Workflows

This directory contains CI/CD workflows for automated testing and deployment.

## Workflows

### 1. `tests.yml` - Main Test Suite

Runs on every push and pull request to `main` and `develop` branches.

**Jobs:**
- **backend-tests** - Backend API tests with PostgreSQL and Redis
  - Linting (ruff)
  - Type checking (mypy)
  - Unit tests
  - Coverage reporting (requires >80%)

- **integration-tests** - End-to-end ESP32 workflow tests
  - Device registration
  - Audio upload
  - Mock ESP32 client simulation

- **firmware-tests** - ESP32 firmware tests
  - Build verification
  - Native unit tests
  - Firmware size check

- **code-quality** - Code quality checks
  - Ruff linting and formatting
  - Security scanning (Bandit)

- **docker-build** - Docker image build test
  - Backend Docker image
  - Basic smoke test

- **test-summary** - Final summary
  - Aggregates all test results
  - Fails if any test fails

### 2. `pre-commit.yml` - Pre-commit Hooks

Runs pre-commit hooks on all files to ensure code quality before merge.

**Checks:**
- Code formatting
- Import sorting
- Trailing whitespace
- YAML/JSON validation
- File size limits

## Configuration

### Required Secrets

No secrets required for basic tests. Optional secrets for advanced features:

- `CODECOV_TOKEN` - For coverage reporting to Codecov (optional)

### Environment Variables

Tests use these environment variables:

```yaml
TEST_DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/chirpneighbors_test
REDIS_URL: redis://localhost:6379/0
ENVIRONMENT: testing
```

## Running Locally

Simulate CI/CD locally using [act](https://github.com/nektos/act):

```bash
# Install act
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run workflows
act push                    # Simulate push event
act pull_request           # Simulate PR event
act -j backend-tests       # Run specific job
```

## Workflow Triggers

### Push to Main/Develop
- Runs all tests
- Reports coverage
- Updates status checks

### Pull Request
- Runs all tests
- Posts coverage report as PR comment
- Blocks merge if tests fail

### Manual Trigger
```bash
# Trigger via GitHub UI or CLI
gh workflow run tests.yml
```

## Status Badges

Add to README:

```markdown
![Tests](https://github.com/yourusername/ChirpNeighbors/workflows/Tests/badge.svg)
[![codecov](https://codecov.io/gh/yourusername/ChirpNeighbors/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/ChirpNeighbors)
```

## Caching

Workflows cache dependencies to speed up builds:

- Python packages (`~/.cache/pip`)
- PlatformIO libraries (`~/.platformio`)
- Pre-commit hooks (`~/.cache/pre-commit`)

## Debugging

### View Logs
- Go to "Actions" tab on GitHub
- Click on workflow run
- Click on failed job
- Expand failed step

### Run Specific Job Locally
```bash
act -j backend-tests --verbose
```

### Debug Mode
Add this to workflow for debug logs:
```yaml
- name: Setup debugging
  run: |
    echo "ACTIONS_STEP_DEBUG=true" >> $GITHUB_ENV
```

## Optimization

### Parallel Execution
Jobs run in parallel when possible:
- Backend tests
- Firmware tests
- Code quality checks

### Conditional Execution
Some jobs only run when relevant files change:
```yaml
paths:
  - 'backend/**'
  - 'firmware/**'
```

### Matrix Builds
Test multiple Python versions (if needed):
```yaml
strategy:
  matrix:
    python-version: [3.10, 3.11, 3.12]
```

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Act - Local Testing](https://github.com/nektos/act)
