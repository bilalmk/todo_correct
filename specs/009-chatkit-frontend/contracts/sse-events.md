# Server-Sent Events (SSE) Specification

**Feature**: 009-chatkit-frontend
**Contract**: SSE event types streamed from backend to frontend
**Date**: 2026-01-15

## Overview

This document defines the Server-Sent Events (SSE) format and event types streamed from the backend ChatKit server to the frontend client. All events follow the SSE protocol specification (RFC 6202).

## SSE Protocol Format

Each event consists of:
```
event: <event_type>
data: <json_payload>

(blank line terminates event)
```

**Example**:
```
event: thread.message.delta
data: {"type":"thread.message.delta","content":"Task created!"}

```

---

## Event Types

### 1. thread.message.delta

**Purpose**: Incremental text chunk from AI assistant response (streaming).

**Frequency**: Multiple events per response (one per chunk).

**Payload**:
```json
{
  "type": "thread.message.delta",
  "content": "partial text chunk",
  "message_id": "msg_abc123",
  "timestamp": "2026-01-15T14:30:00Z"
}
```

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | ✅ | Always "thread.message.delta" |
| `content` | string | ✅ | Partial text chunk (append to previous chunks) |
| `message_id` | string | ⚠️ | UUID of message (may be null until first chunk) |
| `timestamp` | string | ✅ | ISO 8601 timestamp |

**Client Handling**:
- Append `content` to accumulated text buffer
- Display progressively in chat interface
- Update UI on each chunk (throttle if needed)

**Example Flow**:
```
1. event: thread.message.delta
   data: {"type":"thread.message.delta","content":"I'll create "}

2. event: thread.message.delta
   data: {"type":"thread.message.delta","content":"that task "}

3. event: thread.message.delta
   data: {"type":"thread.message.delta","content":"for you."}
```

---

### 2. thread.message.completed

**Purpose**: AI assistant response finished streaming.

**Frequency**: Once per response (final event).

**Payload**:
```json
{
  "type": "thread.message.completed",
  "message_id": "msg_abc123",
  "content": "full message text",
  "timestamp": "2026-01-15T14:30:00Z"
}
```

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | ✅ | Always "thread.message.completed" |
| `message_id` | string | ✅ | UUID of completed message |
| `content` | string | ✅ | Full message text (for validation) |
| `timestamp` | string | ✅ | ISO 8601 timestamp |

**Client Handling**:
- Stop streaming animation
- Mark message as complete
- Persist to local state/cache
- Enable user input (if disabled during streaming)

---

### 3. tool.call.start

**Purpose**: MCP tool invocation begins (e.g., add_task, list_tasks).

**Frequency**: Once per tool call.

**Payload**:
```json
{
  "type": "tool.call.start",
  "tool_name": "add_task",
  "tool_call_id": "call_xyz789",
  "arguments": {
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  },
  "timestamp": "2026-01-15T14:30:00Z"
}
```

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | ✅ | Always "tool.call.start" |
| `tool_name` | string | ✅ | MCP tool name (add_task, list_tasks, etc.) |
| `tool_call_id` | string | ✅ | Unique identifier for this tool call |
| `arguments` | object | ✅ | Tool parameters (varies by tool) |
| `timestamp` | string | ✅ | ISO 8601 timestamp |

**Client Handling**:
- Display "Executing [tool_name]..." indicator (optional)
- Log tool call for debugging
- Correlate with `tool.call.result` via `tool_call_id`

---

### 4. tool.call.result

**Purpose**: MCP tool execution completed with result or error.

**Frequency**: Once per tool call (follows `tool.call.start`).

**Payload (Success)**:
```json
{
  "type": "tool.call.result",
  "tool_call_id": "call_xyz789",
  "tool_name": "add_task",
  "success": true,
  "result": {
    "id": 123,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-01-15T14:30:00Z"
  },
  "timestamp": "2026-01-15T14:30:01Z"
}
```

**Payload (Error)**:
```json
{
  "type": "tool.call.result",
  "tool_call_id": "call_xyz789",
  "tool_name": "add_task",
  "success": false,
  "error": "Task title is required",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2026-01-15T14:30:01Z"
}
```

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | ✅ | Always "tool.call.result" |
| `tool_call_id` | string | ✅ | Matches `tool.call.start.tool_call_id` |
| `tool_name` | string | ✅ | MCP tool name |
| `success` | boolean | ✅ | true if tool succeeded, false if error |
| `result` | object | ⚠️ | Tool output (only if success=true) |
| `error` | string | ⚠️ | Error message (only if success=false) |
| `error_code` | string | ⚠️ | Error code (only if success=false) |
| `timestamp` | string | ✅ | ISO 8601 timestamp |

**Client Handling**:
- If `success=true` and `tool_name` is task-related:
  - Emit `TaskEvent` to trigger dashboard refresh
  - Show success toast (optional)
- If `success=false`:
  - Log error for debugging
  - Do NOT show error toast (AI will explain error in message)

---

### 5. error

**Purpose**: Fatal error occurred (connection lost, backend failure, etc.).

**Frequency**: Once per error (terminates stream).

**Payload**:
```json
{
  "type": "error",
  "error": {
    "message": "Unable to process your message. Please try again.",
    "code": "CHAT_STREAMING_ERROR",
    "correlation_id": "7f3d8c90-1234-5678-9abc-def012345678"
  },
  "timestamp": "2026-01-15T14:30:00Z"
}
```

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | ✅ | Always "error" |
| `error.message` | string | ✅ | User-facing error message |
| `error.code` | string | ✅ | Machine-readable error code |
| `error.correlation_id` | string | ✅ | UUID for tracing in logs |
| `timestamp` | string | ✅ | ISO 8601 timestamp |

**Client Handling**:
- Display error toast with message
- Log correlation_id for support tickets
- Trigger auto-retry (exponential backoff: 1s, 2s, 4s)
- Show "Retry" button if auto-retry exhausted

**Error Codes**:
| Code | Meaning | User Action |
|------|---------|-------------|
| `CHAT_STREAMING_ERROR` | Backend service failure | Retry automatically, then manual retry |
| `BACKEND_UNAVAILABLE` | Backend server unreachable | Wait and retry |
| `RATE_LIMIT_EXCEEDED` | Too many requests (20/min) | Wait `retry_after` seconds |
| `AUTHENTICATION_FAILED` | JWT token expired/invalid | Redirect to login |
| `MCP_SERVER_UNAVAILABLE` | MCP server unreachable | Retry automatically |

---

## Event Sequence Examples

### Example 1: Simple Task Creation

```
User: "Add a task to buy groceries"
Backend:

1. event: thread.message.delta
   data: {"type":"thread.message.delta","content":"I'll create that task for you."}

2. event: tool.call.start
   data: {"type":"tool.call.start","tool_name":"add_task","tool_call_id":"call_001","arguments":{"title":"Buy groceries"}}

3. event: tool.call.result
   data: {"type":"tool.call.result","tool_call_id":"call_001","success":true,"result":{"id":123,"title":"Buy groceries"}}

4. event: thread.message.delta
   data: {"type":"thread.message.delta","content":" Task created successfully with ID 123!"}

5. event: thread.message.completed
   data: {"type":"thread.message.completed","message_id":"msg_abc123"}
```

**Client Actions**:
- Step 1: Display "I'll create that task for you." (streaming)
- Step 2: (Optional) Show "Executing add_task..." indicator
- Step 3: Emit `TaskEvent{type:'task:created', taskId:123}` → Dashboard refreshes
- Step 4: Append " Task created successfully with ID 123!" to message
- Step 5: Stop streaming, enable input

---

### Example 2: List Tasks

```
User: "Show me all my pending tasks"
Backend:

1. event: tool.call.start
   data: {"type":"tool.call.start","tool_name":"list_tasks","tool_call_id":"call_002","arguments":{"status":"active"}}

2. event: tool.call.result
   data: {"type":"tool.call.result","tool_call_id":"call_002","success":true,"result":[{"id":1,"title":"Task 1"},{"id":2,"title":"Task 2"}]}

3. event: thread.message.delta
   data: {"type":"thread.message.delta","content":"You have 2 pending tasks:\n\n1. Task 1\n2. Task 2"}

4. event: thread.message.completed
   data: {"type":"thread.message.completed","message_id":"msg_def456"}
```

**Client Actions**:
- Step 1-2: (No dashboard update needed - read-only operation)
- Step 3-4: Display formatted task list in chat

---

### Example 3: Error Handling

```
User: "Mark task 999 as done"  (task doesn't exist)
Backend:

1. event: tool.call.start
   data: {"type":"tool.call.start","tool_name":"complete_task","tool_call_id":"call_003","arguments":{"task_id":999}}

2. event: tool.call.result
   data: {"type":"tool.call.result","tool_call_id":"call_003","success":false,"error":"Task 999 not found","error_code":"TASK_NOT_FOUND"}

3. event: thread.message.delta
   data: {"type":"thread.message.delta","content":"I couldn't find task 999. Please check the task ID and try again."}

4. event: thread.message.completed
   data: {"type":"thread.message.completed","message_id":"msg_ghi789"}
```

**Client Actions**:
- Step 2: Log error (do NOT show toast - AI will explain)
- Step 3-4: Display AI's error explanation in chat

---

## Performance Expectations

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Time to First Event** | <2 seconds | From POST to first `thread.message.delta` |
| **Event Latency** | <100ms | From backend emit to frontend receive |
| **Throughput** | 50 events/sec | Maximum sustainable rate per connection |
| **Connection Timeout** | 30 seconds | Idle timeout before connection closed |

---

## Error Recovery

### Connection Lost (Network Interruption)

**Detection**: No events received for >5 seconds.

**Client Action**:
1. Display "Connection lost. Retrying..." indicator
2. Auto-retry with exponential backoff (1s, 2s, 4s)
3. If 3 retries fail, show "Retry" button

### Partial Message (Incomplete Stream)

**Detection**: Connection closed before `thread.message.completed` event.

**Client Action**:
1. Display partial message with "(incomplete)" indicator
2. Show "Retry" button to resend message
3. Log correlation_id for debugging

### Duplicate Events (Network Replay)

**Detection**: Received `tool.call.result` with same `tool_call_id` twice.

**Client Action**:
- Ignore duplicate (idempotent handling)
- Log warning for monitoring

---

## Testing

### Test Cases

1. **Stream 100+ delta events** → Verify no dropped chunks
2. **Close connection mid-stream** → Verify partial message handling
3. **Rapid tool calls (5 in 1 second)** → Verify correct ordering
4. **Backend returns error event** → Verify error toast and retry button
5. **Rate limit (21st request)** → Verify countdown timer

### Mock SSE Server (for E2E tests)

```ts
// test/mocks/sse-server.ts
export function mockSSEStream(events: SSEEvent[]) {
  return new Response(
    new ReadableStream({
      start(controller) {
        for (const event of events) {
          controller.enqueue(`event: ${event.type}\n`);
          controller.enqueue(`data: ${JSON.stringify(event.data)}\n\n`);
        }
        controller.close();
      },
    }),
    {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
      },
    }
  );
}
```

---

## Summary

**SSE Event Types**:
1. `thread.message.delta` - Streaming text chunks
2. `thread.message.completed` - Response finished
3. `tool.call.start` - MCP tool invocation begins
4. `tool.call.result` - MCP tool result or error
5. `error` - Fatal error (terminates stream)

**Client Responsibilities**:
- Parse SSE events correctly
- Accumulate delta chunks into full message
- Emit TaskEvent on task-related tool results
- Handle errors gracefully with retry logic

**Backend Responsibilities** (Reference):
- Stream events in correct order
- Include correlation_id in all events
- Handle idempotent retry requests
- Close stream cleanly on completion
