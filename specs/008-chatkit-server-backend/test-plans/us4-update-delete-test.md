# User Story 4 - Update and Delete Tasks via Chat Test Plan

**Feature**: 008-chatkit-server-backend
**User Story**: US4 - Update and Delete Tasks via Natural Language
**Task Reference**: T044, T045, T046, T047
**Date**: 2026-01-13

## Overview

This test plan validates that users can update task titles/descriptions or delete tasks using natural language commands. The chatbot should invoke `update_task` and `delete_task` MCP tools and confirm changes, or provide user-friendly error messages if operations fail.

## Prerequisites

Before running these tests:

1. ✅ MCP server running at `http://localhost:8001/mcp`
2. ✅ Backend server running at `http://localhost:8000`
3. ✅ ChatKit SDK, OpenAI Agents SDK, and MCP SDK installed
4. ✅ Valid OpenAI API key configured
5. ✅ User authenticated with valid JWT token
6. ✅ Database has sample tasks for testing

## Test Scenarios

### Scenario 1: Update Task Title (T044)

**Given**: User has pending task:
- Task ID 42: "Buy groceries" (status: pending)

**When**: User sends message "Update task 42 title to 'Buy organic groceries'"

**Then**:
1. **MCP Tool Invocation**:
   - System invokes `update_task` MCP tool
   - Parameters: `user_id`, `task_id=42`, `title="Buy organic groceries"`
   - Tool returns: `{"task_id": 42, "title": "Buy organic groceries", "description": "...", "status": "pending"}`

2. **SSE Events Streamed**:
   ```
   event: tool.call.start
   data: {"type":"tool.call.start","tool_name":"update_task","tool_input":{"user_id":"...","task_id":42,"title":"Buy organic groceries"}}

   event: tool.call.result
   data: {"type":"tool.call.result","tool_name":"update_task","tool_output":{"task_id":42,"title":"Buy organic groceries"},"success":true}

   event: thread.message.completed
   data: {"message":{"content":"✓ Task 42 title updated to 'Buy organic groceries'"}}
   ```

3. **Database Verification**:
   ```sql
   SELECT id, title FROM tasks WHERE id = 42;
   -- Expected: 42 | Buy organic groceries
   ```

4. **Structured Logging (T047)**:
   ```json
   {
     "correlation_id": "550e8400-...",
     "user_id": "abc123",
     "tool_name": "update_task",
     "task_id": 42,
     "title": "Buy organic groceries",
     "description": null,
     "success": true,
     "message": "update_task MCP tool execution completed: task 42 updated (title='Buy organic groceries')"
   }
   ```

**Expected Result**: ✅ Task 42 title updated, user receives confirmation

---

### Scenario 2: Update Task Description (T045)

**Given**: User has task:
- Task ID 42: "Buy groceries" (description: null)

**When**: User sends message "Add description 'Remember to check expiry dates' to task 42"

**Then**:
1. **MCP Tool Invocation**:
   - System invokes `update_task` MCP tool
   - Parameters: `user_id`, `task_id=42`, `description="Remember to check expiry dates"`
   - Tool returns: Updated task with new description

2. **Structured Logging (T047)**:
   ```json
   {
     "tool_name": "update_task",
     "task_id": 42,
     "title": null,
     "description": "Remember to check expiry dates",
     "success": true,
     "message": "update_task MCP tool execution completed: task 42 updated (description='Remember to check expiry dates')"
   }
   ```

3. **Database Verification**:
   ```sql
   SELECT id, description FROM tasks WHERE id = 42;
   -- Expected: 42 | Remember to check expiry dates
   ```

**Expected Result**: ✅ Task 42 description updated

---

### Scenario 3: Update Both Title and Description

**Given**: User has task ID 42

**When**: User sends "Update task 42: title 'Buy organic groceries' and description 'Farmers market'"

**Then**:
1. **MCP Tool Invocation**:
   - Parameters: `task_id=42`, `title="Buy organic groceries"`, `description="Farmers market"`

2. **Structured Logging (T047)**:
   ```json
   {
     "tool_name": "update_task",
     "task_id": 42,
     "title": "Buy organic groceries",
     "description": "Farmers market",
     "message": "update_task MCP tool execution completed: task 42 updated (title='Buy organic groceries', description='Farmers market')"
   }
   ```

**Expected Result**: ✅ Both title and description updated simultaneously

---

### Scenario 4: Delete Task (T046)

**Given**: User has task:
- Task ID 42: "Buy groceries" (status: pending, deleted_at: null)

**When**: User sends message "Delete task 42"

**Then**:
1. **MCP Tool Invocation**:
   - System invokes `delete_task` MCP tool
   - Parameters: `user_id`, `task_id=42`
   - Tool returns: `{"task_id": 42, "deleted": true}`

2. **SSE Events Streamed**:
   ```
   event: tool.call.start
   data: {"type":"tool.call.start","tool_name":"delete_task","tool_input":{"user_id":"...","task_id":42}}

   event: tool.call.result
   data: {"type":"tool.call.result","tool_name":"delete_task","tool_output":{"task_id":42,"deleted":true},"success":true}

   event: thread.message.completed
   data: {"message":{"content":"✓ Task 42 has been deleted"}}
   ```

3. **Database Verification** (Soft Delete):
   ```sql
   SELECT id, title, deleted_at FROM tasks WHERE id = 42;
   -- Expected: 42 | Buy groceries | 2026-01-13 14:30:00 (timestamp populated)
   ```

4. **Structured Logging (T047)**:
   ```json
   {
     "correlation_id": "550e8400-...",
     "user_id": "abc123",
     "tool_name": "delete_task",
     "task_id": 42,
     "success": true,
     "message": "delete_task MCP tool execution completed: task 42 soft-deleted"
   }
   ```

**Expected Result**: ✅ Task 42 soft-deleted (deleted_at timestamp set), not hard deleted

---

### Scenario 5: Update Non-Existent Task (Error Handling)

**Given**: User database does not contain task ID 999

**When**: User sends "Update task 999 title to 'New title'"

**Then**:
1. **MCP Tool Invocation**:
   - System invokes `update_task` MCP tool
   - Parameters: `user_id`, `task_id=999`, `title="New title"`
   - Tool returns: `{"error": "Task 999 not found", "success": false}`

2. **Structured Logging**:
   ```json
   {
     "tool_name": "update_task",
     "task_id": 999,
     "success": false,
     "error": "Task 999 not found",
     "message": "update_task MCP tool failed: Task 999 not found"
   }
   ```
   - Log level: WARNING (not ERROR)

3. **Assistant Response**: "I couldn't find task 999. Please check the task ID and try again."

**Expected Result**: ⚠️ User-friendly error message, no exception thrown

---

### Scenario 6: Delete Non-Existent Task (Error Handling)

**Given**: User database does not contain task ID 999

**When**: User sends "Delete task 999"

**Then**:
1. **MCP Tool Invocation**:
   - Tool returns: `{"error": "Task 999 not found", "success": false}`

2. **Structured Logging**: Same as Scenario 5, WARNING level

3. **Assistant Response**: "I couldn't find task 999 to delete."

**Expected Result**: ⚠️ User-friendly error message

---

### Scenario 7: Natural Language Variations

**Update Variations**:
- "Change task 42 title to X"
- "Rename task 42 to X"
- "Modify task 42 description to X"
- "Set task 42 description as X"

**Delete Variations**:
- "Remove task 42"
- "Get rid of task 42"
- "Delete the task 42"
- "Trash task 42"

**Expected**: All variations invoke correct MCP tool

---

## Manual Testing Steps

### Setup

```bash
# Seed database
psql $DATABASE_URL <<EOF
INSERT INTO tasks (user_id, title, description, completed) VALUES
  ('user-uuid', 'Buy groceries', 'Milk and eggs', false),  -- ID 42
  ('user-uuid', 'Submit report', null, false);             -- ID 43
EOF

export TOKEN="eyJhbGc..."
```

### Test Execution

```bash
# Scenario 1: Update title
curl -N -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Update task 42 title to Buy organic groceries"}' \
     http://localhost:8000/api/chatkit/chat

# Scenario 2: Update description
curl -N -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Add description Remember to check expiry dates to task 42"}' \
     http://localhost:8000/api/chatkit/chat

# Scenario 4: Delete task
curl -N -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Delete task 42"}' \
     http://localhost:8000/api/chatkit/chat

# Scenario 5: Update non-existent task
curl -N -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Update task 999 title to New title"}' \
     http://localhost:8000/api/chatkit/chat
```

### Database Verification

```bash
# Check task updates
psql $DATABASE_URL -c "SELECT id, title, description, deleted_at FROM tasks WHERE id = 42;"

# Verify soft delete (deleted_at should be populated)
psql $DATABASE_URL -c "SELECT id, deleted_at IS NOT NULL as is_deleted FROM tasks WHERE id = 42;"
```

### Log Verification (T047)

```bash
# Check update_task logs
tail -f backend/logs/chatkit.log | jq 'select(.tool_name == "update_task")'

# Check delete_task logs
tail -f backend/logs/chatkit.log | jq 'select(.tool_name == "delete_task")'
```

---

## Acceptance Criteria

✅ **AC1**: Update task title via natural language (T044)
- Message updates title successfully
- Database reflects new title
- Confirmation message sent to user

✅ **AC2**: Update task description via natural language (T045)
- Message updates description successfully
- Database reflects new description

✅ **AC3**: Delete task via natural language (T046)
- Message soft-deletes task (deleted_at timestamp)
- **NOT hard delete** (data preserved)
- Confirmation message sent to user

✅ **AC4**: Structured logging for update/delete (T047)
- update_task logged with: task_id, title, description, success
- delete_task logged with: task_id, success
- Errors logged at WARNING level with correlation_id

✅ **AC5**: Error handling for non-existent tasks
- User-friendly error messages
- No technical details exposed
- Structured logging captures failures

---

## Performance Benchmarks

| Metric | Target | Measured |
|--------|--------|----------|
| Update response time (p95) | <2s | _TBD_ |
| Delete response time (p95) | <1.5s | _TBD_ |
| MCP tool invocation | <200ms | _TBD_ |
| Database update | <50ms | _TBD_ |

---

## Edge Cases

**Edge Case 1**: Update with empty title/description
- Should validate minimum length or reject gracefully

**Edge Case 2**: Delete already-deleted task (idempotent)
- Should acknowledge without error

**Edge Case 3**: Update task belonging to different user
- User isolation: should return "task not found"

---

**Test Plan Status**: ✅ COMPLETE
**Last Updated**: 2026-01-13
**Related**: tasks.md (T042-T047), spec.md (US4)
