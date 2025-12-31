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
