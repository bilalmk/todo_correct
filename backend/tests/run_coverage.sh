#!/bin/bash
#
# Backend Test Coverage Runner (T053)
# Validates ≥80% overall coverage, ≥90% for auth modules
#
# Success Criteria:
# - Overall coverage ≥80%
# - Auth modules (jwks.py, deps.py, logging.py) ≥90%
#
# Usage:
#   cd backend
#   chmod +x tests/run_coverage.sh
#   ./tests/run_coverage.sh

set -e  # Exit on error

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

echo "=========================================="
echo "Backend Test Coverage Report (T053)"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! python -m pytest --version &>/dev/null; then
    echo -e "${RED}Error: pytest not installed${NC}"
    echo "Install with: uv pip install -r requirements.txt"
    exit 1
fi

# Check if pytest-cov is available
if ! python -c "import pytest_cov" &>/dev/null; then
    echo -e "${YELLOW}Warning: pytest-cov not installed${NC}"
    echo "Installing pytest-cov..."
    uv pip install pytest-cov
fi

# Run tests with coverage
echo "Running tests with coverage analysis..."
echo ""

pytest \
    --cov=src \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    --cov-report=json:coverage.json \
    --verbose \
    tests/unit/ tests/integration/

echo ""
echo "=========================================="
echo "Coverage Summary"
echo "=========================================="

# Parse coverage.json for validation
if [ -f "coverage.json" ]; then
    # Extract overall coverage percentage
    OVERALL_COVERAGE=$(python3 -c "
import json
with open('coverage.json') as f:
    data = json.load(f)
    print(f\"{data['totals']['percent_covered']:.1f}\")
    ")

    echo "Overall Coverage: ${OVERALL_COVERAGE}%"

    # Check auth module coverage
    echo ""
    echo "Critical Module Coverage:"
    echo "------------------------"

    # JWKS service
    JWKS_COV=$(python3 -c "
import json
with open('coverage.json') as f:
    data = json.load(f)
    files = data.get('files', {})
    for path, info in files.items():
        if 'jwks.py' in path:
            print(f\"{info['summary']['percent_covered']:.1f}\")
            break
    else:
        print('N/A')
    " 2>/dev/null || echo "N/A")

    echo "  - src/services/jwks.py: ${JWKS_COV}%"

    # Auth dependencies
    DEPS_COV=$(python3 -c "
import json
with open('coverage.json') as f:
    data = json.load(f)
    files = data.get('files', {})
    for path, info in files.items():
        if 'deps.py' in path:
            print(f\"{info['summary']['percent_covered']:.1f}\")
            break
    else:
        print('N/A')
    " 2>/dev/null || echo "N/A")

    echo "  - src/api/deps.py: ${DEPS_COV}%"

    # Logging
    LOGGING_COV=$(python3 -c "
import json
with open('coverage.json') as f:
    data = json.load(f)
    files = data.get('files', {})
    for path, info in files.items():
        if 'logging.py' in path or 'monitoring.py' in path:
            print(f\"{info['summary']['percent_covered']:.1f}\")
            break
    else:
        print('N/A')
    " 2>/dev/null || echo "N/A")

    echo "  - src/core/logging.py: ${LOGGING_COV}%"

    echo ""
    echo "=========================================="
    echo "Validation Results"
    echo "=========================================="

    # Validate against requirements
    PASS=true

    # Check overall coverage ≥80%
    if (( $(echo "$OVERALL_COVERAGE >= 80" | bc -l) )); then
        echo -e "${GREEN}✓ Overall coverage ${OVERALL_COVERAGE}% ≥ 80%${NC}"
    else
        echo -e "${RED}✗ Overall coverage ${OVERALL_COVERAGE}% < 80%${NC}"
        PASS=false
    fi

    # Check auth module coverage ≥90% (if available)
    if [ "$JWKS_COV" != "N/A" ]; then
        if (( $(echo "$JWKS_COV >= 90" | bc -l) )); then
            echo -e "${GREEN}✓ JWKS coverage ${JWKS_COV}% ≥ 90%${NC}"
        else
            echo -e "${RED}✗ JWKS coverage ${JWKS_COV}% < 90%${NC}"
            PASS=false
        fi
    fi

    if [ "$DEPS_COV" != "N/A" ]; then
        if (( $(echo "$DEPS_COV >= 90" | bc -l) )); then
            echo -e "${GREEN}✓ Auth deps coverage ${DEPS_COV}% ≥ 90%${NC}"
        else
            echo -e "${RED}✗ Auth deps coverage ${DEPS_COV}% < 90%${NC}"
            PASS=false
        fi
    fi

    if [ "$LOGGING_COV" != "N/A" ]; then
        if (( $(echo "$LOGGING_COV >= 90" | bc -l) )); then
            echo -e "${GREEN}✓ Logging coverage ${LOGGING_COV}% ≥ 90%${NC}"
        else
            echo -e "${RED}✗ Logging coverage ${LOGGING_COV}% < 90%${NC}"
            PASS=false
        fi
    fi

    echo ""
    echo "HTML Report: htmlcov/index.html"
    echo "JSON Report: coverage.json"
    echo ""

    if [ "$PASS" = true ]; then
        echo -e "${GREEN}=========================================="
        echo "✓ All coverage requirements met (T053)"
        echo -e "==========================================${NC}"
        exit 0
    else
        echo -e "${RED}=========================================="
        echo "✗ Coverage requirements not met (T053)"
        echo -e "==========================================${NC}"
        exit 1
    fi
else
    echo -e "${RED}Error: coverage.json not generated${NC}"
    echo "Check pytest-cov installation"
    exit 1
fi
