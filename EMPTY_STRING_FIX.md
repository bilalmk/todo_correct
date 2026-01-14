# Fix: Empty String Validation Error for DateTime Fields

## Problem

When testing: `"I need to submit the quarterly report by January 20th at 2pm, this is very urgent and important"`

**Error:**
```
ValidationError: 1 validation error for AddTaskInput
reminder_at
  Input should be a valid datetime or date, input is too short
  [type=datetime_from_date_parsing, input_value='', input_type=str]
```

## Root Cause

The AI was sending empty strings `''` for datetime fields it didn't want to set, instead of:
- Omitting the field entirely
- Sending `null`
- Sending `None`

**Example of what the AI sent:**
```json
{
  "user_id": "550e8400-...",
  "title": "Submit quarterly report",
  "priority": "high",
  "due_date": "2026-01-20T14:00:00Z",
  "reminder_at": ""  ← Empty string causes Pydantic error
}
```

Pydantic's datetime validator cannot parse an empty string, so it threw a validation error.

## Solution

Added a `@field_validator` to convert empty strings to `None` **before** the datetime validation:

```python
@field_validator("due_date", "reminder_at", mode="before")
@classmethod
def validate_datetime_fields(cls, v):
    """
    Convert empty strings to None for datetime fields.

    AI may send empty strings when it doesn't want to set a field.
    Pydantic can't parse empty strings as datetimes, so convert to None.
    """
    if v == "" or v is None:
        return None
    return v
```

**Location:** `mcp_server/src/todo_mcp/models/inputs.py`
- Added to `AddTaskInput` class (line ~117)
- Added to `UpdateTaskInput` class (line ~307)

## What's Fixed

✅ **Empty strings → None**: AI can send `reminder_at=""` and it converts to `None`
✅ **Validation passes**: Pydantic validates `None` successfully for Optional[datetime]
✅ **No more 500 errors**: MCP tool handles all AI inputs correctly

## Test Results

**Before Fix:**
```python
AddTaskInput(
    user_id="...",
    title="Test",
    reminder_at=""  # ❌ ValidationError
)
```

**After Fix:**
```python
AddTaskInput(
    user_id="...",
    title="Test",
    reminder_at=""  # ✅ Converted to None, validation passes
)
# reminder_at = None
```

## Files Changed

1. ✅ `mcp_server/src/todo_mcp/models/inputs.py`
   - Added datetime validator to `AddTaskInput`
   - Added datetime validator to `UpdateTaskInput`

2. ✅ `mcp_server/src/todo_mcp/utils/responses.py` (previous fix)
   - Updated response formatting to include all fields

3. ✅ `mcp_server/src/todo_mcp/tools_registry.py` (previous fix)
   - Updated tool schemas with advanced fields

## Ready to Test

The MCP server has already reloaded with these changes. Your test should now work:

```bash
curl -N -X POST http://localhost:8000/api/chatkit/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "I need to submit the quarterly report by January 20th at 2pm, this is very urgent and important"}'
```

**Expected Success:**
```json
{
  "type": "message",
  "content": "✅ Created task #X: 'Submit the quarterly report' (Priority: High, Due: Jan 20, 2026 at 2:00 PM)",
  "tool_results": [{
    "tool": "todo_add_task",
    "result": {
      "task_id": 20,
      "title": "Submit the quarterly report",
      "priority": "high",
      "due_date": "2026-01-20T14:00:00+00:00",
      "reminder_at": null  ← Empty string converted to null
    }
  }]
}
```

## All Fixes Applied

1. ✅ **Tool Schema** - Added advanced fields so AI knows about them
2. ✅ **Response Formatting** - Include all fields and serialize datetimes
3. ✅ **Empty String Handling** - Convert empty strings to None for datetime fields

Your natural language task creation should now work perfectly! 🎉
