# User Story 3 - Mark Tasks Complete via Natural Language Test Plan

**Feature**: 008-chatkit-server-backend
**User Story**: US3 - Mark Tasks Complete via Natural Language
**Task Reference**: T038, T039, T040
**Date**: 2026-01-13

## Overview

This test plan validates that users can mark tasks as complete by referencing task ID or title in natural language. The chatbot should invoke the `complete_task` MCP tool and confirm completion, or provide user-friendly error messages if the task is not found.

## Prerequisites

Before running these tests:

1. ✅ MCP server running at `http://localhost:8001/mcp`
2. ✅ Backend server running at `http://localhost:8000`
3. ✅ ChatKit SDK, OpenAI Agents SDK, and MCP SDK installed
4. ✅ Valid OpenAI API key configured
5. ✅ User authenticated with valid JWT token
6. ✅ Database has sample pending tasks for testing (at least 3)

## Test Scenarios

### Scenario 1: Complete Task by ID (T038)

**Given**: User has pending task in database:
- Task ID 42: "Buy groceries" (status: pending)

**When**: User sends message "Mark task 42 as done"

**Then**:
1. **MCP Tool Invocation**:
   - System invokes `complete_task` MCP tool
   - Parameters: `user_id` (from JWT), `task_id=42`
   - Tool returns: `{"task_id": 42, "title": "Buy groceries", "status": "completed"}`

2. **SSE Events Streamed** (in order):
   ```
   event: thread.message.delta
   data: {"type":"thread.message.delta","delta":{"content":"I'll mark that task as complete for you."}}

   event: tool.call.start
   data: {"type":"tool.call.start","tool_name":"complete_task","tool_input":{"user_id":"...","task_id":42}}

   event: tool.call.result
   data: {"type":"tool.call.result","tool_name":"complete_task","tool_output":{"task_id":42,"title":"Buy groceries","status":"completed"},"success":true}

   event: thread.message.delta
   data: {"type":"thread.message.delta","delta":{"content":"✓ Task 42 'Buy groceries' marked as completed!"}}

   event: thread.message.completed
   data: {"type":"thread.message.completed","message":{"content":"I'll mark that task as complete for you.\n✓ Task 42 'Buy groceries' marked as completed!"}}
   ```

3. **Database Verification**:
   - Query tasks table: `SELECT id, title, completed FROM tasks WHERE id = 42;`
   - Expected: `completed = true`

4. **Structured Logging (T041)**:
   - Tool invocation logged: `tool_name="complete_task"`, `task_id=42`, `user_id`, `correlation_id`
   - Tool result logged: `success=true`, `task_id=42`, `correlation_id`
   - Log message: "complete_task MCP tool execution completed: task 42 marked as completed"

**Expected Result**: ✅ Task 42 status updated to completed, user receives confirmation

---

### Scenario 2: Complete Task by Title - Two-Step Process (T039)

**Given**: User has pending task:
- Task ID 43: "Submit report" (status: pending)

**When**: User sends message "Complete the 'Submit report' task"

**Then**:
1. **AI Reasoning** (Two-step process):
   - Step 1: Agent invokes `list_tasks` to find task ID by title
   - Step 2: Agent invokes `complete_task` with resolved task_id=43

2. **SSE Events Streamed** (two tool calls):
   ```
   event: tool.call.start
   data: {"type":"tool.call.start","tool_name":"list_tasks","tool_input":{"user_id":"...","status":"pending"}}

   event: tool.call.result
   data: {"type":"tool.call.result","tool_name":"list_tasks","tool_output":[{"task_id":43,"title":"Submit report","status":"pending"}],"success":true}

   event: tool.call.start
   data: {"type":"tool.call.start","tool_name":"complete_task","tool_input":{"user_id":"...","task_id":43}}

   event: tool.call.result
   data: {"type":"tool.call.result","tool_name":"complete_task","tool_output":{"task_id":43,"title":"Submit report","status":"completed"},"success":true}

   event: thread.message.completed
   data: {"message":{"content":"✓ Task 'Submit report' has been marked as completed!"}}
   ```

3. **Database Verification**:
   - Query tasks table: `SELECT id, title, completed FROM tasks WHERE id = 43;`
   - Expected: `completed = true`

4. **Structured Logging**:
   - list_tasks logged first (to find task by title)
   - complete_task logged second (actual completion)

**Expected Result**: ✅ AI resolves title to ID and completes task successfully

---

### Scenario 3: Task Not Found Error - Invalid ID (T040)

**Given**: User database does not contain task ID 999

**When**: User sends message "Complete task 999"

**Then**:
1. **MCP Tool Invocation**:
   - System invokes `complete_task` MCP tool
   - Parameters: `user_id`, `task_id=999`
   - Tool returns: `{"error": "Task 999 not found for user", "success": false}`

2. **SSE Events Streamed**:
   ```
   event: tool.call.start
   data: {"type":"tool.call.start","tool_name":"complete_task","tool_input":{"user_id":"...","task_id":999}}

   event: tool.call.result
   data: {"type":"tool.call.result","tool_name":"complete_task","tool_output":{"error":"Task 999 not found"},"success":false}

   event: thread.message.delta
   data: {"type":"thread.message.delta","delta":{"content":"I couldn't find task 999 in your task list. Please check the task ID and try again."}}

   event: thread.message.completed
   data: {"message":{"content":"I couldn't find task 999 in your task list. Please check the task ID and try again."}}
   ```

3. **Structured Logging (T040)**:
   - Tool invocation logged: `tool_name="complete_task"`, `task_id=999`, `correlation_id`
   - Tool failure logged: `success=false`, `error="Task 999 not found"`, `correlation_id`
   - Log level: WARNING (not ERROR - user input error)
   - Log message: "complete_task MCP tool failed: Task 999 not found"

4. **No Database Changes**: Task table unchanged (nothing to update)

**Expected Result**: ⚠️ User receives friendly error message (not technical error), no exception thrown

---

### Scenario 4: Task Not Found Error - Invalid Title (T040)

**Given**: User database does not contain task titled "Nonexistent task"

**When**: User sends message "Complete the 'Nonexistent task' task"

**Then**:
1. **AI Reasoning** (Two-step with failure):
   - Step 1: Agent invokes `list_tasks` to search for task
   - Step 2: No matching task found in results
   - Agent responds: "I couldn't find a task titled 'Nonexistent task' in your list."

2. **SSE Events**: list_tasks returns empty or no match, no complete_task invoked

3. **Structured Logging**:
   - list_tasks logged with `task_count=0` or no match
   - No complete_task logged (never invoked)

**Expected Result**: ⚠️ User informed task doesn't exist before attempting completion

---

### Scenario 5: Complete Already Completed Task (Idempotent)

**Given**: User has task that's already completed:
- Task ID 45: "Review PR" (status: completed)

**When**: User sends message "Mark task 45 as done"

**Then**:
1. **MCP Tool Invocation**:
   - System invokes `complete_task` MCP tool
   - Parameters: `user_id`, `task_id=45`
   - Tool returns: `{"task_id": 45, "title": "Review PR", "status": "completed"}` (already completed)

2. **Assistant Response**:
   - "Task 45 'Review PR' is already marked as completed."
   - Or: "✓ Task 45 is complete!" (acknowledges without error)

3. **Database**: No change (already completed)

**Expected Result**: ✅ Idempotent operation, no error thrown

---

### Scenario 6: Natural Language Variations

**Given**: User has pending task ID 42

**When**: User sends variations:
- "Finish task 42"
- "Task 42 is done"
- "I completed task 42"
- "Check off task 42"
- "Mark 42 as complete"

**Then**:
- All variations should invoke `complete_task` with task_id=42
- AI interprets intent correctly
- Consistent confirmation message

**Expected Result**: ✅ Natural language understanding works for various phrasings

---

### Scenario 7: User Isolation - Cannot Complete Other User's Task

**Given**:
- User A (user_id=A) has task ID 42
- User B (user_id=B) authenticated

**When**: User B sends "Mark task 42 as done"

**Then**:
1. **MCP Tool Invocation**:
   - System invokes `complete_task` with `user_id=B`, `task_id=42`
   - Tool returns: `{"error": "Task 42 not found for user B", "success": false}`

2. **Assistant Response**: "I couldn't find task 42 in your task list."

3. **Database**: User A's task unchanged (User B cannot modify it)

**Expected Result**: ✅ User isolation enforced, task not found for User B

---

## Manual Testing Steps

### Setup

```bash
# Terminal 1: Start MCP server
cd mcp_server
python -m todo_mcp.server

# Terminal 2: Start backend
cd backend
uvicorn src.main:app --reload --port 8000

# Terminal 3: Seed database with test tasks
psql $DATABASE_URL <<EOF
-- Insert test tasks for user
INSERT INTO tasks (user_id, title, description, completed) VALUES
  ('user-uuid-here', 'Buy groceries', 'Milk, eggs, bread', false),  -- ID 42
  ('user-uuid-here', 'Submit report', 'Q4 financials', false),       -- ID 43
  ('user-uuid-here', 'Call dentist', 'Schedule checkup', false),     -- ID 44
  ('user-uuid-here', 'Review PR', '#123 bug fix', true);             -- ID 45 (already completed)
EOF

# Get JWT token
export TOKEN="eyJhbGc..."
```

### Test Execution

```bash
# Scenario 1: Complete task by ID
curl -N -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Mark task 42 as done"}' \
     http://localhost:8000/api/chatkit/chat

# Expected SSE output:
# event: tool.call.start
# data: {"tool_name":"complete_task","tool_input":{"task_id":42},...}
# event: tool.call.result
# data: {"tool_output":{"task_id":42,"status":"completed"},"success":true,...}
# event: thread.message.completed
# data: {"message":{"content":"✓ Task 42 'Buy groceries' marked as completed!"}}

# Scenario 2: Complete task by title
curl -N -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Complete the Submit report task"}' \
     http://localhost:8000/api/chatkit/chat

# Scenario 3: Task not found (invalid ID)
curl -N -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Complete task 999"}' \
     http://localhost:8000/api/chatkit/chat

# Expected: "I couldn't find task 999 in your task list..."

# Scenario 5: Already completed task (idempotent)
curl -N -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Mark task 45 as done"}' \
     http://localhost:8000/api/chatkit/chat

# Expected: "Task 45 is already completed" or similar
```

### Database Verification

```bash
# Check task completion status
psql $DATABASE_URL -c "SELECT id, title, completed FROM tasks WHERE user_id = 'user-uuid-here' ORDER BY id;"

# Expected after Scenario 1:
# 42 | Buy groceries  | true
# 43 | Submit report  | false
# 44 | Call dentist   | false
# 45 | Review PR      | true

# Expected after Scenario 2:
# 42 | Buy groceries  | true
# 43 | Submit report  | true  <-- changed
# 44 | Call dentist   | false
# 45 | Review PR      | true
```

### Log Verification (T041)

```bash
# Check structured logs for complete_task operations
tail -f backend/logs/chatkit.log | jq 'select(.tool_name == "complete_task")'

# Expected output (success):
# {
#   "correlation_id": "550e8400-...",
#   "user_id": "...",
#   "conversation_id": "...",
#   "tool_name": "complete_task",
#   "task_id": 42,
#   "success": true,
#   "message": "complete_task MCP tool execution completed: task 42 marked as completed"
# }

# Expected output (failure - task not found):
# {
#   "correlation_id": "550e8400-...",
#   "user_id": "...",
#   "tool_name": "complete_task",
#   "task_id": 999,
#   "success": false,
#   "error": "Task 999 not found",
#   "message": "complete_task MCP tool failed: Task 999 not found"
# }
```

---

## Acceptance Criteria

✅ **AC1**: User can complete task by ID with natural language
- Message "Mark task 42 as done" invokes `complete_task` with `task_id=42`
- Database updated: `completed=true`
- Assistant confirms: "✓ Task 42 marked as completed"

✅ **AC2**: User can complete task by title (T039)
- Message "Complete the 'Submit report' task" triggers two-step process:
  - Step 1: list_tasks to find task ID by title
  - Step 2: complete_task with resolved task_id
- Database updated correctly

✅ **AC3**: Task not found handled gracefully (T040)
- Invalid task ID or title returns user-friendly error message
- No exception thrown, no technical error details exposed
- Structured logging captures failure at WARNING level

✅ **AC4**: Structured logging captures all completion operations (T041)
- Tool invocation logged: `tool_name`, `user_id`, `task_id`, `correlation_id`
- Success logged: `success=true`, `task_id`, `correlation_id`
- Failure logged: `success=false`, `error`, `task_id`, `correlation_id` (WARNING level)

✅ **AC5**: Idempotent operation
- Completing already-completed task doesn't throw error
- Assistant acknowledges task is already complete

---

## Performance Benchmarks

| Metric | Target | Measured |
|--------|--------|----------|
| Response time (p95) | <2s | _TBD_ |
| First token latency | <1s | _TBD_ |
| MCP tool invocation | <200ms | _TBD_ |
| Database update | <50ms | _TBD_ |

---

## Edge Cases

### Edge Case 1: Multiple Tasks with Same Title
**When**: User has tasks "Buy milk" (ID 10) and "Buy milk" (ID 20)
**Expected**: AI may ask for clarification: "Which task? (ID 10 or ID 20)" or completes the first match

### Edge Case 2: Partial Title Match
**When**: User says "Complete buy task" (ambiguous - matches "Buy groceries", "Buy milk")
**Expected**: AI asks for clarification or lists matching tasks

### Edge Case 3: Task ID as String vs Integer
**When**: User says "Mark task forty-two as done" (words, not number)
**Expected**: AI should parse "forty-two" → 42 and invoke complete_task correctly

---

## Known Limitations

⚠️ **SDK Installation Required**: Tests cannot run until ChatKit SDK, OpenAI Agents SDK, and MCP SDK are installed per `backend/requirements.txt`.

⚠️ **Natural Language Variability**: AI interpretation of task titles may vary. Test scenarios use specific phrases for consistency.

⚠️ **Two-Step Process Latency**: Completion by title requires two MCP tool calls (list + complete), adding ~500ms latency.

---

## Next Steps

After User Story 3 validated:
1. Proceed to User Story 4: Update and delete tasks via natural language
2. Implement full CRUD via chat interface

---

**Test Plan Status**: ✅ COMPLETE (ready for execution once SDKs installed)
**Last Updated**: 2026-01-13
**Related**: tasks.md (T037-T041), spec.md (US3), contracts/chatkit-sse-events.md
