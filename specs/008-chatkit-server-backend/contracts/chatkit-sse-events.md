# ChatKit SSE Event Schema

Server-Sent Events (SSE) stream format for `/api/chatkit/chat` endpoint.

## Overview

The ChatKit chat endpoint returns a `text/event-stream` response with Server-Sent Events (SSE). Each event represents a state change in the conversation: assistant message chunks, MCP tool invocations, or errors.

**Content-Type**: `text/event-stream`
**Character Encoding**: UTF-8
**Event Format**: JSON payload in `data:` field

---

## Event Types

### 1. `thread.message.delta`

**Description**: Incremental content chunk for assistant message (streaming response).
**Frequency**: Multiple events per assistant message (one chunk per token/word).
**Use Case**: Display assistant response in real-time as it's generated.

**Format**:
```
event: thread.message.delta
data: {"type":"thread.message.delta","delta":{"role":"assistant","content":"Sure, I can help"},"thread_id":"550e8400-e29b-41d4-a716-446655440000","message_id":"660e8400-e29b-41d4-a716-446655440001"}
```

**JSON Schema**:
```json
{
  "type": "thread.message.delta",
  "delta": {
    "role": "assistant",
    "content": "Sure, I can help you add a task"
  },
  "thread_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_id": "660e8400-e29b-41d4-a716-446655440001"
}
```

**Fields**:
- `type`: Always `"thread.message.delta"`
- `delta.role`: Always `"assistant"`
- `delta.content`: Text chunk (partial sentence or word)
- `thread_id`: Conversation UUID
- `message_id`: Unique UUID for this assistant message

**Client Handling**: Append `delta.content` to message buffer, display incrementally.

---

### 2. `thread.message.completed`

**Description**: Assistant message streaming completed successfully.
**Frequency**: Once per assistant message (final event).
**Use Case**: Mark message as complete, stop spinner/loading indicator.

**Format**:
```
event: thread.message.completed
data: {"type":"thread.message.completed","message":{"message_id":"660e8400-e29b-41d4-a716-446655440001","role":"assistant","content":"Sure, I can help you add a task. What would you like to call it?","created_at":"2026-01-08T10:30:00Z","is_complete":true},"thread_id":"550e8400-e29b-41d4-a716-446655440000"}
```

**JSON Schema**:
```json
{
  "type": "thread.message.completed",
  "message": {
    "message_id": "660e8400-e29b-41d4-a716-446655440001",
    "role": "assistant",
    "content": "Sure, I can help you add a task. What would you like to call it?",
    "created_at": "2026-01-08T10:30:00Z",
    "is_complete": true
  },
  "thread_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Fields**:
- `type`: Always `"thread.message.completed"`
- `message.message_id`: UUID of completed message
- `message.role`: Always `"assistant"`
- `message.content`: Full message text
- `message.created_at`: ISO 8601 timestamp (UTC)
- `message.is_complete`: Always `true` (false only if interrupted mid-stream)
- `thread_id`: Conversation UUID

**Client Handling**: Save message to local state, re-enable input field for next user message.

---

### 3. `tool.call.start`

**Description**: AI agent invoked an MCP tool (e.g., add_task, list_tasks).
**Frequency**: Once per MCP tool invocation.
**Use Case**: Display "Adding task..." loading indicator.

**Format**:
```
event: tool.call.start
data: {"type":"tool.call.start","tool_name":"add_task","tool_input":{"user_id":"550e8400-e29b-41d4-a716-446655440000","title":"Buy groceries","description":"Milk, eggs, bread"},"thread_id":"550e8400-e29b-41d4-a716-446655440000"}
```

**JSON Schema**:
```json
{
  "type": "tool.call.start",
  "tool_name": "add_task",
  "tool_input": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  },
  "thread_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Fields**:
- `type`: Always `"tool.call.start"`
- `tool_name`: MCP tool name (add_task, list_tasks, complete_task, update_task, delete_task)
- `tool_input`: Tool parameters (varies by tool)
- `thread_id`: Conversation UUID

**Client Handling**: Show tool invocation UI (e.g., "🔧 Adding task...").

---

### 4. `tool.call.result`

**Description**: MCP tool execution completed with result.
**Frequency**: Once per MCP tool invocation (after tool.call.start).
**Use Case**: Display tool result (task ID, success message).

**Format**:
```
event: tool.call.result
data: {"type":"tool.call.result","tool_name":"add_task","tool_output":{"task_id":42,"title":"Buy groceries","status":"pending"},"success":true,"thread_id":"550e8400-e29b-41d4-a716-446655440000"}
```

**JSON Schema**:
```json
{
  "type": "tool.call.result",
  "tool_name": "add_task",
  "tool_output": {
    "task_id": 42,
    "title": "Buy groceries",
    "status": "pending"
  },
  "success": true,
  "thread_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Fields**:
- `type`: Always `"tool.call.result"`
- `tool_name`: MCP tool name
- `tool_output`: Tool return value (varies by tool)
- `success`: Boolean (true if tool succeeded, false if error)
- `thread_id`: Conversation UUID

**Client Handling**: Hide loading indicator, display result (e.g., "✓ Task 42 created").

---

### 5. `error`

**Description**: Error occurred during message processing.
**Frequency**: Once per error (terminates stream).
**Use Case**: Display error message to user, log correlation ID.

**Format**:
```
event: error
data: {"type":"error","error":{"message":"Task service temporarily unavailable, please try again later","code":"MCP_CONNECTION_FAILED","correlation_id":"770e8400-e29b-41d4-a716-446655440002"},"thread_id":"550e8400-e29b-41d4-a716-446655440000"}
```

**JSON Schema**:
```json
{
  "type": "error",
  "error": {
    "message": "Task service temporarily unavailable, please try again later",
    "code": "MCP_CONNECTION_FAILED",
    "correlation_id": "770e8400-e29b-41d4-a716-446655440002"
  },
  "thread_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Fields**:
- `type`: Always `"error"`
- `error.message`: User-friendly error message
- `error.code`: Machine-readable error code (MCP_CONNECTION_FAILED, OPENAI_RATE_LIMIT, etc.)
- `error.correlation_id`: Correlation ID for support/debugging
- `thread_id`: Conversation UUID

**Client Handling**: Display error message, close stream, enable retry.

**Error Codes**:
- `MCP_CONNECTION_FAILED`: MCP server unreachable
- `OPENAI_RATE_LIMIT`: OpenAI API rate limit exceeded
- `OPENAI_API_ERROR`: OpenAI API error (network, timeout, etc.)
- `DATABASE_ERROR`: Database operation failed
- `MESSAGE_TOO_LONG`: Message truncated (exceeds 10,000 chars)

---

## Stream Lifecycle

```
1. Client: POST /api/chatkit/chat {"message": "Add task to buy groceries"}
2. Server: HTTP 200 with Content-Type: text/event-stream
3. Server: event: thread.message.delta (multiple chunks)
4. Server: event: tool.call.start (if MCP tool invoked)
5. Server: event: tool.call.result (tool execution result)
6. Server: event: thread.message.delta (more chunks after tool result)
7. Server: event: thread.message.completed (final event)
8. Stream closes (client can send next message)
```

**Alternative Flow (Error)**:
```
1. Client: POST /api/chatkit/chat {"message": "..."}
2. Server: HTTP 200 with Content-Type: text/event-stream
3. Server: event: thread.message.delta (partial response)
4. Server: event: error (MCP connection failed)
5. Stream closes
6. Client: Display error message with correlation ID
```

---

## Example: Full Chat Workflow

**Request**:
```bash
curl -N -H "Authorization: Bearer eyJhbGc..." \\
     -H "Content-Type: application/json" \\
     -d '{"message": "Add a task to buy groceries"}' \\
     http://localhost:8000/api/chatkit/chat
```

**Response Stream**:
```
event: thread.message.delta
data: {"type":"thread.message.delta","delta":{"role":"assistant","content":"Sure,"},"thread_id":"550e8400...","message_id":"660e8400..."}

event: thread.message.delta
data: {"type":"thread.message.delta","delta":{"role":"assistant","content":" I'll"},"thread_id":"550e8400...","message_id":"660e8400..."}

event: thread.message.delta
data: {"type":"thread.message.delta","delta":{"role":"assistant","content":" add"},"thread_id":"550e8400...","message_id":"660e8400..."}

event: thread.message.delta
data: {"type":"thread.message.delta","delta":{"role":"assistant","content":" that"},"thread_id":"550e8400...","message_id":"660e8400..."}

event: thread.message.delta
data: {"type":"thread.message.delta","delta":{"role":"assistant","content":" task"},"thread_id":"550e8400...","message_id":"660e8400..."}

event: thread.message.delta
data: {"type":"thread.message.delta","delta":{"role":"assistant","content":" for"},"thread_id":"550e8400...","message_id":"660e8400..."}

event: thread.message.delta
data: {"type":"thread.message.delta","delta":{"role":"assistant","content":" you."},"thread_id":"550e8400...","message_id":"660e8400..."}

event: tool.call.start
data: {"type":"tool.call.start","tool_name":"add_task","tool_input":{"user_id":"550e8400...","title":"Buy groceries","description":null},"thread_id":"550e8400..."}

event: tool.call.result
data: {"type":"tool.call.result","tool_name":"add_task","tool_output":{"task_id":42,"title":"Buy groceries","status":"pending"},"success":true,"thread_id":"550e8400..."}

event: thread.message.delta
data: {"type":"thread.message.delta","delta":{"role":"assistant","content":" ✓"},"thread_id":"550e8400...","message_id":"660e8400..."}

event: thread.message.delta
data: {"type":"thread.message.delta","delta":{"role":"assistant","content":" Task"},"thread_id":"550e8400...","message_id":"660e8400..."}

event: thread.message.delta
data: {"type":"thread.message.delta","delta":{"role":"assistant","content":" created"},"thread_id":"550e8400...","message_id":"660e8400..."}

event: thread.message.delta
data: {"type":"thread.message.delta","delta":{"role":"assistant","content":":"},"thread_id":"550e8400...","message_id":"660e8400..."}

event: thread.message.delta
data: {"type":"thread.message.delta","delta":{"role":"assistant","content":" Buy"},"thread_id":"550e8400...","message_id":"660e8400..."}

event: thread.message.delta
data: {"type":"thread.message.delta","delta":{"role":"assistant","content":" groceries"},"thread_id":"550e8400...","message_id":"660e8400..."}

event: thread.message.delta
data: {"type":"thread.message.delta","delta":{"role":"assistant","content":" (ID:"},"thread_id":"550e8400...","message_id":"660e8400..."}

event: thread.message.delta
data: {"type":"thread.message.delta","delta":{"role":"assistant","content":" 42)"},"thread_id":"550e8400...","message_id":"660e8400..."}

event: thread.message.completed
data: {"type":"thread.message.completed","message":{"message_id":"660e8400...","role":"assistant","content":"Sure, I'll add that task for you. ✓ Task created: Buy groceries (ID: 42)","created_at":"2026-01-08T10:30:00Z","is_complete":true},"thread_id":"550e8400..."}
```

---

## Client Implementation Notes

**JavaScript/TypeScript Example** (EventSource API):
```typescript
const eventSource = new EventSource('/api/chatkit/chat', {
  headers: { Authorization: `Bearer ${jwtToken}` },
  method: 'POST',
  body: JSON.stringify({ message: 'Add task to buy groceries' }),
});

eventSource.addEventListener('thread.message.delta', (event) => {
  const data = JSON.parse(event.data);
  appendToMessageBuffer(data.delta.content);
});

eventSource.addEventListener('tool.call.start', (event) => {
  const data = JSON.parse(event.data);
  showToolIndicator(data.tool_name);
});

eventSource.addEventListener('tool.call.result', (event) => {
  const data = JSON.parse(event.data);
  hideToolIndicator();
  if (data.success) {
    console.log(`Tool ${data.tool_name} succeeded:`, data.tool_output);
  }
});

eventSource.addEventListener('thread.message.completed', (event) => {
  const data = JSON.parse(event.data);
  finalizeMessage(data.message);
  eventSource.close();
});

eventSource.addEventListener('error', (event) => {
  const data = JSON.parse(event.data);
  showError(data.error.message, data.error.correlation_id);
  eventSource.close();
});
```

**Handling Interrupted Streams**:
- If stream closes before `thread.message.completed`: check `is_complete=false` in last saved message
- Display partial content with "Response interrupted" indicator
- Allow user to retry message

---

**Document Version**: 1.0
**Last Updated**: 2026-01-08
**Related**: chatkit-api.yaml (OpenAPI spec for endpoints)
