# ChatKit Backend Server - Developer Quickstart

**Feature**: 008-chatkit-server-backend
**Date**: 2026-01-08
**Purpose**: Local development setup and testing guide

## Prerequisites

✅ Python 3.11+ installed
✅ PostgreSQL database running (Neon Serverless or local)
✅ MCP server running on `http://localhost:8001/mcp` (from `mcp_server/` directory)
✅ OpenAI API key (for OpenAI Agents SDK)
✅ Better Auth configured (JWT tokens available)

---

## Environment Setup

### 1. Install Dependencies

```bash
cd backend
pip install chatkit-sdk agents httpx mcp-sdk
# OR using requirements.txt after it's updated
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create or update `.env` file in `backend/` directory:

```env
# ===== EXISTING CONFIGURATION =====
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/todo_db

# Better Auth
BETTER_AUTH_SECRET=your-secret-here
BETTER_AUTH_JWKS_URL=http://localhost:3000/api/auth/jwks
BETTER_AUTH_ISSUER=http://localhost:3000

# CORS
CORS_ORIGINS=http://localhost:3000
FRONTEND_URL=http://localhost:3000

# ===== NEW CONFIGURATION (Phase III ChatKit) =====
# OpenAI Agents SDK
OPENAI_API_KEY=sk-proj-your-api-key-here
OPENAI_MODEL=gpt-4

# MCP Server
MCP_SERVER_URL=http://localhost:8001/mcp
MCP_CONNECTION_TIMEOUT=30

# ChatKit
CHATKIT_MESSAGE_LIMIT=10000
CHATKIT_HISTORY_LIMIT=20
```

### 3. Run Database Migrations

```bash
cd backend
alembic upgrade head
# Should see: "Running upgrade XXX -> YYY, add chatkit models"
```

Verify tables created:
```bash
psql $DATABASE_URL -c "\\dt"
# Should see: conversations, messages (among existing tables)
```

---

## Running Services

### Terminal 1: MCP Server

```bash
cd mcp_server
python -m todo_mcp.server

# Expected output:
# INFO:     MCP server running on http://localhost:8001/mcp
# INFO:     Tools registered: add_task, list_tasks, complete_task, update_task, delete_task
```

### Terminal 2: Backend Server

```bash
cd backend
uvicorn src.main:app --reload --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
# INFO:     ChatKit server initialized with MCP client at http://localhost:8001/mcp
```

### Terminal 3: Frontend (Optional, for full stack testing)

```bash
cd frontend
npm run dev

# Expected output:
# ➜  Local:   http://localhost:3000/
```

---

## Testing ChatKit Endpoints

### Get JWT Token

**Option 1**: Login via frontend (http://localhost:3000), copy JWT from localStorage
**Option 2**: Login via API:

```bash
curl -X POST http://localhost:3000/api/auth/login \\
     -H "Content-Type: application/json" \\
     -d '{"email":"user@example.com","password":"password123"}'

# Response: {"token":"eyJhbGc...","user":{...}}
```

Save token to variable:
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Test 1: Send Chat Message (Streaming Response)

```bash
curl -N -H "Authorization: Bearer $TOKEN" \\
     -H "Content-Type: application/json" \\
     -d '{"message": "Add a task to buy groceries"}' \\
     http://localhost:8000/api/chatkit/chat
```

**Expected Output** (SSE stream):
```
event: thread.message.delta
data: {"type":"thread.message.delta","delta":{"content":"Sure, I'll add that task for you."},...}

event: tool.call.start
data: {"type":"tool.call.start","tool_name":"add_task","tool_input":{"title":"Buy groceries"},...}

event: tool.call.result
data: {"type":"tool.call.result","tool_name":"add_task","tool_output":{"task_id":42},"success":true,...}

event: thread.message.completed
data: {"type":"thread.message.completed","message":{"content":"✓ Task created: Buy groceries (ID: 42)"},...}
```

### Test 2: List Tasks via Chat

```bash
curl -N -H "Authorization: Bearer $TOKEN" \\
     -H "Content-Type: application/json" \\
     -d '{"message": "Show me my pending tasks"}' \\
     http://localhost:8000/api/chatkit/chat
```

**Expected Output**: Assistant lists tasks retrieved via `list_tasks` MCP tool.

### Test 3: Complete Task via Chat

```bash
curl -N -H "Authorization: Bearer $TOKEN" \\
     -H "Content-Type: application/json" \\
     -d '{"message": "Mark task 42 as done"}' \\
     http://localhost:8000/api/chatkit/chat
```

**Expected Output**: Assistant confirms task completion via `complete_task` MCP tool.

### Test 4: Reset Conversation

```bash
curl -X DELETE -H "Authorization: Bearer $TOKEN" \\
     http://localhost:8000/api/chatkit/conversation

# Expected: HTTP 204 No Content
```

Verify soft delete:
```bash
psql $DATABASE_URL -c "SELECT conversation_id, deleted_at FROM conversations WHERE user_id='<your-user-id>';"
# Should see: deleted_at timestamp populated
```

---

## Architecture Overview

```
Frontend (React)          Backend (FastAPI)          MCP Server          OpenAI API
┌─────────────┐          ┌─────────────────┐       ┌──────────┐        ┌──────────┐
│ useChatKit  │─HTTP/SSE→│ ChatKitServer   │─MCP──→│ 5 Tools  │        │ Agents   │
│ (Phase III) │          │ - respond()     │       │ add_task │        │ SDK      │
│             │          │ - DB store      │       │ list_    │        │ gpt-4    │
│             │          │ - OpenAI agent  │       │ complete │        │          │
│             │          │                 │       │ update   │        │          │
│             │          │                 │       │ delete   │        │          │
└─────────────┘          └─────────────────┘       └──────────┘        └──────────┘
                                  │
                                  ▼
                          PostgreSQL (Neon)
                          ┌──────────────┐
                          │ conversations│
                          │ messages     │
                          │ tasks        │
                          │ users        │
                          └──────────────┘
```

---

## Key Files

| File Path | Purpose |
|-----------|---------|
| `backend/src/api/chatkit.py` | FastAPI routes (POST /api/chatkit/chat, DELETE /api/chatkit/conversation) |
| `backend/src/chatkit/server.py` | CustomChatKitServer extending ChatKitServer base class |
| `backend/src/chatkit/agent.py` | OpenAI Agents SDK agent initialization with MCP client |
| `backend/src/chatkit/store.py` | DatabaseThreadItemStore implementation (SQLModel) |
| `backend/src/chatkit/utils.py` | Retry logic, correlation ID helpers, error handling |
| `backend/src/models/conversation.py` | Conversation SQLModel (user_id, timestamps, soft delete) |
| `backend/src/models/message.py` | Message SQLModel (conversation_id, role, content, is_complete) |
| `backend/src/core/config.py` | Settings extended with OPENAI_API_KEY, MCP_SERVER_URL |

---

## Running Tests

```bash
cd backend

# Unit tests (ChatKitServer respond() logic)
pytest tests/unit/test_chatkit_server.py -v

# Integration tests (API endpoints, database persistence)
pytest tests/integration/test_chatkit_api.py -v
pytest tests/integration/test_chatkit_persistence.py -v

# E2E tests (full workflow with MCP tools)
pytest tests/e2e/test_chatkit_workflow.py -v

# All tests with coverage
pytest --cov=src.chatkit --cov-report=term-missing
```

**Expected Coverage**: 80%+ for ChatKit modules.

---

## Debugging

### Common Issues

| Symptom | Diagnosis | Solution |
|---------|-----------|----------|
| `MCP_CONNECTION_FAILED` error | MCP server not running or wrong URL | 1. Verify MCP server running: `curl http://localhost:8001/mcp`<br>2. Check `MCP_SERVER_URL` in `.env` |
| `OPENAI_RATE_LIMIT` error | OpenAI API rate limit exceeded | 1. Wait for rate limit reset<br>2. Check usage at platform.openai.com<br>3. Upgrade plan if needed |
| `INVALID_TOKEN` error | JWT token expired or invalid | 1. Re-login to get new token<br>2. Check `BETTER_AUTH_SECRET` matches frontend |
| `DATABASE_ERROR` in logs | Database connection failed | 1. Verify `DATABASE_URL` correct<br>2. Check PostgreSQL running<br>3. Run migrations: `alembic upgrade head` |
| Empty conversation history | Messages not persisting | 1. Check logs for database errors<br>2. Verify conversations/messages tables exist<br>3. Check user_id matches JWT token |

### Checking Logs

**Structured Logs** (JSON format with correlation IDs):
```bash
tail -f backend/logs/chatkit.log | jq
```

**Filter by Correlation ID**:
```bash
cat backend/logs/chatkit.log | jq 'select(.correlation_id == "550e8400...")'
```

**Watch Database Messages**:
```bash
psql $DATABASE_URL -c "SELECT message_id, role, LEFT(content, 50), created_at FROM messages ORDER BY created_at DESC LIMIT 10;"
```

---

## Next Steps

1. ✅ **Backend working** → Implement frontend ChatKit UI (separate feature)
2. ✅ **Frontend integrated** → Deploy to development environment
3. ✅ **Dev deployed** → Run stateless architecture validation test (restart server mid-conversation)
4. ✅ **Stateless validated** → Proceed to Phase IV (Kubernetes deployment)

---

**Document Version**: 1.0
**Last Updated**: 2026-01-08
**Related**: plan.md (implementation plan), data-model.md (database schema), chatkit-api.yaml (API spec)
