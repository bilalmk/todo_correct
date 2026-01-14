# Todo Application - Backend API

FastAPI backend with SQLModel ORM and PostgreSQL database for the Todo Evolution Hackathon.

## Database Schema

### Tables Overview

1. **users** - User accounts with authentication
2. **tasks** - Todo items with scheduling and recurrence
3. **tags** - Custom labels for task organization
4. **task_tags** - Many-to-many relationship between tasks and tags
5. **notifications** - Scheduled notifications for tasks

### Performance Indexes

**8 Specialized Indexes:**
1. `idx_tasks_user_completed` - User + completion status
2. `idx_tasks_user_priority` (PARTIAL) - High-priority tasks
3. `idx_tasks_user_due_date` (PARTIAL) - Tasks with due dates
4. `idx_tasks_due_reminders` (PARTIAL) - Upcoming reminders
5. `idx_tasks_fulltext_search` (GIN) - Full-text search
6. `idx_tags_user_name_unique` (UNIQUE, PARTIAL) - Unique tag names
7. `idx_notifications_pending` (PARTIAL) - Pending notifications
8. `idx_notifications_task_id` (PARTIAL) - Task-related notifications

**Performance Targets:** All queries < 100ms

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Seed database (optional)
python scripts/seed_database.py

# Run tests
pytest --cov=src
```

## Features Implemented

- ✅ User authentication with JWT
- ✅ Task CRUD with soft delete
- ✅ Priority levels (low, medium, high)
- ✅ Due dates and reminders
- ✅ Recurring tasks (daily, weekly, monthly, custom)
- ✅ Tags with colors and many-to-many relationships
- ✅ Full-text search with PostgreSQL GIN indexes
- ✅ Notifications system with multiple channels

## API Documentation

### Interactive Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Authentication

All task/tag endpoints require JWT authentication:
```
Authorization: Bearer <your_jwt_token>
```

### Endpoint Summary (15 Total)

#### Authentication Endpoints (2)
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

#### Task Endpoints (7)
- `POST /api/v1/{user_id}/tasks` - Create task
- `GET /api/v1/{user_id}/tasks` - List tasks (with filters & search)
- `GET /api/v1/{user_id}/tasks/{task_id}` - Get single task
- `PUT /api/v1/{user_id}/tasks/{task_id}` - Replace task (full update)
- `PATCH /api/v1/{user_id}/tasks/{task_id}` - Update task (partial)
- `PATCH /api/v1/{user_id}/tasks/{task_id}/complete` - Toggle completion
- `DELETE /api/v1/{user_id}/tasks/{task_id}` - Soft delete task

#### Tag Endpoints (5)
- `POST /api/v1/{user_id}/tags` - Create tag
- `GET /api/v1/{user_id}/tags` - List tags
- `GET /api/v1/{user_id}/tags/{tag_id}` - Get single tag
- `PUT /api/v1/{user_id}/tags/{tag_id}` - Update tag
- `DELETE /api/v1/{user_id}/tags/{tag_id}` - Soft delete tag

#### Task-Tag Endpoints (3)
- `POST /api/v1/{user_id}/tasks/{task_id}/tags` - Assign tag to task
- `GET /api/v1/{user_id}/tasks/{task_id}/tags` - List task tags
- `DELETE /api/v1/{user_id}/tasks/{task_id}/tags/{tag_id}` - Remove tag from task

### Example Requests

#### Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure123",
    "name": "John Doe"
  }'
```

#### Create Task with Advanced Fields
```bash
curl -X POST http://localhost:8000/api/v1/{user_id}/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Weekly team meeting",
    "description": "Discuss project progress",
    "priority": "high",
    "due_date": "2025-12-31T10:00:00Z",
    "reminder_at": "2025-12-30T09:00:00Z",
    "recurrence_pattern": "weekly",
    "recurrence_config": {
      "rrule": "FREQ=WEEKLY;BYDAY=MO",
      "interval": 1
    }
  }'
```

#### List Tasks with Filters
```bash
# Filter by status and priority, sort by due date
curl http://localhost:8000/api/v1/{user_id}/tasks?status=incomplete&priority=high&sort_by=due_date&order=asc \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Full-text search
curl http://localhost:8000/api/v1/{user_id}/tasks?search=meeting \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Filter by tag (multiple tags use OR logic)
curl http://localhost:8000/api/v1/{user_id}/tasks?tag=work&tag=urgent \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get untagged tasks
curl http://localhost:8000/api/v1/{user_id}/tasks?tag=none \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Query Parameters (List Tasks)

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `status` | string | Filter by completion (`complete`, `incomplete`) | `?status=incomplete` |
| `priority` | string | Filter by priority (`low`, `medium`, `high`) | `?priority=high` |
| `tag` | string[] | Filter by tag names (OR logic), use `none` for untagged | `?tag=work&tag=urgent` |
| `due_before` | datetime | Tasks due before this date (ISO 8601) | `?due_before=2025-12-31T00:00:00Z` |
| `due_after` | datetime | Tasks due after this date (ISO 8601) | `?due_after=2025-12-01T00:00:00Z` |
| `search` | string | Full-text search in title and description | `?search=meeting` |
| `sort_by` | string | Column to sort by (`created_at`, `due_date`, `priority`, `title`) | `?sort_by=due_date` |
| `order` | string | Sort order (`asc`, `desc`) | `?order=asc` |

### Response Examples

#### Task Response
```json
{
  "id": 1,
  "user_id": "uuid",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "priority": "high",
  "due_date": "2025-12-31T10:00:00Z",
  "reminder_at": "2025-12-30T09:00:00Z",
  "recurrence_pattern": "weekly",
  "recurrence_config": {
    "rrule": "FREQ=WEEKLY;BYDAY=MO,FR",
    "interval": 1
  },
  "tags": [
    {"id": 1, "name": "shopping", "color": "#FF5733"}
  ],
  "created_at": "2025-12-01T10:00:00Z",
  "updated_at": "2025-12-01T10:00:00Z"
}
```

#### Tag Response
```json
{
  "id": 1,
  "user_id": "uuid",
  "name": "work",
  "color": "#FF5733",
  "created_at": "2025-12-01T10:00:00Z",
  "updated_at": "2025-12-01T10:00:00Z"
}
```

### Error Responses

All errors follow this format:
```json
{
  "error": "Task not found",
  "code": "TASK_NOT_FOUND",
  "status": 404,
  "request_id": "req_abc123"
}
```

**Common Status Codes:**
- `200 OK` - Successful GET/PUT/PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing/invalid JWT
- `403 Forbidden` - User ID mismatch
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error

---

## ChatKit - AI-Powered Task Management (Phase III)

### Overview

ChatKit is an AI-powered conversational interface for task management using OpenAI Agents SDK and Model Context Protocol (MCP). Users can manage tasks through natural language commands.

**Features:**
- Natural language task management (add, list, complete, update, delete)
- Streaming responses via Server-Sent Events (SSE)
- Persistent conversation history (20-message limit)
- Stateless architecture (database-backed state)
- MCP tool integration for task operations

### Prerequisites

1. **Python 3.11+** (required for ChatKit SDK)
2. **OpenAI API Key** (for AI agent)
3. **MCP Server** (for task management tools)
4. **Neon PostgreSQL** (for conversation persistence)

### Environment Variables

Add these to your `.env` file:

```bash
# ChatKit Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
MCP_SERVER_URL=http://localhost:8001/mcp

# ChatKit Limits (Constitutional Requirements)
CHATKIT_HISTORY_LIMIT=20          # FR-007: 20-message history limit
CHATKIT_MESSAGE_LIMIT=10000       # FR-024: Content truncation at 10,000 chars

# Database Configuration (if not already set)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# Better Auth Configuration (if not already set)
BETTER_AUTH_SECRET=your-better-auth-secret-key
```

### Installation

```bash
# 1. Install ChatKit SDK and dependencies
pip install chatkit-sdk agents mcp httpx

# Or add to requirements.txt:
echo "chatkit-sdk>=0.1.0" >> requirements.txt
echo "agents>=0.1.0" >> requirements.txt
echo "mcp>=0.1.0" >> requirements.txt
echo "httpx>=0.25.0" >> requirements.txt

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run database migrations
alembic upgrade head

# This creates the conversation and message tables:
# - conversations (conversation_id, user_id, created_at, updated_at, deleted_at)
# - messages (message_id, conversation_id, user_id, role, content, is_complete, created_at, deleted_at)
```

### MCP Server Setup

The MCP server provides task management tools to the AI agent.

**Start MCP Server:**

```bash
# Navigate to MCP server directory
cd mcp_server

# Install dependencies
pip install -r requirements.txt

# Start MCP server
python -m src.todo_mcp

# Server should be running at http://localhost:8001/mcp
```

**MCP Tools Available:**
- `add_task(user_id, title, description)` - Create new task
- `list_tasks(user_id, status)` - List tasks (pending/completed)
- `complete_task(user_id, task_id)` - Mark task as completed
- `update_task(user_id, task_id, title?, description?)` - Update task
- `delete_task(user_id, task_id)` - Soft delete task

### Running ChatKit

```bash
# 1. Start backend server (in backend directory)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 2. Verify health check
curl http://localhost:8000/api/chatkit/health

# Expected response:
# {
#   "status": "healthy",
#   "mcp_server": "connected",
#   "database": "connected",
#   "timestamp": "2026-01-13T14:30:00Z"
# }
```

### ChatKit API Endpoints

#### 1. POST /api/chatkit/chat - Send chat message

**Request:**
```bash
curl -N -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Add task to buy groceries"}' \
     http://localhost:8000/api/chatkit/chat
```

**Response:** Server-Sent Events (SSE) stream
```
event: tool.call.start
data: {"type":"tool.call.start","tool_name":"add_task"}

event: tool.call.result
data: {"type":"tool.call.result","tool_name":"add_task","success":true}

event: thread.message.delta
data: {"type":"thread.message.delta","content":"Task created successfully!"}

event: thread.message.completed
data: {"type":"thread.message.completed"}
```

#### 2. DELETE /api/chatkit/conversation - Reset conversation

**Request:**
```bash
curl -X DELETE -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/chatkit/conversation
```

**Response:** 204 No Content

#### 3. GET /api/chatkit/health - Health check

**Request:**
```bash
curl http://localhost:8000/api/chatkit/health
```

**Response:**
```json
{
  "status": "healthy",
  "mcp_server": "connected",
  "database": "connected",
  "timestamp": "2026-01-13T14:30:00Z"
}
```

### Example Chat Interactions

**Add Task:**
```bash
curl -N -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Add task to read book"}' \
     http://localhost:8000/api/chatkit/chat
```

**List Tasks:**
```bash
curl -N -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Show me all my pending tasks"}' \
     http://localhost:8000/api/chatkit/chat
```

**Complete Task:**
```bash
curl -N -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Mark task 42 as done"}' \
     http://localhost:8000/api/chatkit/chat
```

**Update Task:**
```bash
curl -N -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Update task 42 title to Buy organic groceries"}' \
     http://localhost:8000/api/chatkit/chat
```

**Delete Task:**
```bash
curl -N -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Delete task 42"}' \
     http://localhost:8000/api/chatkit/chat
```

### Testing ChatKit

```bash
# Run ChatKit unit tests
pytest backend/tests/unit/test_chatkit_*.py -v

# Run ChatKit integration tests
pytest backend/tests/integration/test_chatkit_*.py -v

# Run ChatKit E2E tests
pytest backend/tests/e2e/test_chatkit_*.py -v

# Run all tests with coverage
pytest backend/tests/ --cov=backend/src/chatkit --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### ChatKit Architecture

**Constitutional Compliance:**
- **FR-007**: 20-message history limit (token budget management)
- **FR-016**: Structured logging with correlation IDs
- **FR-017**: User isolation on all database queries
- **FR-023**: Database connection pool (50 concurrent requests)
- **FR-024**: Content truncation at 10,000 characters
- **SC-002**: Stateless architecture (database-backed state)
- **SC-003**: Supports 50 concurrent requests
- **SC-006**: 100% correlation ID logging coverage

**Components:**
- `CustomChatKitServer` - Main server class extending ChatKitServer
- `DatabaseThreadItemStore` - Conversation persistence with SQLModel
- `RequestContext` - User ID + correlation ID for tracing
- Retry utilities - Exponential backoff (OpenAI), fixed delay (database)

**Database Tables:**
- `conversations` - Active conversation per user (unique constraint)
- `messages` - Conversation history (20-message limit per FR-007)

### Troubleshooting

**Issue: MCP server unreachable**
```bash
# Check MCP server health
curl http://localhost:8001/health

# Restart MCP server
cd mcp_server && python -m src.todo_mcp
```

**Issue: OpenAI API errors**
```bash
# Verify API key
echo $OPENAI_API_KEY

# Check logs for retry attempts (3x with exponential backoff)
tail -f backend/logs/chatkit.log | jq 'select(.tool_name)'
```

**Issue: Database connection errors**
```bash
# Verify database URL
echo $DATABASE_URL

# Test database connection
python -c "from src.core.database import async_engine; print(async_engine)"

# Run migrations
alembic upgrade head
```

**Issue: Conversation history not loading**
```bash
# Verify conversation exists
psql $DATABASE_URL -c "SELECT * FROM conversations WHERE deleted_at IS NULL;"

# Verify messages exist
psql $DATABASE_URL -c "SELECT COUNT(*) FROM messages WHERE deleted_at IS NULL;"
```

### Production Deployment

**Pre-deployment Checklist:**
1. ✅ Environment variables configured (.env file)
2. ✅ Database migrations applied (`alembic upgrade head`)
3. ✅ MCP server running and reachable
4. ✅ OpenAI API key valid
5. ✅ Health check endpoint returns 200 (`GET /api/chatkit/health`)
6. ✅ JWT authentication configured (Better Auth)
7. ✅ Database connection pool configured (10 + 40 overflow)
8. ✅ Structured logging enabled (correlation IDs)

**Monitoring:**
- Health check: `GET /api/chatkit/health` (Kubernetes liveness/readiness probe)
- Logs: `backend/logs/chatkit.log` (correlation IDs for tracing)
- Metrics: Database connection pool usage, OpenAI API latency

**Scaling:**
- Database pool: 10 base + 40 overflow = 50 concurrent connections
- Stateless architecture: Horizontal scaling supported
- Conversation history: 20-message limit per user (token budget management)

---

### Related Documentation

- **Spec**: `specs/008-chatkit-server-backend/spec.md`
- **Plan**: `specs/008-chatkit-server-backend/plan.md`
- **Tasks**: `specs/008-chatkit-server-backend/tasks.md`
- **Test Plans**: `specs/008-chatkit-server-backend/test-plans/`
- **API Contracts**: `contracts/chatkit-api.yaml`, `contracts/chatkit-sse-events.md`
- **Quickstart**: `specs/008-chatkit-server-backend/quickstart.md`
