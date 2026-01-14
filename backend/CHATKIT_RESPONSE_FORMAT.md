# ChatKit Response Format - Hybrid Text + Structured Data

**Date**: 2026-01-14
**Feature**: 008-chatkit-server-backend
**Status**: ✅ PRODUCTION READY

---

## Overview

The ChatKit endpoint now returns a **hybrid response format** that provides both:
1. **Conversational AI text** - Human-readable, natural language response
2. **Structured tool results** - Raw JSON data from MCP tool calls

This gives frontend developers the flexibility to:
- Display the AI's conversational response to users
- Use structured data for programmatic operations (e.g., rendering task lists, updating UI)

---

## Response Format

### Basic Structure

```typescript
interface ChatKitResponse {
  type: "message";
  role: "assistant";
  content: string;                    // AI's conversational response
  timestamp: string;                  // ISO 8601 timestamp
  tool_results?: ToolResult[];        // Optional: only present when tools are called
}

interface ToolResult {
  tool: string;                       // Tool name (e.g., "todo_list_tasks")
  arguments: Record<string, any>;     // Arguments passed to tool (excludes user_id)
  result: any;                        // Tool result (parsed JSON object or string)
}
```

---

## Response Examples

### Example 1: Task List Query (Single Tool Call)

**User Input**: `"List all my tasks"`

**Response**:
```json
{
  "type": "message",
  "role": "assistant",
  "content": "You have a total of 4 tasks:\n\n1. Task ID: 11 - \"Buy groceries\" (Pending)\n   Description: Milk, eggs, bread\n\n2. Task ID: 12 - \"Buy groceries\" (Pending)\n   Description: Milk, eggs, bread\n\n3. Task ID: 13 - \"Buy groceries\" (Pending)\n   Description: Milk, eggs, bread\n\n4. Task ID: 10 - \"Buy groceries1\" (Completed)\n   Description: Milk, eggs, bread, butter\n\nLet me know how else I can assist you.",
  "timestamp": "2026-01-14T13:21:36.421287+00:00",
  "tool_results": [
    {
      "tool": "todo_list_tasks",
      "arguments": {
        "status": "all"
      },
      "result": {
        "total": 4,
        "tasks": [
          {
            "task_id": 11,
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "completed": false,
            "created_at": "2026-01-08T10:30:11.995083+00:00",
            "updated_at": "2026-01-08T10:30:11.995083+00:00"
          },
          {
            "task_id": 12,
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "completed": false,
            "created_at": "2026-01-08T10:30:28.452851+00:00",
            "updated_at": "2026-01-08T10:30:28.452851+00:00"
          },
          {
            "task_id": 13,
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "completed": false,
            "created_at": "2026-01-08T10:37:51.593952+00:00",
            "updated_at": "2026-01-08T10:37:51.593952+00:00"
          },
          {
            "task_id": 10,
            "title": "Buy groceries1",
            "description": "Milk, eggs, bread, butter",
            "completed": true,
            "created_at": "2026-01-05T08:28:02.698451+00:00",
            "updated_at": "2026-01-08T10:39:56.934058+00:00"
          }
        ]
      }
    }
  ]
}
```

**Frontend Usage**:
```typescript
// Display AI's conversational response
console.log(response.content);

// Use structured data to render task list
if (response.tool_results) {
  const listTasksResult = response.tool_results.find(tr => tr.tool === 'todo_list_tasks');
  if (listTasksResult && listTasksResult.result.tasks) {
    const tasks = listTasksResult.result.tasks;
    renderTaskList(tasks);  // Render task cards, table, etc.
  }
}
```

---

### Example 2: Multiple Tool Calls

**User Input**: `"Add a task 'Test multiple tools' then list all my tasks"`

**Response**:
```json
{
  "type": "message",
  "role": "assistant",
  "content": "Okay, I've added your task 'Test multiple tools' with the task ID: 17. Now, here are all of your tasks:\n\n- Task 11: Buy groceries\n- Task 12: Buy groceries\n- Task 13: Buy groceries\n- Task 10: Buy groceries1 (Completed)\n- Task 17: Test multiple tools\n\nPlease let me know if I can help you manage these tasks further.",
  "timestamp": "2026-01-14T13:23:51.136512+00:00",
  "tool_results": [
    {
      "tool": "todo_add_task",
      "arguments": {
        "title": "Test multiple tools"
      },
      "result": {
        "task_id": 17,
        "title": "Test multiple tools",
        "description": null,
        "completed": false,
        "created_at": "2026-01-14T13:23:41.300498+00:00",
        "updated_at": "2026-01-14T13:23:41.300498+00:00"
      }
    },
    {
      "tool": "todo_list_tasks",
      "arguments": {
        "status": "all"
      },
      "result": {
        "total": 5,
        "tasks": [...]
      }
    }
  ]
}
```

**Frontend Usage**:
```typescript
// Display AI's conversational response
showChatMessage(response.content);

// Extract newly created task
if (response.tool_results) {
  const addTaskResult = response.tool_results.find(tr => tr.tool === 'todo_add_task');
  if (addTaskResult) {
    const newTask = addTaskResult.result;
    addTaskToUI(newTask);  // Add to task list UI
    showNotification(`Task ${newTask.task_id} created!`);
  }

  // Update full task list
  const listTasksResult = response.tool_results.find(tr => tr.tool === 'todo_list_tasks');
  if (listTasksResult) {
    updateTaskList(listTasksResult.result.tasks);
  }
}
```

---

### Example 3: Conversational (No Tools)

**User Input**: `"Hello! How are you?"`

**Response**:
```json
{
  "type": "message",
  "role": "assistant",
  "content": "Hello! I'm your virtual assistant, designed to help you manage your tasks. How can I assist you today?",
  "timestamp": "2026-01-14T13:23:01.263512+00:00"
}
```

**Frontend Usage**:
```typescript
// Display AI's conversational response
showChatMessage(response.content);

// No tool_results field when no tools are called
if (!response.tool_results) {
  console.log("Pure conversational response");
}
```

---

## Frontend Integration Guide

### React/Next.js Example

```typescript
import { useState } from 'react';

interface ChatKitResponse {
  type: "message";
  role: "assistant";
  content: string;
  timestamp: string;
  tool_results?: ToolResult[];
}

interface ToolResult {
  tool: string;
  arguments: Record<string, any>;
  result: any;
}

function ChatInterface() {
  const [messages, setMessages] = useState<ChatKitResponse[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);

  const sendMessage = async (userMessage: string) => {
    const response = await fetch('/api/chatkit/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ message: userMessage })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));

          // Handle message event
          if (data.type === 'message') {
            // Display AI response in chat
            setMessages(prev => [...prev, data]);

            // Process tool results for UI updates
            if (data.tool_results) {
              handleToolResults(data.tool_results);
            }
          }
        }
      }
    }
  };

  const handleToolResults = (toolResults: ToolResult[]) => {
    toolResults.forEach(result => {
      switch (result.tool) {
        case 'todo_list_tasks':
          setTasks(result.result.tasks);
          break;
        case 'todo_add_task':
          setTasks(prev => [...prev, result.result]);
          break;
        case 'todo_complete_task':
          setTasks(prev => prev.map(t =>
            t.task_id === result.result.task_id ? result.result : t
          ));
          break;
        case 'todo_delete_task':
          setTasks(prev => prev.filter(t => t.task_id !== result.result.task_id));
          break;
        case 'todo_update_task':
          setTasks(prev => prev.map(t =>
            t.task_id === result.result.task_id ? result.result : t
          ));
          break;
      }
    });
  };

  return (
    <div className="flex">
      {/* Chat interface */}
      <div className="chat-panel">
        {messages.map((msg, i) => (
          <div key={i} className="message">
            <p>{msg.content}</p>
            <span>{msg.timestamp}</span>
          </div>
        ))}
      </div>

      {/* Task list (auto-updated from tool results) */}
      <div className="task-panel">
        <h2>Your Tasks</h2>
        {tasks.map(task => (
          <TaskCard key={task.task_id} task={task} />
        ))}
      </div>
    </div>
  );
}
```

---

## Implementation Details

### Backend Changes

**File**: `backend/src/chatkit/server.py`

**Key Changes**:
1. **Tool Result Capture** (lines 321-322, 370-384):
   - Created `tool_results = []` array before agent execution
   - Modified tool handler to capture results in closure
   - Parsed JSON string results into objects

2. **Response Event Construction** (lines 461-480):
   - Build response event with `content` and `timestamp`
   - Include `tool_results` array only if tools were called
   - Log tool call count for debugging

**Code Snippet**:
```python
# Track tool calls and their results
tool_results = []

def create_tool_handler(tool_name_capture: str):
    async def on_invoke_tool(ctx: Any, args: str) -> str:
        # ... call MCP tool ...
        result = await mcp_client.call_tool(tool_name_capture, parsed_args)

        # Parse result if it's a JSON string
        parsed_result = result
        if isinstance(result, str):
            try:
                parsed_result = json_module.loads(result)
            except json_module.JSONDecodeError:
                parsed_result = result

        # Capture structured tool result for response
        tool_results.append({
            "tool": tool_name_capture,
            "arguments": {k: v for k, v in parsed_args.items() if k != "user_id"},
            "result": parsed_result
        })

        # Return result as string (for agent to process)
        if isinstance(result, dict):
            return json_module.dumps(result)
        return str(result)
    return on_invoke_tool

# ... after agent streaming completes ...

# Yield a clean response event with content and tool results
response_event = {
    "type": "message",
    "role": "assistant",
    "content": response_text,
    "timestamp": datetime.now(timezone.utc).isoformat()
}

# Include tool results if any tools were called
if tool_results:
    response_event["tool_results"] = tool_results

yield response_event
```

---

## Testing

### Test Files

1. **`test_hybrid_response.py`**: Basic hybrid response test
2. **`test_conversational_response.py`**: No tool calls test
3. **`test_multiple_tool_calls.py`**: Multiple tool calls test

### Running Tests

```bash
cd /mnt/e/giaic/learning/spec_kit_plus/todo_correct/backend

# Test hybrid response
uv run python ../test_hybrid_response.py

# Test conversational response
uv run python ../test_conversational_response.py

# Test multiple tool calls
uv run python ../test_multiple_tool_calls.py
```

### Expected Results

All tests should pass with:
- ✅ Single clean event returned
- ✅ `content` field with AI's conversational response
- ✅ `tool_results` array present when tools are called
- ✅ `tool_results` array contains parsed JSON objects (not strings)
- ✅ No `tool_results` field when no tools are called

---

## API Endpoint

### Endpoint

```
POST /api/chatkit/chat
```

### Headers

```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

### Request Body

```json
{
  "message": "List all my tasks"
}
```

### Response (Server-Sent Events)

```
event: message
data: {"type": "message", "role": "assistant", "content": "...", "timestamp": "...", "tool_results": [...]}
```

---

## Benefits

### For Users
- ✅ **Natural conversation**: AI responds in human-readable text
- ✅ **Rich UI updates**: Frontend can render structured data (task cards, lists, etc.)
- ✅ **Real-time sync**: Tool results update UI immediately

### For Developers
- ✅ **Flexibility**: Choose to display text, use structured data, or both
- ✅ **Type safety**: Structured tool results are predictable and type-safe
- ✅ **Debugging**: Tool results show exactly what the agent did
- ✅ **No parsing**: No need to parse AI text to extract data

### For System
- ✅ **Stateless**: All data comes from database/MCP, not in-memory state
- ✅ **User isolation**: user_id automatically injected, excluded from tool_results
- ✅ **Error handling**: Tool errors captured in tool_results array

---

## Migration Guide

### Before (Old Format)

**Problem**: Frontend received 159 streaming events with internal metadata

```typescript
// Old: 159 events with metadata
async for event in stream:
  if event.type == 'response.output_text.delta':
    text += event.delta
  elif event.type == 'response.function_tool_call.done':
    // How to get tool result? Not in event!
```

### After (New Format)

**Solution**: Frontend receives 1 clean event with text + structured data

```typescript
// New: 1 clean event
const response = await getNextEvent(stream);
console.log(response.content);          // AI text
console.log(response.tool_results);     // Structured data
```

---

## Troubleshooting

### Issue: `tool_results` field is always present (even when empty)

**Fix**: The implementation only adds `tool_results` if the array is non-empty:

```python
if tool_results:
    response_event["tool_results"] = tool_results
```

### Issue: Tool results are JSON strings, not objects

**Fix**: Results are parsed automatically:

```python
if isinstance(result, str):
    try:
        parsed_result = json_module.loads(result)
    except json_module.JSONDecodeError:
        parsed_result = result
```

### Issue: `user_id` appears in tool arguments

**Fix**: `user_id` is excluded from captured arguments:

```python
"arguments": {k: v for k, v in parsed_args.items() if k != "user_id"}
```

---

## Future Enhancements

### Potential Improvements

1. **Streaming Tool Results**: Yield tool results as they happen (not just at the end)
2. **Tool Call Status**: Include `status: "in_progress" | "completed" | "failed"` for each tool
3. **Partial Results**: Stream partial results for long-running operations
4. **Tool Metadata**: Include execution time, retry count, etc.

### Example (Future)

```json
{
  "type": "message",
  "role": "assistant",
  "content": "Processing your request...",
  "timestamp": "2026-01-14T13:21:36.421287+00:00",
  "tool_results": [
    {
      "tool": "todo_list_tasks",
      "arguments": {"status": "all"},
      "status": "in_progress",
      "started_at": "2026-01-14T13:21:35.000000+00:00"
    }
  ]
}
```

---

## Related Documentation

- **[MCP_500_ERROR_FIX.md](../MCP_500_ERROR_FIX.md)**: Previous fix for user_id injection
- **[spec.md](../../specs/008-chatkit-server-backend/spec.md)**: Feature specification
- **[plan.md](../../specs/008-chatkit-server-backend/plan.md)**: Architecture plan
- **[tasks.md](../../specs/008-chatkit-server-backend/tasks.md)**: Implementation tasks

---

**Status**: ✅ PRODUCTION READY
**Last Updated**: 2026-01-14
**Author**: Claude Code (Sonnet 4.5)
