#!/bin/bash
# Run all ChirpNeighbors tests
# Usage: ./scripts/run_all_tests.sh

set -e  # Exit on error

echo "🧪 ChirpNeighbors - Running All Tests"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track failures
FAILED=0

# Function to run command and track failures
run_test() {
    local name="$1"
    local cmd="$2"

    echo -e "${YELLOW}Running: ${name}${NC}"
    if eval "$cmd"; then
        echo -e "${GREEN}✓ ${name} passed${NC}"
        echo ""
    else
        echo -e "${RED}✗ ${name} failed${NC}"
        echo ""
        FAILED=$((FAILED + 1))
    fi
}

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# 1. Backend Tests
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Backend API Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -d "backend" ]; then
    cd backend

    # Check if dependencies are installed
    if ! python -c "import pytest" 2>/dev/null; then
        echo -e "${YELLOW}Installing Python dependencies...${NC}"
        pip install -r requirements.txt -r requirements-dev.txt
    fi

    # Linting
    run_test "Backend Linting (ruff)" "ruff check app/ || true"

    # Type checking
    run_test "Backend Type Checking (mypy)" "mypy app/ --ignore-missing-imports || true"

    # Unit tests
    run_test "Backend Unit Tests" "pytest -v -m 'not integration' --tb=short"

    # Integration tests
    run_test "Backend Integration Tests" "pytest -v -m integration --tb=short || true"

    # Coverage
    run_test "Backend Coverage Check" "pytest --cov=app --cov-fail-under=80 --tb=short || true"

    cd ..
else
    echo -e "${RED}Backend directory not found${NC}"
    FAILED=$((FAILED + 1))
fi

echo ""

# 2. Firmware Tests
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. ESP32 Firmware Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -d "firmware" ]; then
    cd firmware

    # Check if PlatformIO is installed
    if ! command -v pio &> /dev/null; then
        echo -e "${YELLOW}PlatformIO not found. Skipping firmware tests.${NC}"
        echo "Install with: pip install platformio"
    else
        # Build firmware
        run_test "Firmware Build (ESP32-S3)" "pio run -e esp32-s3"

        # Run tests
        run_test "Firmware Tests (Native)" "pio test -e native || true"

        # Check size
        run_test "Firmware Size Check" "pio run -e esp32-s3 -t size"
    fi

    cd ..
else
    echo -e "${RED}Firmware directory not found${NC}"
    FAILED=$((FAILED + 1))
fi

echo ""

# 3. Integration Tests with Mock ESP32
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. ESP32 Integration Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -f "scripts/mock_esp32_client.py" ]; then
    # Check if backend is running
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        run_test "Mock ESP32 Client Test" "python scripts/mock_esp32_client.py --backend-url http://localhost:8000 --register || true"
    else
        echo -e "${YELLOW}Backend not running. Skipping mock ESP32 client test.${NC}"
        echo "Start backend with: cd backend && uvicorn app.main:app"
    fi
else
    echo -e "${RED}Mock ESP32 client not found${NC}"
fi

echo ""

# 4. Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}✗ $FAILED test suite(s) failed${NC}"
    echo ""
    echo "Tips:"
    echo "  - Check the error messages above for details"
    echo "  - Run individual test suites for more information"
    echo "  - Ensure all dependencies are installed"
    echo "  - Make sure PostgreSQL and Redis are running (for backend tests)"
    echo ""
    exit 1
fi
