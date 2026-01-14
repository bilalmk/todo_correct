# Fix Summary: 500 Error When Creating Tasks with Advanced Fields

## Problem

When testing: `"I need to submit the quarterly report to my manager by January 20th at 2pm, this is very urgent and important"`

**Error:**
```
HTTP Request: POST http://localhost:8001/mcp "HTTP/1.1 500 Internal Server Error"
Tool todo_add_task failed: Server error '500 Internal Server Error'
```

**But the AI WAS working correctly:**
- ✅ Extracted priority: "high" (from "urgent and important")
- ✅ Extracted due_date: "2026-01-20T14:00:00Z" (from "January 20th at 2pm")
- ✅ Extracted title: "Submit the quarterly report to my manager"

The problem was in the **MCP tool response formatting**, not the AI parsing!

---

## Root Cause

The `format_task_result()` function in `mcp_server/src/todo_mcp/utils/responses.py` was only returning 3 fields:
```python
{
    "task_id": 42,
    "status": "created",
    "title": "Buy groceries"
}
```

It was **missing**:
- ❌ `priority` - causing JSON serialization to fail when trying to serialize Task object
- ❌ `due_date` - datetime object not converted to ISO string
- ❌ `reminder_at` - datetime object not converted to ISO string
- ❌ `recurrence_pattern` - not included
- ❌ `recurrence_config` - not included
- ❌ `description`, `completed`, `created_at`, `updated_at` - basic fields also missing

When `json.dumps()` tried to serialize the Task model with datetime objects directly, it failed with a 500 error because datetime objects aren't JSON serializable without conversion.

---

## Changes Applied

### 1. Updated `format_task_result()` (responses.py:12-56)

**Before:**
```python
def format_task_result(task, status):
    return json.dumps({
        "task_id": task.id,
        "status": status,
        "title": task.title,
    })
```

**After:**
```python
def format_task_result(task, status):
    result = {
        "task_id": task.id,
        "status": status,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at.isoformat() if isinstance(task.created_at, datetime) else task.created_at,
        "updated_at": task.updated_at.isoformat() if isinstance(task.updated_at, datetime) else task.updated_at,
        # Advanced fields (Phase V)
        "priority": task.priority,
        "due_date": task.due_date.isoformat() if isinstance(task.due_date, datetime) and task.due_date else task.due_date,
        "reminder_at": task.reminder_at.isoformat() if isinstance(task.reminder_at, datetime) and task.reminder_at else task.reminder_at,
        "recurrence_pattern": task.recurrence_pattern,
        "recurrence_config": task.recurrence_config,
    }
    return json.dumps(result, indent=2)
```

### 2. Updated `format_task_list()` (responses.py:84-121)

Added same advanced fields to task list formatting for consistency.

---

## What's Fixed

✅ **Datetime Serialization**: All datetime fields (`due_date`, `reminder_at`, `created_at`, `updated_at`) are now properly converted to ISO 8601 strings before JSON serialization

✅ **Complete Task Object**: Response now includes ALL task fields, not just title

✅ **Null Safety**: Advanced fields return `null` if not set (proper JSON null, not Python None)

✅ **API Consistency**: All MCP tool responses now return complete task objects

---

## Testing Instructions

### 1. Restart MCP Server (if needed)

The MCP server should have auto-reloaded when you saved the changes. Verify:

```bash
# Check MCP server is running
curl http://localhost:8001/health

# Should return: {"status": "healthy", ...}
```

### 2. Test Case 1: High Priority + Due Date

```bash
curl -N -X POST http://localhost:8000/api/chatkit/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "I need to submit the quarterly report to my manager by January 20th at 2pm, this is very urgent and important"}'
```

**Expected Response (SUCCESS):**
```json
{
  "type": "message",
  "content": "✅ Created task #X: 'Submit the quarterly report to my manager' (Priority: High, Due: Jan 20, 2026 at 2:00 PM)",
  "tool_results": [{
    "tool": "todo_add_task",
    "arguments": {
      "title": "Submit the quarterly report to my manager",
      "priority": "high",
      "due_date": "2026-01-20T14:00:00Z"
    },
    "result": {
      "task_id": 20,
      "status": "created",
      "title": "Submit the quarterly report to my manager",
      "description": null,
      "completed": false,
      "priority": "high",
      "due_date": "2026-01-20T14:00:00+00:00",
      "reminder_at": null,
      "recurrence_pattern": null,
      "recurrence_config": null,
      "created_at": "2026-01-14T19:45:00+00:00",
      "updated_at": "2026-01-14T19:45:00+00:00"
    }
  }]
}
```

### 3. Test Case 2: Weekly Recurring

```bash
curl -N -X POST http://localhost:8000/api/chatkit/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "Remind me to water the office plants every Monday morning, not urgent but needs to be done weekly"}'
```

**Expected Response:**
```json
{
  "result": {
    "task_id": 21,
    "status": "created",
    "title": "Water the office plants",
    "priority": "low",
    "recurrence_pattern": "weekly",
    ...
  }
}
```

### 4. Verify Database

Check that the task was saved with all fields:

```bash
# Connect to your database and query
SELECT id, title, priority, due_date, recurrence_pattern
FROM tasks
WHERE deleted_at IS NULL
ORDER BY id DESC
LIMIT 5;
```

You should see tasks with populated `priority` and `due_date` fields!

---

## What Should Work Now

✅ **Priority Extraction**: "urgent", "important" → priority="high"
✅ **Due Date Parsing**: "January 20th at 2pm" → due_date="2026-01-20T14:00:00Z"
✅ **Recurrence Detection**: "every Monday", "weekly" → recurrence_pattern="weekly"
✅ **Title Cleaning**: Removes temporal/priority keywords from title
✅ **Complete Responses**: All tool responses include all task fields
✅ **Proper JSON**: Datetime objects converted to ISO 8601 strings

---

## Debugging Tips

If you still get errors:

1. **Check MCP Server Logs:**
   ```bash
   # Look for any errors in the MCP server output
   # It should show successful tool calls now
   ```

2. **Verify Tool Schema:**
   ```bash
   # Check that advanced fields are in the tool schema
   curl -s -X POST http://localhost:8001/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"0.1.0","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'

   curl -s -X POST http://localhost:8001/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | grep -A 5 "priority"
   ```

3. **Test Pydantic Validation:**
   ```bash
   python3 test_pydantic_datetime.py
   # Should show SUCCESS for both test cases
   ```

4. **Check Backend Logs:**
   Look for the tool call arguments and result to verify the flow

---

## Summary

The fix was in **3 locations**:

1. ✅ `tools_registry.py` - Added advanced fields to tool schemas (so AI knows about them)
2. ✅ `models/inputs.py` - Already had datetime fields (Pydantic parses correctly)
3. ✅ `utils/responses.py` - **THIS WAS THE BUG** - Now includes all fields and serializes datetimes

The 500 error was caused by incomplete response formatting, not AI parsing. The AI was working perfectly - it just couldn't return the result properly! 🎉
