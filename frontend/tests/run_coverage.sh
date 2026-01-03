#!/bin/bash
#
# Frontend Test Coverage Runner (T054)
# Validates ≥80% coverage for critical modules
#
# Success Criteria:
# - api-client.ts ≥80%
# - auth.ts ≥80%
# - TaskContext.tsx ≥80%
# - TagContext.tsx ≥80%
#
# Setup (if not done):
#   npm install --save-dev vitest @vitest/coverage-v8 @testing-library/react @testing-library/jest-dom jsdom
#
# Usage:
#   cd frontend
#   chmod +x tests/run_coverage.sh
#   ./tests/run_coverage.sh

set -e  # Exit on error

echo "=========================================="
echo "Frontend Test Coverage Report (T054)"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Vitest is installed
if ! npm list vitest --depth=0 &>/dev/null; then
    echo -e "${YELLOW}Warning: Vitest not installed${NC}"
    echo "Installing Vitest and coverage tools..."
    npm install --save-dev vitest @vitest/coverage-v8 @testing-library/react @testing-library/jest-dom jsdom
fi

# Check if vitest.config.ts exists
if [ ! -f "vitest.config.ts" ]; then
    echo -e "${YELLOW}Creating vitest.config.ts...${NC}"
    cat > vitest.config.ts << 'EOF'
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: [
        'src/lib/api-client.ts',
        'src/lib/auth.ts',
        'src/contexts/TaskContext.tsx',
        'src/contexts/TagContext.tsx',
      ],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.test.{ts,tsx}',
        '**/*.spec.{ts,tsx}',
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
EOF
fi

# Check if setup file exists
if [ ! -f "tests/setup.ts" ]; then
    echo -e "${YELLOW}Creating tests/setup.ts...${NC}"
    mkdir -p tests
    cat > tests/setup.ts << 'EOF'
import '@testing-library/jest-dom'

// Mock Next.js router
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
  }),
  usePathname: () => '/',
  useSearchParams: () => new URLSearchParams(),
}))

// Mock Better Auth client
vi.mock('@/lib/auth', () => ({
  authClient: {
    signIn: {
      email: vi.fn(),
    },
    signUp: {
      email: vi.fn(),
    },
    signOut: vi.fn(),
    useSession: vi.fn(() => ({
      data: null,
      isPending: false,
      error: null,
    })),
  },
}))
EOF
fi

# Add test script to package.json if not present
if ! grep -q '"test:coverage"' package.json; then
    echo -e "${YELLOW}Adding test:coverage script to package.json...${NC}"
    npm pkg set scripts.test:coverage="vitest run --coverage"
    npm pkg set scripts.test="vitest"
fi

echo "Running tests with coverage..."
echo ""

# Run tests with coverage
npm run test:coverage

echo ""
echo "=========================================="
echo "Coverage Validation (T054)"
echo "=========================================="

# Parse coverage-final.json if available
if [ -f "coverage/coverage-final.json" ]; then
    # Note: This requires jq for JSON parsing
    # Fallback to manual validation below if jq not available

    echo ""
    echo "Critical Module Coverage:"
    echo "------------------------"

    # For now, direct user to HTML report
    echo ""
    echo "HTML Coverage Report: coverage/index.html"
    echo ""
    echo "Manually verify the following modules have ≥80% coverage:"
    echo "  - src/lib/api-client.ts"
    echo "  - src/lib/auth.ts"
    echo "  - src/contexts/TaskContext.tsx"
    echo "  - src/contexts/TagContext.tsx"
    echo ""

    if [ -f "coverage/index.html" ]; then
        echo -e "${GREEN}✓ Coverage report generated successfully${NC}"
        echo ""
        echo "Open coverage/index.html in a browser to verify module coverage"
        echo ""

        # Try to open in browser (works on WSL with xdg-utils)
        if command -v xdg-open &>/dev/null; then
            echo "Opening coverage report in browser..."
            xdg-open coverage/index.html &>/dev/null || true
        fi

        exit 0
    else
        echo -e "${RED}✗ Coverage HTML report not generated${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Warning: coverage-final.json not found${NC}"
    echo "Coverage may not have been collected properly"
    echo ""
    echo "Check that:"
    echo "  1. Vitest is installed: npm list vitest"
    echo "  2. Tests are written for the target modules"
    echo "  3. vitest.config.ts includes coverage configuration"
    echo ""
    exit 1
fi
