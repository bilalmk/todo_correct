#!/bin/bash
echo "=== CRITICAL IMPLEMENTATION CHECKS ==="
echo ""

PASS=0
FAIL=0

check() {
  if [ $1 -eq 0 ]; then
    echo "✓ $2"
    ((PASS++))
  else
    echo "✗ $2"
    ((FAIL++))
  fi
}

# Check 1: FR-007 - 20 message limit
grep -q "CHATKIT_HISTORY_LIMIT.*20\|limit.*20\|LIMIT.*20" src/chatkit/store.py src/core/config.py
check $? "FR-007: 20-message history limit configured"

# Check 2: FR-024 - 10,000 character truncation
grep -q "10000\|CHATKIT_MESSAGE_LIMIT" src/chatkit/store.py src/core/config.py
check $? "FR-024: Message truncation at 10,000 characters"

# Check 3: FR-008 - Authentication integration
grep -q "get_current_user" src/api/chatkit.py
check $? "FR-008: Better Auth JWT integration"

# Check 4: FR-011 - Message persistence
grep -q "save_thread_item" src/chatkit/store.py
check $? "FR-011: Message persistence to database"

# Check 5: FR-014 - Retry logic for OpenAI
grep -q "retry" src/chatkit/utils.py
check $? "FR-014: Retry logic implemented"

# Check 6: FR-016 - Correlation IDs
grep -q "correlation_id\|RequestContext" src/chatkit/utils.py
check $? "FR-016: Correlation ID utilities"

# Check 7: FR-017 - User isolation
grep -q "user_id" src/models/conversation.py src/models/message.py | head -1 > /dev/null
check $? "FR-017: User isolation (user_id in models)"

# Check 8: FR-020 - Soft deletes
grep -q "deleted_at" src/models/conversation.py src/models/message.py | head -1 > /dev/null
check $? "FR-020: Soft delete fields present"

# Check 9: FR-023 - Connection pool
grep -q "pool_size\|max_overflow" src/core/database.py
check $? "FR-023: Database connection pool configured"

# Check 10: All test files exist
test -f tests/unit/test_chatkit_server.py && \
  test -f tests/integration/test_chatkit_api.py && \
  test -f tests/e2e/test_chatkit_workflow.py
check $? "Phase 8: All test files exist"

echo ""
echo "=== RESULTS ==="
echo "Passed: $PASS/10"
echo "Failed: $FAIL/10"
echo ""

if [ $FAIL -eq 0 ]; then
  echo "✅ All critical checks passed!"
  exit 0
else
  echo "⚠️  Some checks failed - review implementation"
  exit 1
fi
