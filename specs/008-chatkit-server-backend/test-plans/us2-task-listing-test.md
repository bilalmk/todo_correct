# User Story 2 - View and Filter Tasks via Conversation Test Plan

**Feature**: 008-chatkit-server-backend
**User Story**: US2 - View and Filter Tasks via Conversation
**Task Reference**: T034, T035
**Date**: 2026-01-13

## Overview

This test plan validates that users can request task lists filtered by status using natural language queries. The chatbot should invoke the `list_tasks` MCP tool and return a formatted list of tasks or a friendly message if no tasks match the filter.

## Prerequisites

Before running these tests:

1. ✅ MCP server running at `http://localhost:8001/mcp`
2. ✅ Backend server running at `http://localhost:8000`
3. ✅ ChatKit SDK, OpenAI Agents SDK, and MCP SDK installed
4. ✅ Valid OpenAI API key configured
5. ✅ User authenticated with valid JWT token
6. ✅ Database has sample tasks for testing (at least 3 pending, 2 completed)

## Test Scenarios

### Scenario 1: List All Pending Tasks

**Given**: User has 3 pending tasks in database:
- Task ID 42: "Buy groceries" (pending)
- Task ID 43: "Submit report" (pending)
- Task ID 44: "Call dentist" (pending)

**When**: User sends message "Show me my pending tasks"

**Then**:
1. **MCP Tool Invocation**:
   - System invokes `list_tasks` MCP tool
   - Parameters: `user_id` (from JWT), `status="pending"`
   - Tool returns: `[{"task_id": 42, "title": "Buy groceries", "status": "pending"}, {...}]` (3 tasks)

2. **SSE Events Streamed** (in order):
   ```
   event: thread.message.delta
   data: {"type":"thread.message.delta","delta":{"content":"Here are your pending tasks:"}}

   event: tool.call.start
   data: {"type":"tool.call.start","tool_name":"list_tasks","tool_input":{"user_id":"...","status":"pending"}}

   event: tool.call.result
   data: {"type":"tool.call.result","tool_name":"list_tasks","tool_output":[{"task_id":42,"title":"Buy groceries","status":"pending"},{...}],"success":true}

   event: thread.message.delta
   data: {"type":"thread.message.delta","delta":{"content":"\n1. Buy groceries (ID: 42)\n2. Submit report (ID: 43)\n3. Call dentist (ID: 44)"}}

   event: thread.message.completed
   data: {"type":"thread.message.completed","message":{"content":"Here are your pending tasks:\n1. Buy groceries (ID: 42)\n2. Submit report (ID: 43)\n3. Call dentist (ID: 44)"}}
   ```

3. **Structured Logging (T036)**:
   - Tool invocation logged: `tool_name="list_tasks"`, `status_filter="pending"`, `user_id`
   - Tool result logged: `task_count=3`, `success=true`, `correlation_id`
   - Assistant response logged: `message_length`, `correlation_id`

**Expected Result**: ✅ User receives formatted list of 3 pending tasks with IDs

---

### Scenario 2: List All Completed Tasks

**Given**: User has 2 completed tasks in database:
- Task ID 45: "Review PR" (completed)
- Task ID 46: "Update docs" (completed)

**When**: User sends message "Show my completed tasks"

**Then**:
1. **MCP Tool Invocation**:
   - System invokes `list_tasks` MCP tool
   - Parameters: `user_id`, `status="completed"`
   - Tool returns: `[{"task_id": 45, "title": "Review PR", "status": "completed"}, {...}]` (2 tasks)

2. **SSE Events**: Similar to Scenario 1, with completed tasks listed

3. **Assistant Response**:
   ```
   Here are your completed tasks:
   1. Review PR (ID: 45)
   2. Update docs (ID: 46)
   ```

**Expected Result**: ✅ User receives formatted list of 2 completed tasks

---

### Scenario 3: List All Tasks (No Status Filter)

**Given**: User has 5 total tasks (3 pending + 2 completed)

**When**: User sends message "Show me all my tasks"

**Then**:
1. **MCP Tool Invocation**:
   - System invokes `list_tasks` MCP tool
   - Parameters: `user_id`, `status=null` (no filter)
   - Tool returns: Array of all 5 tasks (pending + completed)

2. **Assistant Response**:
   ```
   Here are all your tasks:

   Pending:
   1. Buy groceries (ID: 42)
   2. Submit report (ID: 43)
   3. Call dentist (ID: 44)

   Completed:
   4. Review PR (ID: 45)
   5. Update docs (ID: 46)
   ```

**Expected Result**: ✅ User receives all tasks grouped by status

---

### Scenario 4: Empty Task List - No Pending Tasks (T035)

**Given**: User has 0 pending tasks in database (all tasks completed or none exist)

**When**: User sends message "Show my pending tasks"

**Then**:
1. **MCP Tool Invocation**:
   - System invokes `list_tasks` MCP tool
   - Parameters: `user_id`, `status="pending"`
   - Tool returns: `[]` (empty array)

2. **SSE Events Streamed**:
   ```
   event: thread.message.delta
   data: {"type":"thread.message.delta","delta":{"content":"You have no pending tasks. Great job!"}}

   event: tool.call.start
   data: {"type":"tool.call.start","tool_name":"list_tasks","tool_input":{"user_id":"...","status":"pending"}}

   event: tool.call.result
   data: {"type":"tool.call.result","tool_name":"list_tasks","tool_output":[],"success":true}

   event: thread.message.completed
   data: {"type":"thread.message.completed","message":{"content":"You have no pending tasks. Great job!"}}
   ```

3. **Structured Logging (T035)**:
   - Tool result logged: `task_count=0`, `success=true`, `correlation_id`
   - Empty result logged: "list_tasks returned empty result (user has no tasks matching filter)"
   - Log includes: `user_id`, `status_filter="pending"`

**Expected Result**: ✅ User receives friendly "no pending tasks" message (not an error)

---

### Scenario 5: Empty Task List - No Completed Tasks (T035)

**Given**: User has 0 completed tasks in database (all tasks pending or none exist)

**When**: User sends message "What tasks have I completed?"

**Then**:
1. **MCP Tool Invocation**:
   - System invokes `list_tasks` MCP tool
   - Parameters: `user_id`, `status="completed"`
   - Tool returns: `[]` (empty array)

2. **Assistant Response**: "You haven't completed any tasks yet. Keep going!"

3. **Structured Logging**: Same as Scenario 4, with `status_filter="completed"`

**Expected Result**: ✅ User receives friendly "no completed tasks" message

---

### Scenario 6: Natural Language Variation

**Given**: User has tasks in database

**When**: User sends variations:
- "List my tasks"
- "What do I need to do?"
- "Show todos"
- "What's on my list?"

**Then**:
- All variations should invoke `list_tasks` tool
- AI interprets intent and applies appropriate status filter (or none)
- Consistent formatting in response

**Expected Result**: ✅ Natural language understanding works for various phrasings

---

### Scenario 7: Multi-Turn Conversation Context

**Given**: User previously created tasks in conversation

**When**:
1. User sends "Add task to buy groceries" → Task created (ID: 42)
2. User sends "Show me my pending tasks" → Should include task 42

**Then**:
1. **Conversation Continuity**:
   - Same `conversation_id` used for both messages
   - Conversation history includes task creation interaction

2. **Task Visibility**:
   - `list_tasks` returns task 42 (just created)
   - Assistant confirms task appears in list

**Expected Result**: ✅ Tasks created in conversation immediately appear in list

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
  ('user-uuid-here', 'Buy groceries', 'Milk, eggs, bread', false),
  ('user-uuid-here', 'Submit report', 'Q4 financials', false),
  ('user-uuid-here', 'Call dentist', 'Schedule checkup', false),
  ('user-uuid-here', 'Review PR', '#123 bug fix', true),
  ('user-uuid-here', 'Update docs', 'API reference', true);
EOF

# Get JWT token
export TOKEN="eyJhbGc..."
```

### Test Execution

```bash
# Scenario 1: List pending tasks
curl -N -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Show me my pending tasks"}' \
     http://localhost:8000/api/chatkit/chat

# Expected SSE output:
# event: tool.call.start
# data: {"tool_name":"list_tasks","tool_input":{"status":"pending"},...}
# event: tool.call.result
# data: {"tool_output":[{"task_id":42,...}],...}
# event: thread.message.completed
# data: {"message":{"content":"Here are your pending tasks:\n1. Buy groceries..."}}

# Scenario 2: List completed tasks
curl -N -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Show my completed tasks"}' \
     http://localhost:8000/api/chatkit/chat

# Scenario 4: Empty list (delete all pending tasks first)
psql $DATABASE_URL -c "UPDATE tasks SET completed = true WHERE user_id = 'user-uuid-here';"
curl -N -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Show my pending tasks"}' \
     http://localhost:8000/api/chatkit/chat

# Expected: "You have no pending tasks. Great job!"
```

### Log Verification

```bash
# Check structured logs for list_tasks operations (T036)
tail -f backend/logs/chatkit.log | jq 'select(.tool_name == "list_tasks")'

# Expected output:
# {
#   "correlation_id": "550e8400-...",
#   "user_id": "...",
#   "tool_name": "list_tasks",
#   "task_count": 3,
#   "status_filter": "pending",
#   "success": true,
#   "message": "list_tasks MCP tool execution completed: 3 tasks returned"
# }

# Check empty list logging (T035)
tail -f backend/logs/chatkit.log | jq 'select(.message | contains("empty result"))'

# Expected when task_count=0:
# {
#   "correlation_id": "...",
#   "user_id": "...",
#   "status_filter": "pending",
#   "message": "list_tasks returned empty result (user has no tasks matching filter)"
# }
```

### Database Verification

```bash
# Verify tasks exist in database
psql $DATABASE_URL -c "SELECT id, title, completed FROM tasks WHERE user_id = 'user-uuid-here';"

# Verify messages persisted
psql $DATABASE_URL -c "SELECT message_id, role, LEFT(content, 100) FROM messages WHERE user_id = 'user-uuid-here' ORDER BY created_at DESC LIMIT 5;"
```

---

## Acceptance Criteria

✅ **AC1**: User can list pending tasks with natural language
- Message "Show my pending tasks" invokes `list_tasks` with `status="pending"`
- Returns formatted list with task IDs and titles

✅ **AC2**: User can list completed tasks with natural language
- Message "Show completed tasks" invokes `list_tasks` with `status="completed"`
- Returns formatted list of completed tasks

✅ **AC3**: Empty task list handled gracefully (T035)
- Empty array returns friendly message (e.g., "You have no pending tasks")
- No error message or technical details exposed
- Structured logging captures empty result scenario

✅ **AC4**: Structured logging captures all list operations (T036)
- Tool invocation logged: `tool_name`, `user_id`, `status_filter`, `correlation_id`
- Tool result logged: `task_count`, `success`, `correlation_id`
- Empty results logged with specific message

✅ **AC5**: Task formatting is user-friendly
- Tasks numbered in list format
- Each task shows title and ID
- Clear distinction between pending and completed (if both shown)

---

## Performance Benchmarks

| Metric | Target | Measured |
|--------|--------|----------|
| Response time (p95) | <3s | _TBD_ |
| First token latency | <1s | _TBD_ |
| MCP tool invocation | <300ms | _TBD_ |
| Database query | <50ms | _TBD_ |

---

## Edge Cases

### Edge Case 1: User with 0 Tasks Ever
**When**: New user sends "Show my tasks"
**Expected**: "You don't have any tasks yet. Create one by saying 'Add task to...'"

### Edge Case 2: User with 100+ Tasks
**When**: User has >100 tasks, sends "Show all tasks"
**Expected**:
- MCP server may paginate results (depends on MCP implementation)
- Assistant summarizes: "You have 100+ tasks. Would you like to filter by status?"
- Constitutional limit: Only last 20 messages shown (not task limit)

### Edge Case 3: Invalid Status Filter
**When**: User sends ambiguous request (rare - AI should interpret correctly)
**Expected**: AI defaults to showing all tasks or asks for clarification

---

## Known Limitations

⚠️ **SDK Installation Required**: Tests cannot run until ChatKit SDK, OpenAI Agents SDK, and MCP SDK are installed per `backend/requirements.txt`.

⚠️ **Natural Language Variability**: AI interpretation may vary based on phrasing. Test scenarios use specific phrases for consistency.

⚠️ **Task Formatting**: Assistant response formatting depends on OpenAI model's style. May vary between runs.

---

## Next Steps

After User Story 2 validated:
1. Proceed to User Story 3: Complete tasks via natural language
2. Implement User Story 4: Update/delete tasks via natural language

---

**Test Plan Status**: ✅ COMPLETE (ready for execution once SDKs installed)
**Last Updated**: 2026-01-13
**Related**: tasks.md (T033-T036), spec.md (US2), contracts/chatkit-sse-events.md
