# User Story 1 - Natural Language Task Creation Test Plan

**Feature**: 008-chatkit-server-backend
**User Story**: US1 - Natural Language Task Creation via Chat
**Task Reference**: T030
**Date**: 2026-01-13

## Overview

This test plan validates that users can create tasks by typing natural language commands without needing API syntax or forms. The chatbot should invoke the `add_task` MCP tool and return a confirmation with the task ID.

## Prerequisites

Before running these tests:

1. ✅ MCP server running at `http://localhost:8001/mcp`
2. ✅ Backend server running at `http://localhost:8000`
3. ✅ ChatKit SDK, OpenAI Agents SDK, and MCP SDK installed
4. ✅ Valid OpenAI API key configured
5. ✅ User authenticated with valid JWT token
6. ✅ Database migrations applied (conversations, messages tables exist)

## Test Scenarios

### Scenario 1: Basic Task Creation

**Given**: User is authenticated and has no existing conversations

**When**: User sends message "Add a task to buy groceries"

**Then**:
1. **MCP Tool Invocation**:
   - System invokes `add_task` MCP tool
   - Parameters: `user_id` (from JWT), `title="Buy groceries"`, `description=null`
   - Tool returns: `{"task_id": 42, "title": "Buy groceries", "status": "pending"}`

2. **SSE Events Streamed** (in order):
   ```
   event: thread.message.delta
   data: {"type":"thread.message.delta","delta":{"content":"I'll add that task for you."}}

   event: tool.call.start
   data: {"type":"tool.call.start","tool_name":"add_task","tool_input":{"user_id":"...","title":"Buy groceries"}}

   event: tool.call.result
   data: {"type":"tool.call.result","tool_name":"add_task","tool_output":{"task_id":42,"title":"Buy groceries"},"success":true}

   event: thread.message.delta
   data: {"type":"thread.message.delta","delta":{"content":"✓ Task created: Buy groceries (ID: 42)"}}

   event: thread.message.completed
   data: {"type":"thread.message.completed","message":{"content":"I'll add that task for you.\n✓ Task created: Buy groceries (ID: 42)"}}
   ```

3. **Database Verification**:
   - User message saved: `role='user'`, `content='Add a task to buy groceries'`
   - Assistant message saved: `role='assistant'`, `content='I'll add that task for you.\n✓ Task created: Buy groceries (ID: 42)'`
   - Both messages linked to same `conversation_id`

4. **Structured Logging**:
   - Message receipt logged with correlation_id
   - `add_task` tool invocation logged (tool_name, user_id, parameters)
   - Tool result logged (success=true, task_id=42)
   - Assistant response completion logged

**Expected Result**: ✅ Task created with ID 42, user receives confirmation

---

### Scenario 2: Task Creation with Description

**Given**: User is authenticated

**When**: User sends message "Create a task to submit report with description 'Include Q4 financials'"

**Then**:
1. **MCP Tool Invocation**:
   - System invokes `add_task` MCP tool
   - Parameters: `user_id`, `title="Submit report"`, `description="Include Q4 financials"`
   - Tool returns: `{"task_id": 43, "title": "Submit report", "description": "Include Q4 financials", "status": "pending"}`

2. **SSE Events**: Similar to Scenario 1, with description included in tool_input and tool_output

3. **Assistant Response**: Confirms task creation with both title and description

**Expected Result**: ✅ Task created with title and description

---

### Scenario 3: Conversation Persistence Across Turns

**Given**: User created task in Scenario 1 (conversation exists)

**When**: User sends message "Add another task to call dentist"

**Then**:
1. **Conversation Continuity**:
   - System loads existing conversation (same `conversation_id`)
   - Conversation history includes previous task creation messages (last 20)

2. **MCP Tool Invocation**:
   - System invokes `add_task` again for second task
   - Parameters: `user_id`, `title="Call dentist"`
   - Tool returns: `{"task_id": 44, ...}`

3. **Database Verification**:
   - New user message appended to existing conversation
   - New assistant message appended to same conversation
   - All messages have same `conversation_id`, different `created_at` timestamps

**Expected Result**: ✅ Second task created, conversation history preserved

---

### Scenario 4: Error Handling - MCP Tool Failure

**Given**: User is authenticated, MCP server is unreachable

**When**: User sends message "Add task to buy milk"

**Then**:
1. **Retry Logic Triggered**:
   - System attempts to connect to MCP server
   - Retry 3 times with exponential backoff (2s, 4s, 8s)
   - All attempts fail (httpx.ConnectError)

2. **Error Event Streamed**:
   ```
   event: error
   data: {"type":"error","error":{"message":"Task service temporarily unavailable, please try again later","code":"MCP_CONNECTION_FAILED","correlation_id":"..."}}
   ```

3. **Structured Logging**:
   - Connection failures logged with correlation_id
   - Retry attempts logged (attempt 1/3, attempt 2/3, attempt 3/3)
   - Final error logged with error type and correlation_id

**Expected Result**: ⚠️ User receives error message with correlation ID for support

---

### Scenario 5: User Isolation Verification

**Given**: Two users (User A and User B) both authenticated

**When**:
- User A sends "Add task to buy groceries" → task_id: 42
- User B sends "Add task to buy groceries" → task_id: 43

**Then**:
1. **User A's Conversation**:
   - `conversation_id=AAA`, `user_id=A`
   - Messages scoped to User A only
   - MCP tool invoked with `user_id=A`

2. **User B's Conversation**:
   - `conversation_id=BBB`, `user_id=B`
   - Messages scoped to User B only
   - MCP tool invoked with `user_id=B`

3. **Database Verification**:
   - User A cannot query User B's conversations or messages
   - MCP server receives correct `user_id` parameter (enforces task ownership)

**Expected Result**: ✅ User isolation enforced at all levels

---

## Manual Testing Steps

### Setup

```bash
# Terminal 1: Start MCP server
cd mcp_server
python -m todo_mcp.server
# Expected: "MCP server running on http://localhost:8001/mcp"

# Terminal 2: Start backend
cd backend
uvicorn src.main:app --reload --port 8000
# Expected: "Application startup complete"

# Terminal 3: Get JWT token
curl -X POST http://localhost:3000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"password123"}'
# Save token to $TOKEN
```

### Test Execution

```bash
# Scenario 1: Basic task creation
curl -N -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Add a task to buy groceries"}' \
     http://localhost:8000/api/chatkit/chat

# Expected SSE output:
# event: thread.message.delta
# data: {"type":"thread.message.delta",...}
# event: tool.call.start
# data: {"type":"tool.call.start","tool_name":"add_task",...}
# event: tool.call.result
# data: {"type":"tool.call.result","tool_output":{"task_id":42},...}
# event: thread.message.completed
# data: {"type":"thread.message.completed",...}

# Scenario 2: With description
curl -N -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Create a task to submit report with description Include Q4 financials"}' \
     http://localhost:8000/api/chatkit/chat

# Scenario 3: Second task (same conversation)
curl -N -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Add another task to call dentist"}' \
     http://localhost:8000/api/chatkit/chat
```

### Database Verification

```bash
# Check conversations table
psql $DATABASE_URL -c "SELECT conversation_id, user_id, created_at FROM conversations WHERE deleted_at IS NULL;"

# Check messages table
psql $DATABASE_URL -c "SELECT message_id, conversation_id, role, LEFT(content, 50), created_at FROM messages WHERE deleted_at IS NULL ORDER BY created_at DESC LIMIT 10;"

# Check tasks created via MCP
psql $DATABASE_URL -c "SELECT id, title, description, completed FROM tasks ORDER BY created_at DESC LIMIT 10;"
```

### Log Verification

```bash
# Check structured logs for correlation IDs
tail -f backend/logs/chatkit.log | jq 'select(.tool_name == "add_task")'

# Expected output:
# {
#   "correlation_id": "550e8400-...",
#   "user_id": "...",
#   "conversation_id": "...",
#   "tool_name": "add_task",
#   "tool_input": {"user_id": "...", "title": "Buy groceries"},
#   "tool_output": {"task_id": 42, "title": "Buy groceries"},
#   "success": true
# }
```

---

## Acceptance Criteria

✅ **AC1**: User can create task with natural language command
- Message "Add task to X" invokes `add_task` MCP tool with correct parameters
- Tool returns task_id and assistant confirms creation

✅ **AC2**: SSE events emitted in correct order
- tool.call.start before tool.call.result
- thread.message.completed after all tool calls finish

✅ **AC3**: Structured logging captures all operations
- Message receipt logged with correlation_id
- Tool invocation logged (tool_name, user_id, parameters)
- Tool result logged (success, task_id)
- Assistant response logged (message_length)

✅ **AC4**: Conversation history persisted to database
- User message saved immediately
- Assistant message saved after streaming completes
- Both messages linked to same conversation_id

✅ **AC5**: User isolation enforced
- user_id from JWT token passed to MCP tool
- Cannot access other users' conversations or tasks

---

## Performance Benchmarks

| Metric | Target | Measured |
|--------|--------|----------|
| Response time (p95) | <5s | _TBD_ |
| First token latency | <1s | _TBD_ |
| MCP tool invocation | <500ms | _TBD_ |
| Database query | <100ms | _TBD_ |

---

## Known Limitations

⚠️ **SDK Installation Required**: Tests cannot run until ChatKit SDK, OpenAI Agents SDK, and MCP SDK are installed per `backend/requirements.txt`.

⚠️ **OpenAI API Key Required**: Tests require valid OpenAI API key with sufficient credits.

⚠️ **Natural Language Variability**: AI may interpret commands differently based on phrasing. Test scenarios use specific phrases to ensure consistency.

---

## Next Steps

After User Story 1 validated:
1. Proceed to User Story 2: List tasks via natural language
2. Implement User Story 3: Complete tasks via natural language
3. Implement User Story 4: Update/delete tasks via natural language

---

**Test Plan Status**: ✅ COMPLETE (ready for execution once SDKs installed)
**Last Updated**: 2026-01-13
**Related**: tasks.md (T030), spec.md (US1), contracts/chatkit-sse-events.md
