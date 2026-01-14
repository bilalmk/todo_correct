# Implementation Verification Guide
## Feature: 008-chatkit-server-backend

**Purpose**: Verify that all tasks are implemented correctly and meet specification requirements.
**Last Updated**: 2026-01-14

---

## Quick Status Check

Run these commands to get an overview:

```bash
# Task completion status
grep -E "^\- \[X\]" specs/008-chatkit-server-backend/tasks.md | wc -l  # Should be 76
grep -E "^\- \[ \]" specs/008-chatkit-server-backend/tasks.md | wc -l  # Should be 0

# File structure verification
find backend/src/chatkit backend/src/models/conversation.py backend/src/models/message.py backend/src/api/chatkit.py -type f 2>/dev/null | wc -l  # Should be 9+

# Test files verification
find backend/tests -name "*chatkit*" -type f | wc -l  # Should be 9
```

---

## Verification Approach

### Level 1: Specification Compliance ✅
**What**: Verify all requirements from spec.md are addressed
**How**: Manual checklist against spec.md

### Level 2: Code Structure ✅
**What**: Verify all files, classes, and functions exist
**How**: Grep/find commands

### Level 3: Test Execution ✅
**What**: Run automated tests to verify functionality
**How**: pytest commands

### Level 4: Functional Testing ✅
**What**: End-to-end manual testing via API
**How**: curl/httpie commands

### Level 5: Constitutional Compliance ✅
**What**: Verify adherence to CLAUDE.md principles
**How**: Architecture review

---

## Level 1: Specification Compliance

### Functional Requirements (spec.md)

**Reference**: `specs/008-chatkit-server-backend/spec.md`

#### Core Requirements

- [ ] **FR-001**: ChatKit server responds to streaming chat messages
  ```bash
  grep -n "def respond" backend/src/chatkit/server.py
  grep -n "AsyncIterator\|StreamingResponse" backend/src/chatkit/server.py backend/src/api/chatkit.py
  ```

- [ ] **FR-002**: Natural language task creation via chatbot
  ```bash
  grep -n "add_task" backend/src/chatkit/agent.py backend/src/chatkit/server.py
  ```

- [ ] **FR-003**: Natural language task listing with filters
  ```bash
  grep -n "list_tasks" backend/src/chatkit/agent.py backend/src/chatkit/server.py
  ```

- [ ] **FR-004**: Natural language task completion
  ```bash
  grep -n "complete_task" backend/src/chatkit/agent.py backend/src/chatkit/server.py
  ```

- [ ] **FR-005**: Natural language task updates
  ```bash
  grep -n "update_task" backend/src/chatkit/agent.py backend/src/chatkit/server.py
  ```

- [ ] **FR-006**: Natural language task deletion
  ```bash
  grep -n "delete_task" backend/src/chatkit/agent.py backend/src/chatkit/server.py
  ```

- [ ] **FR-007**: Conversation history limited to 20 messages
  ```bash
  grep -n "20\|CHATKIT_HISTORY_LIMIT" backend/src/chatkit/store.py backend/src/core/config.py
  # Test: backend/tests/integration/test_chatkit_persistence.py (T056)
  ```

- [ ] **FR-008**: Integration with existing authentication (Better Auth JWT)
  ```bash
  grep -n "get_current_user" backend/src/api/chatkit.py
  grep -n "Depends.*get_current_user" backend/src/api/chatkit.py
  ```

- [ ] **FR-009**: Integration with existing MCP server
  ```bash
  grep -n "MCP_SERVER_URL\|mcp.*client" backend/src/chatkit/agent.py backend/src/core/config.py
  ```

- [ ] **FR-010**: Integration with OpenAI Agents SDK
  ```bash
  grep -n "Agent\|openai" backend/src/chatkit/agent.py
  grep -r "openai" backend/requirements.txt
  ```

- [ ] **FR-011**: Message persistence to database
  ```bash
  grep -n "save_thread_item\|Message" backend/src/chatkit/store.py
  ```

- [ ] **FR-012**: Conversation persistence to database
  ```bash
  grep -n "Conversation\|conversation_id" backend/src/models/conversation.py backend/src/chatkit/server.py
  ```

- [ ] **FR-013**: MCP server URL validation
  ```bash
  grep -n "HttpUrl\|MCP_SERVER_URL" backend/src/core/config.py
  # Test: T003a
  ```

- [ ] **FR-014**: Retry logic for OpenAI API failures
  ```bash
  grep -n "retry.*exponential\|@retry" backend/src/chatkit/utils.py
  # Test: T051 (unit test)
  ```

- [ ] **FR-015**: Retry logic for database operations
  ```bash
  grep -n "retry_database" backend/src/chatkit/utils.py
  # Test: T051 (unit test)
  ```

- [ ] **FR-016**: Structured logging with correlation IDs
  ```bash
  grep -n "correlation_id\|RequestContext" backend/src/chatkit/utils.py backend/src/chatkit/server.py
  # Test: T058 (logging audit test)
  ```

- [ ] **FR-017**: User isolation (all operations scoped to authenticated user)
  ```bash
  grep -n "user_id" backend/src/models/conversation.py backend/src/models/message.py
  # Test: T066 (security audit)
  ```

- [ ] **FR-018**: Error handling for MCP connection failures
  ```bash
  grep -n "except.*MCP\|ConnectError\|httpx" backend/src/chatkit/agent.py backend/src/chatkit/utils.py
  ```

- [ ] **FR-019**: Error handling for database failures
  ```bash
  grep -n "except.*OperationalError\|DBAPIError" backend/src/chatkit/utils.py
  ```

- [ ] **FR-020**: Soft delete for conversations and messages
  ```bash
  grep -n "deleted_at" backend/src/models/conversation.py backend/src/models/message.py
  # Test: T016, T025, T053
  ```

- [ ] **FR-021**: System prompt with AI assistant instructions
  ```bash
  grep -n "SYSTEM_PROMPT" backend/src/chatkit/server.py
  # Verify: contains role, tools list, response style, user isolation reminder
  ```

- [ ] **FR-022**: Handle streaming interruptions gracefully
  ```bash
  grep -n "is_complete" backend/src/models/message.py backend/src/chatkit/store.py
  # Test: Additional test case in tasks.md Phase 8
  ```

- [ ] **FR-023**: Database connection pool configuration
  ```bash
  grep -n "pool_size\|max_overflow\|pool_timeout\|pool_pre_ping" backend/src/core/database.py
  # Test: T059 (database config test)
  ```

- [ ] **FR-024**: Message content truncation at 10,000 characters
  ```bash
  grep -n "10000\|truncat" backend/src/chatkit/store.py
  # Test: T057 (truncation test)
  ```

### Success Criteria (spec.md)

- [ ] **SC-001**: Response time < 3 seconds for typical messages
  - **Test**: Manual timing with curl or integration tests with timing assertions

- [ ] **SC-002**: Stateless server (restart test passes)
  - **Test**: T028, T054 (persistence tests verify stateless)
  ```bash
  # Manual test: Send message, restart server, verify history loads
  ```

- [ ] **SC-003**: Support 50 concurrent requests
  - **Test**: Load testing (not in tasks.md, requires separate tool)
  - **Verification**: FR-023 connection pool config supports this

- [ ] **SC-004**: Conversation history persists across sessions
  - **Test**: T054 (persistence integration test)

- [ ] **SC-005**: All 5 MCP operations work (add/list/complete/update/delete)
  - **Test**: T029-T047 (user story tests verify all operations)

- [ ] **SC-006**: 100% logging coverage with correlation IDs
  - **Test**: T058 (logging audit test)

---

## Level 2: Code Structure Verification

### Database Models (Phase 2: T005-T007)

**Conversation Model** (`backend/src/models/conversation.py`):
```bash
# Verify required fields
grep -E "conversation_id|user_id|created_at|updated_at|deleted_at" backend/src/models/conversation.py

# Verify UUID primary key
grep "UUID" backend/src/models/conversation.py

# Verify soft delete
grep "deleted_at.*Optional\|deleted_at:.*datetime" backend/src/models/conversation.py
```

**Message Model** (`backend/src/models/message.py`):
```bash
# Verify required fields
grep -E "message_id|conversation_id|user_id|role|content|is_complete|created_at|deleted_at" backend/src/models/message.py

# Verify role enum/constraint
grep -E "role.*Enum|role.*Literal|role:.*str.*=.*Field" backend/src/models/message.py

# Verify content length constraint
grep -E "max_length.*10000|content:.*str.*Field.*max_length" backend/src/models/message.py

# Verify is_complete flag
grep "is_complete.*bool" backend/src/models/message.py
```

### Database Migration (Phase 2: T007-T008)

```bash
# Find ChatKit migration file
ls -1 backend/alembic/versions/*chatkit*.py

# Verify migration creates both tables
grep -E "create_table.*conversations|create_table.*messages" backend/alembic/versions/*chatkit*.py

# Verify indexes and constraints
grep -E "create_index|ForeignKey|UniqueConstraint" backend/alembic/versions/*chatkit*.py
```

### Configuration (Phase 1: T003, T003a, T009)

```bash
# Verify environment variables in Settings
grep -E "OPENAI_API_KEY|MCP_SERVER_URL|OPENAI_MODEL|CHATKIT_MESSAGE_LIMIT|CHATKIT_HISTORY_LIMIT" backend/src/core/config.py

# Verify MCP_SERVER_URL validation (T003a)
grep -E "HttpUrl|url_validator|@validator.*MCP_SERVER_URL" backend/src/core/config.py

# Verify database connection pool config (T009)
grep -E "pool_size|max_overflow|pool_timeout|pool_pre_ping" backend/src/core/database.py
```

### ChatKit Core Implementation (Phase 2-3: T010-T027)

**MCP Client** (`backend/src/chatkit/agent.py`):
```bash
# Verify MCP client initialization (T010)
grep -n "def create_mcp_client\|MCPClient\|httpx" backend/src/chatkit/agent.py

# Verify agent creation with MCP tools (T012)
grep -n "def create_agent\|Agent.*mcp\|list_tools" backend/src/chatkit/agent.py
```

**CustomChatKitServer** (`backend/src/chatkit/server.py`):
```bash
# Verify class definition (T020)
grep -n "class.*ChatKitServer" backend/src/chatkit/server.py

# Verify respond() method (T021)
grep -n "async def respond" backend/src/chatkit/server.py

# Verify system prompt (T013)
grep -n "SYSTEM_PROMPT" backend/src/chatkit/server.py
```

**DatabaseThreadItemStore** (`backend/src/chatkit/store.py`):
```bash
# Verify class definition (T014)
grep -n "class.*ThreadItemStore" backend/src/chatkit/store.py

# Verify load_thread_items with 20-message limit (T014)
grep -n "def load_thread_items\|limit.*20\|CHATKIT_HISTORY_LIMIT" backend/src/chatkit/store.py

# Verify save_thread_item with truncation (T015, FR-024)
grep -n "def save_thread_item\|10000\|truncat" backend/src/chatkit/store.py

# Verify delete_thread_items soft delete (T016)
grep -n "def delete_thread_items\|deleted_at" backend/src/chatkit/store.py
```

**Utilities** (`backend/src/chatkit/utils.py`):
```bash
# Verify retry logic (T011, T018)
grep -n "def retry.*exponential\|def retry_database" backend/src/chatkit/utils.py

# Verify correlation ID utilities (T017)
grep -n "correlation_id\|RequestContext\|ContextVar" backend/src/chatkit/utils.py
```

### API Endpoints (Phase 3: T024-T026)

**ChatKit Router** (`backend/src/api/chatkit.py`):
```bash
# Verify POST /api/chatkit/chat endpoint (T024)
grep -n "@router.post.*chat\|def.*chat.*endpoint" backend/src/api/chatkit.py
grep -n "StreamingResponse\|text/event-stream" backend/src/api/chatkit.py
grep -n "Depends.*get_current_user" backend/src/api/chatkit.py

# Verify DELETE /api/chatkit/conversation endpoint (T025)
grep -n "@router.delete.*conversation\|def.*delete.*conversation" backend/src/api/chatkit.py

# Verify health check endpoint (T063)
grep -n "@router.get.*health\|def.*health" backend/src/api/chatkit.py

# Verify router registration in main.py (T026)
grep -n "chatkit.*router\|include_router.*chatkit" backend/src/main.py
```

### Error Handling (Phase 3: T027, T011, T018)

```bash
# Verify retry wrappers used in respond() (T027)
grep -n "retry_with_exponential_backoff\|retry_database_operation" backend/src/chatkit/server.py

# Verify MCP connection error handling (FR-018)
grep -n "except.*ConnectError\|except.*httpx\|except.*MCP" backend/src/chatkit/agent.py backend/src/chatkit/server.py

# Verify database error handling (FR-019)
grep -n "except.*OperationalError\|except.*DBAPIError" backend/src/chatkit/utils.py backend/src/chatkit/server.py
```

---

## Level 3: Test Execution

### Prerequisites

```bash
# Ensure you're in the backend directory
cd backend

# Activate virtual environment if using one
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # pytest, pytest-asyncio, httpx, faker, etc.

# Set up test environment variables
cp .env.example .env.test
# Edit .env.test with test database URL, test OpenAI key, etc.

# Run database migrations
alembic upgrade head
```

### Unit Tests (Phase 8: T049-T051)

**Run all unit tests**:
```bash
pytest tests/unit/test_chatkit_*.py -v
```

**Individual unit test files**:

1. **T049**: CustomChatKitServer.respond() unit tests
   ```bash
   pytest tests/unit/test_chatkit_server.py -v
   ```
   - Tests conversation loading
   - Tests message persistence
   - Tests error handling with mocked MCP client

2. **T050**: DatabaseThreadItemStore unit tests
   ```bash
   pytest tests/unit/test_chatkit_store.py -v
   ```
   - Tests load_thread_items() with 20-message limit
   - Tests save_thread_item() with content truncation
   - Tests delete_thread_items() soft delete

3. **T051**: Retry utilities unit tests
   ```bash
   pytest tests/unit/test_chatkit_utils.py -v
   ```
   - Tests retry_with_exponential_backoff() with mock failures
   - Tests retry_database_operation() with mock OperationalError
   - Tests correlation ID generation

### Integration Tests (Phase 8: T052-T059)

**Run all integration tests**:
```bash
pytest tests/integration/test_chatkit_*.py -v
```

**Individual integration test files**:

1. **T052**: POST /api/chatkit/chat endpoint integration test
   ```bash
   pytest tests/integration/test_chatkit_api.py::test_chat_endpoint -v
   ```
   - Tests authenticated request with valid JWT
   - Verifies streaming response (SSE events)
   - Verifies message persistence to database
   - Tests 401 for invalid token

2. **T053**: DELETE /api/chatkit/conversation integration test
   ```bash
   pytest tests/integration/test_chatkit_api.py::test_delete_conversation -v
   ```
   - Tests conversation soft delete
   - Verifies deleted_at timestamp
   - Verifies messages cascaded
   - Tests 404 for no active conversation

3. **T054**: Persistence integration test (stateless architecture)
   ```bash
   pytest tests/integration/test_chatkit_persistence.py::test_stateless_architecture -v
   ```
   - Tests full workflow (send message, save to DB, refresh, load history)
   - Verifies 20-message limit enforcement
   - Verifies conversation resumption after server restart (validates SC-002)

4. **T056**: FR-007 (20-message history limit test)
   ```bash
   pytest tests/integration/test_chatkit_persistence.py::test_conversation_history_limit -v
   ```
   - Creates conversation with 25 messages
   - Verifies only last 20 returned in chronological order
   - Verifies first 5 excluded

5. **T057**: FR-024 (message truncation test)
   ```bash
   pytest tests/integration/test_chatkit_message_truncation.py -v
   ```
   - Tests message content exactly 10,001 characters
   - Verifies truncation at 10,000 with warning appended
   - Verifies truncation event logged with correlation ID

6. **T058**: FR-016, SC-006 (logging audit test)
   ```bash
   pytest tests/integration/test_chatkit_logging.py -v
   ```
   - Sends test message through POST /api/chatkit/chat
   - Verifies correlation ID in ALL log entries
   - Verifies 100% logging coverage
   - Fails if any operation missing correlation ID

7. **T059**: FR-023 (database connection pool test)
   ```bash
   pytest tests/integration/test_database_config.py -v
   ```
   - Inspects engine pool configuration
   - Asserts pool_size == 10
   - Asserts max_overflow == 40
   - Asserts pool_timeout == 30
   - Asserts pool_pre_ping == True

### E2E Tests (Phase 8: T055, T055a)

**Run all E2E tests**:
```bash
pytest tests/e2e/test_chatkit_*.py -v
```

**Individual E2E test files**:

1. **T055**: Complete chat workflow E2E test
   ```bash
   pytest tests/e2e/test_chatkit_workflow.py -v
   ```
   - Authenticates user
   - Sends "Add task to buy groceries"
   - Verifies add_task MCP tool invoked
   - Verifies task created in database
   - Sends "Show my tasks"
   - Verifies list_tasks invoked
   - Verifies response includes created task
   - Sends "Mark task X as done"
   - Verifies complete_task invoked
   - Verifies task status updated

2. **T055a**: Malformed input edge case test
   ```bash
   pytest tests/e2e/test_chatkit_edge_cases.py::test_malformed_input -v
   ```
   - Sends nonsensical message "asdf jkl; qwerty"
   - Verifies OpenAI Agents SDK interprets as unclear
   - Verifies assistant responds with helpful prompt

### Test Coverage Report

```bash
# Generate coverage report
pytest tests/ --cov=src/chatkit --cov=src/api/chatkit --cov-report=html --cov-report=term

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows

# Target: 80%+ coverage (Constitutional requirement)
```

---

## Level 4: Functional Testing (Manual API Testing)

### Setup

```bash
# Start backend server
cd backend
uvicorn src.main:app --reload --port 8000

# In another terminal, start MCP server (prerequisite)
cd mcp_server
python -m uvicorn src.todo_mcp.server:app --port 8001
```

### Test Scenarios

#### 1. Health Check (T063)

```bash
curl -X GET http://localhost:8000/api/chatkit/health
# Expected: {"status": "healthy", "mcp_connected": true}
```

#### 2. Authentication Test (FR-008)

```bash
# Get JWT token (adjust based on your Better Auth setup)
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}' | jq -r '.token')

# Test without token (should fail with 401)
curl -X POST http://localhost:8000/api/chatkit/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
# Expected: 401 Unauthorized

# Test with token (should succeed)
curl -X POST http://localhost:8000/api/chatkit/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}' \
  --no-buffer
# Expected: SSE stream with assistant response
```

#### 3. Task Creation via Chat (US1: FR-002)

```bash
curl -X POST http://localhost:8000/api/chatkit/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy groceries"}' \
  --no-buffer
# Expected: SSE stream confirming task creation with task ID
```

**Verify in database**:
```bash
# Connect to database and check tasks table
psql $DATABASE_URL -c "SELECT * FROM tasks WHERE title ILIKE '%groceries%' ORDER BY created_at DESC LIMIT 1;"
```

#### 4. Task Listing via Chat (US2: FR-003)

```bash
curl -X POST http://localhost:8000/api/chatkit/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me my pending tasks"}' \
  --no-buffer
# Expected: Formatted list of pending tasks
```

#### 5. Task Completion via Chat (US3: FR-004)

```bash
# Replace TASK_ID with actual task ID from previous test
curl -X POST http://localhost:8000/api/chatkit/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Mark task TASK_ID as done"}' \
  --no-buffer
# Expected: Confirmation of task completion
```

#### 6. Task Update via Chat (US4: FR-005)

```bash
curl -X POST http://localhost:8000/api/chatkit/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Update task TASK_ID title to \"Buy organic groceries\""}' \
  --no-buffer
# Expected: Confirmation of update
```

#### 7. Task Deletion via Chat (US4: FR-006)

```bash
curl -X POST http://localhost:8000/api/chatkit/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Delete task TASK_ID"}' \
  --no-buffer
# Expected: Confirmation of deletion
```

#### 8. Conversation Persistence (US5: FR-012, SC-002, SC-004)

```bash
# Send first message
curl -X POST http://localhost:8000/api/chatkit/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, I am testing conversation history"}' \
  --no-buffer

# Wait a few seconds, then send follow-up
curl -X POST http://localhost:8000/api/chatkit/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Do you remember what I just said?"}' \
  --no-buffer
# Expected: Assistant references previous message

# Verify persistence: Restart server, send new message
# Expected: Conversation history loads from database
```

#### 9. Conversation Deletion (FR-020)

```bash
curl -X DELETE http://localhost:8000/api/chatkit/conversation \
  -H "Authorization: Bearer $TOKEN"
# Expected: 204 No Content

# Verify soft delete in database
psql $DATABASE_URL -c "SELECT conversation_id, deleted_at FROM conversations WHERE user_id = 'USER_ID' ORDER BY created_at DESC LIMIT 1;"
# Expected: deleted_at timestamp set
```

#### 10. 20-Message History Limit (FR-007)

```bash
# Send 25 messages in a conversation
for i in {1..25}; do
  curl -X POST http://localhost:8000/api/chatkit/chat \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Test message number $i\"}" \
    --no-buffer
  sleep 1
done

# Send query to verify only last 20 messages used
curl -X POST http://localhost:8000/api/chatkit/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What was my first message?"}' \
  --no-buffer
# Expected: Assistant should NOT remember message 1-5 (only last 20)
```

#### 11. Edge Case: Malformed Input (T055a)

```bash
curl -X POST http://localhost:8000/api/chatkit/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "asdf jkl; qwerty zxcv"}' \
  --no-buffer
# Expected: Assistant responds with helpful prompt like "I didn't understand that. You can ask me to add tasks, list tasks..."
```

---

## Level 5: Constitutional Compliance

**Reference**: `.specify/memory/constitution.md`, `CLAUDE.md`

### Stateless Architecture (Constitution Section 3, SC-002)

- [ ] **No in-memory session state**: Verify CustomChatKitServer has no class-level state variables
  ```bash
  # Should NOT find: self.conversations = {}, self.messages = [], etc.
  grep -n "self\\..*=.*\[\]\|self\\..*=.*{}" backend/src/chatkit/server.py | grep -v "__init__"
  ```

- [ ] **Database-backed state**: All conversation and message state in PostgreSQL
  ```bash
  # Verify all state queries hit database
  grep -n "session.execute\|session.query\|session.get" backend/src/chatkit/store.py
  ```

- [ ] **Restart test passes** (T028, T054):
  ```bash
  # Manual test:
  # 1. Send message via API
  # 2. Kill server (Ctrl+C)
  # 3. Restart server
  # 4. Send another message
  # 5. Verify history includes message from step 1
  ```

### User Isolation (Constitution Section 10, FR-017)

- [ ] **All models have user_id foreign key**:
  ```bash
  grep -n "user_id.*ForeignKey" backend/src/models/conversation.py backend/src/models/message.py
  ```

- [ ] **All database queries filter by user_id**:
  ```bash
  # Should find user_id in ALL query filters
  grep -n "where.*user_id\|filter.*user_id" backend/src/chatkit/store.py backend/src/chatkit/server.py
  ```

- [ ] **No cross-user access possible** (T066):
  ```bash
  # Manual security test:
  # 1. Create User A, send message
  # 2. Create User B, try to access User A's conversation_id
  # 3. Expected: 403 Forbidden or 404 Not Found
  ```

### Async/Await for All I/O (Constitution Section 4)

- [ ] **All database operations use async**:
  ```bash
  grep -n "async def.*(" backend/src/chatkit/store.py | wc -l
  # Should match number of methods in DatabaseThreadItemStore
  ```

- [ ] **All MCP client calls use async**:
  ```bash
  grep -n "await.*mcp\|async def.*mcp" backend/src/chatkit/agent.py
  ```

- [ ] **All OpenAI agent calls use async**:
  ```bash
  grep -n "await.*agent\|async def.*agent" backend/src/chatkit/agent.py backend/src/chatkit/server.py
  ```

### Type Safety (Constitution Section 5)

- [ ] **No `Any` types used**:
  ```bash
  grep -n ": Any\|-> Any" backend/src/chatkit/*.py | wc -l
  # Should be 0 or minimal (only for truly dynamic data)
  ```

- [ ] **All SQLModel fields typed**:
  ```bash
  grep -n "Field\|Optional\|UUID\|datetime" backend/src/models/conversation.py backend/src/models/message.py
  ```

### Soft Deletes (Constitution, FR-020)

- [ ] **deleted_at field in all relevant models**:
  ```bash
  grep -n "deleted_at.*Optional\[datetime\]" backend/src/models/conversation.py backend/src/models/message.py
  ```

- [ ] **All queries filter out soft-deleted records**:
  ```bash
  grep -n "deleted_at IS NULL\|deleted_at == None" backend/src/chatkit/store.py
  ```

### Structured Logging (Constitution Section 9, FR-016, SC-006)

- [ ] **Correlation IDs in all log entries** (T058):
  ```bash
  # Run logging audit test
  pytest tests/integration/test_chatkit_logging.py -v
  ```

- [ ] **All critical operations logged**:
  ```bash
  grep -n "logger\\.info\|logger\\.error\|logger\\.warning" backend/src/chatkit/server.py backend/src/chatkit/agent.py | wc -l
  # Should have logs for: message receipt, conversation load, agent invocation, MCP tool calls, response streaming
  ```

### Retry Logic (FR-014, FR-015, FR-018, FR-019)

- [ ] **OpenAI retry: 3 attempts, exponential backoff (2s, 4s, 8s)**:
  ```bash
  grep -n "retry.*3\|max_attempts.*3" backend/src/chatkit/utils.py
  grep -n "2.*4.*8\|exponential" backend/src/chatkit/utils.py
  ```

- [ ] **Database retry: 2 attempts, 1s delay**:
  ```bash
  grep -n "retry.*2\|max_attempts.*2" backend/src/chatkit/utils.py
  grep -n "delay.*1\|sleep.*1" backend/src/chatkit/utils.py
  ```

### Security (Constitution, T066)

- [ ] **JWT validation on all protected endpoints**:
  ```bash
  grep -n "Depends(get_current_user)" backend/src/api/chatkit.py | wc -l
  # Should match number of protected endpoints (at least 2: POST /chat, DELETE /conversation)
  ```

- [ ] **No secrets in logs**:
  ```bash
  grep -i "OPENAI_API_KEY\|password\|token" backend/src/chatkit/*.py | grep -v "config\\.py"
  # Should find NO hardcoded secrets
  ```

- [ ] **No SQL injection possible** (using SQLModel ORM):
  ```bash
  # Verify NO raw SQL strings with user input
  grep -n "execute.*f\"\|query.*f\"" backend/src/chatkit/*.py
  # Should be 0 (all queries via SQLModel)
  ```

---

## Summary Checklist

Use this high-level checklist to track overall progress:

### Phase Completion

- [X] **Phase 0: Research** (R001-R008) - All research tasks complete
- [X] **Phase 1: Setup** (T001-T004) - Project structure and dependencies
- [X] **Phase 2: Foundational** (T005-T019) - Database models, MCP client, Agent SDK, ThreadItemStore
- [X] **Phase 3: User Story 5** (T020-T028) - Persistent conversation history
- [X] **Phase 4: User Story 1** (T029-T032) - Natural language task creation
- [X] **Phase 5: User Story 2** (T033-T036) - View and filter tasks
- [X] **Phase 6: User Story 3** (T037-T041) - Mark tasks complete
- [X] **Phase 7: User Story 4** (T042-T048) - Update and delete tasks
- [X] **Phase 8: Testing** (T049-T059) - Comprehensive test coverage
- [X] **Phase 9: Polish** (T060-T066) - Documentation, logging, security

### Verification Levels

- [ ] **Level 1: Specification Compliance** - All 24 FRs + 6 SCs verified
- [ ] **Level 2: Code Structure** - All files, classes, methods exist
- [ ] **Level 3: Test Execution** - All 9 test files pass (unit, integration, E2E)
- [ ] **Level 4: Functional Testing** - All 11 manual API scenarios work
- [ ] **Level 5: Constitutional Compliance** - Stateless, user isolation, async, type safety, soft deletes, logging, retry, security

### Critical Requirements

- [ ] **Stateless Architecture**: Server restart test passes (SC-002)
- [ ] **20-Message Limit**: Conversation history limited to last 20 (FR-007)
- [ ] **User Isolation**: No cross-user data access possible (FR-017)
- [ ] **Message Truncation**: Content truncated at 10,000 chars (FR-024)
- [ ] **Correlation IDs**: 100% logging coverage (SC-006)
- [ ] **Connection Pool**: Supports 50 concurrent requests (FR-023, SC-003)
- [ ] **All MCP Tools Work**: add/list/complete/update/delete (SC-005)
- [ ] **Test Coverage**: 80%+ coverage (Constitutional requirement)

---

## Next Steps After Verification

### If All Checks Pass ✅

1. **Commit Changes**:
   ```bash
   git add .
   git commit -m "feat(phase3): implement ChatKit backend server

   - Implemented CustomChatKitServer with OpenAI Agents SDK
   - Integrated MCP client for task management tools
   - Added Conversation and Message persistence
   - Implemented 20-message history limit
   - Added comprehensive test coverage (unit, integration, E2E)
   - Configured connection pooling for 50 concurrent requests
   - Added structured logging with correlation IDs

   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
   ```

2. **Create Pull Request**:
   ```bash
   gh pr create --title "ChatKit Backend Server Implementation" \
     --body "$(cat <<'EOF'
   ## Summary
   - Implements Phase III: AI-Powered Chatbot backend (spec 008)
   - All 5 user stories complete (task creation, listing, completion, update, delete via chat)
   - Stateless architecture with database-backed conversation persistence
   - 100% test coverage with unit, integration, and E2E tests

   ## Test plan
   - [x] All 76 tasks completed (see tasks.md)
   - [x] Unit tests pass (T049-T051)
   - [x] Integration tests pass (T052-T059)
   - [x] E2E tests pass (T055, T055a)
   - [x] Manual API testing complete (see VERIFICATION_GUIDE.md)
   - [x] Constitutional compliance verified (stateless, user isolation, logging)

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```

3. **Update Project Status**:
   - Update `CLAUDE.md` with Phase III completion
   - Mark Phase III deliverables as complete
   - Prepare for Phase IV (Kubernetes deployment)

### If Some Checks Fail ❌

1. **Identify Failed Requirements**:
   - Review failed checks in each verification level
   - Prioritize by severity (critical FRs > nice-to-have features)

2. **Create Fix Tasks**:
   - Document missing implementations in a new tasks file
   - Follow same task format: `[ID] [Story] Description`

3. **Re-run Verification**:
   - After fixes, re-run this verification guide
   - Ensure all checks pass before proceeding

---

## Tools and Scripts

### Verification Script

Location: `backend/scripts/verify_implementation.sh`

```bash
# Run automated checks
bash backend/scripts/verify_implementation.sh
```

### Test Runner Script

Create `backend/scripts/run_all_tests.sh`:

```bash
#!/bin/bash
set -e

echo "Running all ChatKit tests..."

echo "=== Unit Tests ==="
pytest tests/unit/test_chatkit_*.py -v

echo "=== Integration Tests ==="
pytest tests/integration/test_chatkit_*.py -v

echo "=== E2E Tests ==="
pytest tests/e2e/test_chatkit_*.py -v

echo "=== Coverage Report ==="
pytest tests/ --cov=src/chatkit --cov=src/api/chatkit --cov-report=term --cov-report=html

echo "✓ All tests passed!"
```

---

## Appendix: Quick Reference Commands

```bash
# Check task completion status
grep -c "\[X\]" specs/008-chatkit-server-backend/tasks.md  # Should be 76

# List all implementation files
find backend/src/chatkit backend/src/models -name "*.py" -type f

# List all test files
find backend/tests -name "*chatkit*" -type f

# Run specific test
pytest tests/unit/test_chatkit_server.py::test_respond_method -v

# Run tests with coverage
pytest tests/ --cov=src/chatkit --cov-report=html

# Check code quality (optional)
ruff check backend/src/chatkit backend/src/api/chatkit.py
mypy backend/src/chatkit backend/src/api/chatkit.py

# Database migrations
alembic upgrade head  # Apply migrations
alembic downgrade -1  # Rollback last migration
alembic history       # Show migration history

# Start servers for manual testing
uvicorn src.main:app --reload --port 8000  # Backend
cd mcp_server && python -m uvicorn src.todo_mcp.server:app --port 8001  # MCP server
```

---

**Last Updated**: 2026-01-14
**Feature**: 008-chatkit-server-backend
**Total Tasks**: 76 (all marked complete)
**Test Files**: 9 (3 unit, 5 integration, 2 E2E)
**Specification**: specs/008-chatkit-server-backend/spec.md
