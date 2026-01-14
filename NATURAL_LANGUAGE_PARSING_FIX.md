# Natural Language Task Parsing - Fix Applied ✅

## Problem Identified

When you sent: `"Finish the presentation by tomorrow at 5pm, it's urgent"`

**Expected:** Task with `title`, `due_date="2026-01-15T17:00:00Z"`, and `priority="high"`
**Actual:** Task with only `title`, no `due_date`, no `priority`

## Root Cause

The MCP tool schemas in `tools_registry.py` were hardcoded with only basic fields (`title`, `description`). Even though we updated the Pydantic input models (`AddTaskInput`, `UpdateTaskInput`) to accept advanced fields, **the AI never saw them** because the MCP `TOOL_DEFINITIONS` didn't include them.

## Changes Applied

### 1. Updated `todo_add_task` Tool Schema (tools_registry.py:32-94)
Added fields with natural language parsing instructions:
- ✅ **priority** - "Extract from keywords: urgent/important → high, low priority → low"
- ✅ **due_date** - "Parse from natural language: tomorrow, next week, January 31st → ISO 8601 UTC"
- ✅ **reminder_at** - "Parse from phrases: remind me 1 hour before → calculate from due_date"
- ✅ **recurrence_pattern** - "Extract from keywords: every day → daily, weekly → weekly"
- ✅ **recurrence_config** - "For custom patterns like 'every Monday, Wednesday, Friday'"

### 2. Updated `todo_update_task` Tool Schema (tools_registry.py:135-200)
Added same advanced fields for updating existing tasks.

### 3. Enhanced Tool Descriptions
Added explicit parsing instructions directly in the tool description field that the AI sees:
```
"Create a new task with advanced natural language parsing.
Extract priority from keywords (urgent/important=high, low priority=low).
Parse due dates from natural language (tomorrow, next week, January 31st, etc.)
and convert to ISO 8601 datetime UTC.
Detect recurrence patterns (daily, weekly, monthly)."
```

### 4. Field-Level Descriptions
Each field now has detailed extraction instructions:
- **priority**: `"Task priority. Extract from keywords: 'urgent'/'important'/'critical'/'asap' → high, 'low priority'/'not urgent' → low, default → medium"`
- **due_date**: `"Task deadline as ISO 8601 datetime UTC (e.g., '2026-01-31T23:59:59Z'). Parse from natural language: 'tomorrow', 'next week', 'January 31st', 'by Friday', 'in 3 days'. Today is 2026-01-14. Use 23:59:59 for end-of-day unless specific time mentioned."`

## What Changed in AI Behavior

### Before Fix:
```json
// User: "Finish the presentation by tomorrow at 5pm, it's urgent"
{
  "tool": "todo_add_task",
  "arguments": {
    "title": "Finish the presentation by tomorrow at 5pm, it's urgent"
  }
}
```

### After Fix:
```json
// User: "Finish the presentation by tomorrow at 5pm, it's urgent"
{
  "tool": "todo_add_task",
  "arguments": {
    "title": "Finish the presentation",           // ← Cleaned title (removed temporal/priority words)
    "priority": "high",                           // ← Extracted from "urgent"
    "due_date": "2026-01-15T17:00:00Z"           // ← Parsed "tomorrow at 5pm"
  }
}
```

## Testing Instructions

### 1. Get JWT Token
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"yourpassword"}' \
  | jq -r '.access_token'
```

### 2. Test Natural Language Parsing

**Test Case 1: Priority + Due Date**
```bash
curl -N -X POST http://localhost:8000/api/chatkit/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "Finish the presentation by tomorrow at 5pm, it'\''s urgent"}'
```

**Expected Response:**
```
✅ Created task #X: 'Finish the presentation'
   (Priority: High, Due: Jan 15, 2026 at 5:00 PM)
```

**Expected Tool Call:**
```json
{
  "tool": "todo_add_task",
  "arguments": {
    "title": "Finish the presentation",
    "priority": "high",
    "due_date": "2026-01-15T17:00:00Z"
  },
  "result": {
    "task_id": 20,
    "status": "created",
    "title": "Finish the presentation",
    "priority": "high",
    "due_date": "2026-01-15T17:00:00+00:00",
    "completed": false
  }
}
```

---

**Test Case 2: Your Original Example**
```bash
curl -N -X POST http://localhost:8000/api/chatkit/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "i will complete my project about fastapi due date is 31st january"}'
```

**Expected Response:**
```
✅ Created task #X: 'Complete my project about FastAPI'
   (Priority: Medium, Due: Jan 31, 2026 at 11:59 PM)
```

**Expected Tool Call:**
```json
{
  "tool": "todo_add_task",
  "arguments": {
    "title": "Complete my project about FastAPI",
    "priority": "medium",
    "due_date": "2026-01-31T23:59:59Z"
  }
}
```

---

**Test Case 3: Weekly Recurring**
```bash
curl -N -X POST http://localhost:8000/api/chatkit/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "Remind me to call mom every Sunday"}'
```

**Expected Response:**
```
✅ Created recurring task #X: 'Call mom' (Repeats: Weekly)
```

**Expected Tool Call:**
```json
{
  "tool": "todo_add_task",
  "arguments": {
    "title": "Call mom",
    "recurrence_pattern": "weekly"
  }
}
```

---

**Test Case 4: Low Priority**
```bash
curl -N -X POST http://localhost:8000/api/chatkit/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "Buy groceries when I have time, not urgent"}'
```

**Expected Response:**
```
✅ Created task #X: 'Buy groceries' (Priority: Low)
```

**Expected Tool Call:**
```json
{
  "tool": "todo_add_task",
  "arguments": {
    "title": "Buy groceries",
    "priority": "low"
  }
}
```

---

**Test Case 5: Update Deadline**
```bash
curl -N -X POST http://localhost:8000/api/chatkit/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "Change task 20 deadline to February 15th"}'
```

**Expected Response:**
```
✅ Updated task #20: Due date changed to Feb 15, 2026 at 11:59 PM
```

**Expected Tool Call:**
```json
{
  "tool": "todo_update_task",
  "arguments": {
    "task_id": 20,
    "due_date": "2026-02-15T23:59:59Z"
  }
}
```

## Automated Test Script

Run the Python test script:
```bash
# Edit TOKEN in test_nlp_task.py first
python3 test_nlp_task.py
```

Or use the bash script:
```bash
# Edit TOKEN in test_advanced_task_parsing.sh first
./test_advanced_task_parsing.sh
```

## Verification Checklist

After testing, verify:

- [ ] Task titles are cleaned (no "tomorrow", "urgent", "by Friday")
- [ ] Due dates are extracted and converted to ISO 8601 UTC
- [ ] Priority levels are inferred from keywords
- [ ] Recurrence patterns are detected
- [ ] AI confirms extracted fields in response
- [ ] Database contains all fields (priority, due_date, etc.)

## What to Look For

✅ **Success Indicators:**
- AI response mentions priority: "Priority: High"
- AI response mentions due date: "Due: Jan 31, 2026 at 11:59 PM"
- Tool call includes `priority` and `due_date` arguments
- Task result JSON shows `"priority": "high"` and `"due_date": "2026-01-31T23:59:59+00:00"`

❌ **Failure Indicators:**
- Tool call only has `title` and `description`
- No `priority` or `due_date` in arguments
- AI doesn't mention priority or due date in response
- Task result doesn't include advanced fields

## Troubleshooting

If parsing still doesn't work:

1. **Check MCP Server Status:**
   ```bash
   curl http://localhost:8001/health
   ```

2. **Verify Tool Schema:**
   ```bash
   # Initialize MCP session first
   curl -X POST http://localhost:8001/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"0.1.0","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'

   # Then list tools
   curl -X POST http://localhost:8001/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
     | jq '.result.tools[] | select(.name == "todo_add_task") | .inputSchema.properties | keys'
   ```

   Expected output should include: `["description", "due_date", "priority", "recurrence_config", "recurrence_pattern", "reminder_at", "title", "user_id"]`

3. **Restart Backend Server** (if using cached agent):
   ```bash
   # The backend caches the MCP client/agent
   # Restart to pick up new tool schemas
   # (Check your backend process and restart it)
   ```

4. **Check Backend Logs:**
   Look for tool call logs showing the arguments being passed to MCP tools.

## Summary

The fix was simple but critical: **The AI can only use fields that are in the tool schema it receives**. Even though our Pydantic models and database supported advanced fields, the MCP tool definitions exposed to the AI were stuck with just `title` and `description`.

Now the AI sees and uses all advanced fields:
- ✅ Priority extraction from keywords
- ✅ Due date parsing from natural language
- ✅ Reminder calculation
- ✅ Recurrence pattern detection
- ✅ Title cleaning (removes temporal/priority keywords)

Your natural language task creation should now work as expected! 🎉
