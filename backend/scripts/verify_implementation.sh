#!/bin/bash
# Implementation Verification Script for 008-chatkit-server-backend
# Based on specs/008-chatkit-server-backend/tasks.md

set -e

echo "========================================="
echo "ChatKit Backend Implementation Verification"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0
WARN=0

check_pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((PASS++))
}

check_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((FAIL++))
}

check_warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
    ((WARN++))
}

echo "=== 1. DATABASE MODELS VERIFICATION ==="
echo ""

# T005: Conversation model
if grep -q "class Conversation" src/models/conversation.py && \
   grep -q "conversation_id.*UUID" src/models/conversation.py && \
   grep -q "user_id" src/models/conversation.py && \
   grep -q "deleted_at" src/models/conversation.py; then
    check_pass "Conversation model exists with required fields (UUID, user_id, soft delete)"
else
    check_fail "Conversation model missing required fields"
fi

# T006: Message model
if grep -q "class Message" src/models/message.py && \
   grep -q "message_id.*UUID" src/models/message.py && \
   grep -q "conversation_id" src/models/message.py && \
   grep -q "role" src/models/message.py && \
   grep -q "content" src/models/message.py && \
   grep -q "is_complete" src/models/message.py; then
    check_pass "Message model exists with required fields (UUID, conversation_id, role, content, is_complete)"
else
    check_fail "Message model missing required fields"
fi

echo ""
echo "=== 2. API ENDPOINTS VERIFICATION ==="
echo ""

# T024: POST /api/chatkit/chat endpoint
if grep -q "@router.post.*chat" src/api/chatkit.py && \
   grep -q "StreamingResponse" src/api/chatkit.py; then
    check_pass "POST /api/chatkit/chat endpoint exists with streaming support"
else
    check_fail "POST /api/chatkit/chat endpoint missing or no streaming"
fi

# T025: DELETE /api/chatkit/conversation endpoint
if grep -q "@router.delete.*conversation" src/api/chatkit.py; then
    check_pass "DELETE /api/chatkit/conversation endpoint exists"
else
    check_fail "DELETE /api/chatkit/conversation endpoint missing"
fi

# T063: GET /api/chatkit/health endpoint
if grep -q "health" src/api/chatkit.py || grep -q "@router.get.*health" src/api/chatkit.py; then
    check_pass "Health check endpoint exists"
else
    check_warn "Health check endpoint not found (optional)"
fi

echo ""
echo "=== 3. CHATKIT CORE IMPLEMENTATION ==="
echo ""

# T020: CustomChatKitServer class
if grep -q "class.*ChatKitServer" src/chatkit/server.py && \
   grep -q "def respond" src/chatkit/server.py; then
    check_pass "CustomChatKitServer class exists with respond() method"
else
    check_fail "CustomChatKitServer class or respond() method missing"
fi

# T014-T016: DatabaseThreadItemStore
if grep -q "class.*ThreadItemStore" src/chatkit/store.py && \
   grep -q "load_thread_items" src/chatkit/store.py && \
   grep -q "save_thread_item" src/chatkit/store.py && \
   grep -q "delete_thread_items" src/chatkit/store.py; then
    check_pass "DatabaseThreadItemStore implements all required methods"
else
    check_fail "DatabaseThreadItemStore missing required methods"
fi

# T010-T012: MCP client and agent setup
if grep -q "mcp" src/chatkit/agent.py || grep -q "MCP" src/chatkit/agent.py; then
    check_pass "MCP client integration exists in agent.py"
else
    check_fail "MCP client integration missing in agent.py"
fi

# T013: System prompt
if grep -q "SYSTEM_PROMPT" src/chatkit/server.py; then
    check_pass "SYSTEM_PROMPT constant defined"
else
    check_fail "SYSTEM_PROMPT constant missing"
fi

echo ""
echo "=== 4. CONFIGURATION VERIFICATION ==="
echo ""

# T003: Environment variables
if grep -q "OPENAI_API_KEY" src/core/config.py && \
   grep -q "MCP_SERVER_URL" src/core/config.py && \
   grep -q "CHATKIT_MESSAGE_LIMIT" src/core/config.py; then
    check_pass "Required environment variables configured in Settings"
else
    check_fail "Missing required environment variables in Settings"
fi

# T003a: MCP_SERVER_URL validation
if grep -q "HttpUrl" src/core/config.py || grep -q "url_validator" src/core/config.py; then
    check_pass "MCP_SERVER_URL validation implemented"
else
    check_warn "MCP_SERVER_URL validation not found"
fi

# T009: Database connection pool
if grep -q "pool_size" src/core/database.py || grep -q "max_overflow" src/core/database.py; then
    check_pass "Database connection pool configured"
else
    check_warn "Database connection pool configuration not verified"
fi

echo ""
echo "=== 5. UTILITIES & ERROR HANDLING ==="
echo ""

# T011: Retry logic
if grep -q "retry" src/chatkit/utils.py; then
    check_pass "Retry logic implemented in utils.py"
else
    check_fail "Retry logic missing in utils.py"
fi

# T017: Correlation ID utilities
if grep -q "correlation" src/chatkit/utils.py || grep -q "RequestContext" src/chatkit/utils.py; then
    check_pass "Correlation ID utilities implemented"
else
    check_fail "Correlation ID utilities missing"
fi

echo ""
echo "=== 6. TEST COVERAGE VERIFICATION ==="
echo ""

# Unit tests
if [ -f "tests/unit/test_chatkit_server.py" ] && \
   [ -f "tests/unit/test_chatkit_store.py" ] && \
   [ -f "tests/unit/test_chatkit_utils.py" ]; then
    check_pass "All unit test files exist (server, store, utils)"
else
    check_fail "Missing unit test files"
fi

# Integration tests
if [ -f "tests/integration/test_chatkit_api.py" ] && \
   [ -f "tests/integration/test_chatkit_persistence.py" ] && \
   [ -f "tests/integration/test_chatkit_logging.py" ]; then
    check_pass "All integration test files exist (api, persistence, logging)"
else
    check_fail "Missing integration test files"
fi

# E2E tests
if [ -f "tests/e2e/test_chatkit_workflow.py" ] && \
   [ -f "tests/e2e/test_chatkit_edge_cases.py" ]; then
    check_pass "All E2E test files exist (workflow, edge cases)"
else
    check_fail "Missing E2E test files"
fi

# T056: FR-007 (20-message limit test)
if grep -q "20.*message" tests/integration/test_chatkit_persistence.py || \
   grep -q "CHATKIT_HISTORY_LIMIT" tests/integration/test_chatkit_persistence.py; then
    check_pass "FR-007: 20-message history limit test exists"
else
    check_warn "FR-007: 20-message limit test not verified"
fi

# T057: FR-024 (message truncation test)
if grep -q "10000" tests/integration/test_chatkit_message_truncation.py || \
   grep -q "truncat" tests/integration/test_chatkit_message_truncation.py; then
    check_pass "FR-024: Message truncation test exists"
else
    check_warn "FR-024: Message truncation test not verified"
fi

echo ""
echo "=== 7. DATABASE MIGRATIONS ==="
echo ""

# T007: Alembic migration exists
if ls alembic/versions/*chatkit*.py 2>/dev/null | grep -q .; then
    check_pass "Alembic migration for ChatKit tables exists"
else
    check_fail "Alembic migration for ChatKit tables missing"
fi

echo ""
echo "=== 8. DOCUMENTATION ==="
echo ""

# T060: API documentation
if grep -q '"""' backend/src/api/chatkit.py || grep -q "docstring" backend/src/api/chatkit.py; then
    check_pass "API documentation (docstrings) present"
else
    check_warn "API documentation might be missing"
fi

# T061: README updated
if grep -q -i "chatkit" README.md; then
    check_pass "README.md mentions ChatKit setup"
else
    check_warn "README.md may need ChatKit documentation"
fi

# Quickstart guide
if [ -f "specs/008-chatkit-server-backend/quickstart.md" ]; then
    check_pass "Quickstart guide exists"
else
    check_warn "Quickstart guide missing"
fi

echo ""
echo "========================================="
echo "VERIFICATION SUMMARY"
echo "========================================="
echo -e "${GREEN}Passed:${NC} $PASS"
echo -e "${YELLOW}Warnings:${NC} $WARN"
echo -e "${RED}Failed:${NC} $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    echo "Proceed to Step 4: Run Tests"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Review implementation.${NC}"
    exit 1
fi
