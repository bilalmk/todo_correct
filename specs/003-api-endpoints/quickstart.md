# Quickstart: RESTful API Endpoints

**Feature**: 003-api-endpoints
**Date**: 2025-12-30
**Purpose**: Quick reference for implementing and testing the 15 API endpoints

---

## Architecture Overview

```
┌─────────────┐
│   Client    │ (Next.js frontend - Phase II)
│  (Browser)  │
└──────┬──────┘
       │ HTTP + JWT Bearer Token
       │
┌──────▼──────────────────────────────────────────┐
│          FastAPI Application                    │
│                                                  │
│  ┌────────────────────────────────────────┐    │
│  │  Middleware Layer                      │    │
│  │  - Request ID tracking                 │    │
│  │  - JWT validation                      │    │
│  │  - CORS                                │    │
│  └───────────────┬────────────────────────┘    │
│                  │                              │
│  ┌───────────────▼────────────────────────┐    │
│  │  API Routers (3)                       │    │
│  │  - tasks.py (7 endpoints)              │    │
│  │  - tags.py (5 endpoints)               │    │
│  │  - task_tags.py (3 endpoints)          │    │
│  └───────────────┬────────────────────────┘    │
│                  │                              │
│  ┌───────────────▼────────────────────────┐    │
│  │  Dependencies                          │    │
│  │  - get_current_user (JWT → User)       │    │
│  │  - verify_user_match (URL vs JWT)      │    │
│  │  - get_session (async DB session)      │    │
│  └───────────────┬────────────────────────┘    │
│                  │                              │
│  ┌───────────────▼────────────────────────┐    │
│  │  Repositories (3)                      │    │
│  │  - TaskRepository                      │    │
│  │  - TagRepository                       │    │
│  │  - TaskTagRepository                   │    │
│  └───────────────┬────────────────────────┘    │
│                  │                              │
│  ┌───────────────▼────────────────────────┐    │
│  │  Query Service                         │    │
│  │  - build_task_query() with filters    │    │
│  │  - Full-text search                   │    │
│  │  - Sorting logic                       │    │
│  └───────────────┬────────────────────────┘    │
└──────────────────┼──────────────────────────────┘
                   │
       ┌───────────▼──────────────┐
       │ Async SQLModel Session   │
       └───────────┬──────────────┘
                   │
       ┌───────────▼──────────────┐
       │  Neon PostgreSQL         │
       │  - tasks table           │
       │  - tags table            │
       │  - task_tags table       │
       │  - GIN full-text index   │
       └──────────────────────────┘
```

---

## Implementation Sequence

### Phase 1: Foundation (Dependencies & Schemas)

**Files to Create:**
1. `backend/src/schemas/common.py` - Enums and ErrorResponse
2. `backend/src/schemas/tag.py` - TagCreate, TagUpdate, TagResponse
3. `backend/src/schemas/task.py` - TaskCreate, TaskUpdate, TaskReplace, TaskResponse
4. `backend/src/schemas/task_tag.py` - TaskTagCreate, TaskTagResponse
5. `backend/src/api/deps.py` - Add `verify_user_match` dependency

**Test:**
```bash
# Validate Pydantic models
python -c "from backend.src.schemas.task import TaskCreate; print(TaskCreate.model_json_schema())"
```

---

### Phase 2: Repository Layer

**Files to Create:**
1. `backend/src/repositories/__init__.py`
2. `backend/src/repositories/tag.py` - TagRepository
3. `backend/src/repositories/task.py` - TaskRepository
4. `backend/src/repositories/task_tag.py` - TaskTagRepository

**Key Methods:**

```python
# TaskRepository (backend/src/repositories/task.py)
class TaskRepository:
    async def create(user_id: UUID, data: TaskCreate) -> Task
    async def get_by_id(user_id: UUID, task_id: int) -> Optional[Task]
    async def list_tasks(user_id: UUID) -> List[Task]
    async def update(user_id: UUID, task_id: int, data: TaskUpdate) -> Optional[Task]
    async def replace(user_id: UUID, task_id: int, data: TaskReplace) -> Optional[Task]
    async def soft_delete(user_id: UUID, task_id: int) -> bool
    async def search(user_id: UUID, query: str) -> List[Task]

# TagRepository (backend/src/repositories/tag.py)
class TagRepository:
    async def create(user_id: UUID, data: TagCreate) -> Tag
    async def get_by_id(user_id: UUID, tag_id: int) -> Optional[Tag]
    async def list_tags(user_id: UUID) -> List[Tag]
    async def update(user_id: UUID, tag_id: int, data: TagUpdate) -> Optional[Tag]
    async def soft_delete(user_id: UUID, tag_id: int) -> bool
    async def exists_by_name(user_id: UUID, name: str) -> bool

# TaskTagRepository (backend/src/repositories/task_tag.py)
class TaskTagRepository:
    async def assign_tag(user_id: UUID, task_id: int, tag_id: int) -> bool
    async def unassign_tag(user_id: UUID, task_id: int, tag_id: int) -> bool
    async def get_task_tags(user_id: UUID, task_id: int) -> List[Tag]
```

**Test:**
```bash
# Unit test repositories
pytest backend/tests/unit/test_repositories.py -v
```

---

### Phase 3: Query Service

**File to Create:**
`backend/src/services/query.py` - QueryService with `build_task_query()`

**Example Query Building:**

```python
# QueryService.build_task_query()
# Handles:
# - User isolation (WHERE user_id = :user_id)
# - Soft delete filter (WHERE deleted_at IS NULL)
# - Status filter (WHERE completed = :status)
# - Priority filter (WHERE priority = :priority)
# - Tag filter with OR logic (EXISTS subquery with IN clause)
# - Tag "none" filter (NOT EXISTS subquery)
# - Due date range (WHERE due_date BETWEEN :after AND :before)
# - Full-text search (WHERE to_tsvector(...) @@ plainto_tsquery(:search))
# - Sorting (ORDER BY :sort_by :order)
# - Eager loading tags (selectinload(Task.tags))
```

**Test:**
```bash
pytest backend/tests/unit/test_query_service.py -v
```

---

### Phase 4: API Routers

**Files to Create:**
1. `backend/src/api/tasks.py` - 7 task endpoints
2. `backend/src/api/tags.py` - 5 tag endpoints
3. `backend/src/api/task_tags.py` - 3 task-tag endpoints

**Endpoint Signature Pattern:**

```python
# Example: GET /api/v1/{user_id}/tasks
@router.get("/api/v1/{user_id}/tasks", response_model=List[TaskResponse])
async def list_tasks(
    user: User = Depends(verify_user_match),
    session: AsyncSession = Depends(get_session),
    status: Optional[str] = Query(None, regex="^(incomplete|complete)$"),
    priority: Optional[PriorityEnum] = None,
    tag: Optional[List[str]] = Query(None),
    due_before: Optional[datetime] = None,
    due_after: Optional[datetime] = None,
    search: Optional[str] = None,
    sort: str = Query("created_at", regex="^(created_at|due_date|priority|title)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
):
    query_service = QueryService()
    stmt = query_service.build_task_query(
        user_id=user.id,
        status=status,
        priority=priority,
        tags=tag,
        due_before=due_before,
        due_after=due_after,
        search=search,
        sort_by=sort,
        order=order,
    )
    result = await session.execute(stmt)
    tasks = result.scalars().all()
    return [TaskResponse.model_validate(task) for task in tasks]
```

**Test:**
```bash
# Integration test endpoints
pytest backend/tests/integration/test_tasks.py -v
pytest backend/tests/integration/test_tags.py -v
pytest backend/tests/integration/test_task_tags.py -v
```

---

### Phase 5: Register Routers in Main App

**File to Modify:** `backend/src/main.py`

```python
from fastapi import FastAPI
from .api import tasks, tags, task_tags

app = FastAPI(
    title="Todo Application API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Register routers
app.include_router(tasks.router, tags=["Tasks"])
app.include_router(tags.router, tags=["Tags"])
app.include_router(task_tags.router, tags=["Task-Tags"])
```

**Test:**
```bash
# Run server and access OpenAPI docs
uvicorn backend.src.main:app --reload
# Open http://localhost:8000/docs
```

---

## Testing Strategy

### 1. Unit Tests (backend/tests/unit/)

**test_repositories.py:**
- TaskRepository CRUD operations
- TagRepository CRUD operations
- TaskTagRepository many-to-many operations
- Soft delete behavior
- User isolation enforcement

**test_query_service.py:**
- Filter combinations (status + priority + tags)
- Tag "none" filter logic
- Full-text search query building
- Sorting logic
- Eager loading configuration

**test_validators.py:**
- Hex color validation and normalization
- reminder_at < due_date validation
- Title/name whitespace trimming

**Run:**
```bash
pytest backend/tests/unit/ -v --cov=backend/src/repositories --cov=backend/src/services
```

---

### 2. Integration Tests (backend/tests/integration/)

**test_tasks.py:**
- POST /api/v1/{user_id}/tasks (create)
- GET /api/v1/{user_id}/tasks (list with all filter combinations)
- GET /api/v1/{user_id}/tasks/{id} (get single)
- PUT /api/v1/{user_id}/tasks/{id} (full replacement)
- PATCH /api/v1/{user_id}/tasks/{id} (partial update)
- PATCH /api/v1/{user_id}/tasks/{id}/complete (toggle completion)
- DELETE /api/v1/{user_id}/tasks/{id} (soft delete)

**test_tags.py:**
- POST /api/v1/{user_id}/tags (create, test 409 on duplicate)
- GET /api/v1/{user_id}/tags (list)
- GET /api/v1/{user_id}/tags/{id} (get single)
- PUT /api/v1/{user_id}/tags/{id} (update, test hex color normalization)
- DELETE /api/v1/{user_id}/tags/{id} (soft delete)

**test_task_tags.py:**
- POST /api/v1/{user_id}/tasks/{id}/tags (assign, test 409 on duplicate)
- GET /api/v1/{user_id}/tasks/{id}/tags (list)
- DELETE /api/v1/{user_id}/tasks/{id}/tags/{tag_id} (unassign)

**Run:**
```bash
pytest backend/tests/integration/ -v --cov=backend/src/api
```

---

### 3. E2E Tests (backend/tests/e2e/)

**test_user_isolation.py:**
- User A cannot access User B's tasks (404, not 403)
- User A cannot modify User B's tasks
- User A cannot assign tags to User B's tasks
- JWT user_id mismatch returns 403
- Cross-user tag filtering returns empty results

**Run:**
```bash
pytest backend/tests/e2e/ -v
```

---

### 4. Performance Tests

**Test Cases:**
1. Task creation: <100ms p95 (simple task)
2. Task list with filters: <500ms p95 (10,000 tasks)
3. Full-text search: <200ms p95 (5,000 tasks)
4. N+1 query prevention: Verify eager loading with SQL logging

**Run:**
```bash
pytest backend/tests/performance/ -v --durations=10
```

---

## Sample API Calls

### 1. Create Task with All Fields

```bash
curl -X POST http://localhost:8000/api/v1/123e4567-e89b-12d3-a456-426614174000/tasks \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "priority": "high",
    "due_date": "2025-12-31T10:00:00Z",
    "reminder_at": "2025-12-30T09:45:00Z",
    "recurrence_pattern": "weekly",
    "recurrence_config": {"rrule": "FREQ=WEEKLY;BYDAY=MO,FR"}
  }'
```

**Expected Response (201 Created):**
```json
{
  "id": 123,
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "priority": "high",
  "due_date": "2025-12-31T10:00:00Z",
  "reminder_at": "2025-12-30T09:45:00Z",
  "recurrence_pattern": "weekly",
  "recurrence_config": {"rrule": "FREQ=WEEKLY;BYDAY=MO,FR"},
  "tags": [],
  "created_at": "2025-12-30T14:30:00Z",
  "updated_at": "2025-12-30T14:30:00Z"
}
```

---

### 2. List Tasks with Filters

```bash
curl -X GET "http://localhost:8000/api/v1/123e4567-e89b-12d3-a456-426614174000/tasks?status=incomplete&priority=high&tag=work&tag=urgent&sort=due_date&order=asc" \
  -H "Authorization: Bearer eyJhbGc..."
```

**Query Breakdown:**
- `status=incomplete`: Only incomplete tasks
- `priority=high`: Only high priority
- `tag=work&tag=urgent`: Tasks with "work" OR "urgent" tags
- `sort=due_date&order=asc`: Sort by due date ascending (earliest first)

**Expected Response (200 OK):**
```json
[
  {
    "id": 124,
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Finish report",
    "completed": false,
    "priority": "high",
    "due_date": "2025-12-28T17:00:00Z",
    "tags": [
      {"id": 1, "name": "work", "color": "#FF5733", ...}
    ],
    ...
  },
  {
    "id": 123,
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Buy groceries",
    "completed": false,
    "priority": "high",
    "due_date": "2025-12-31T10:00:00Z",
    "tags": [
      {"id": 2, "name": "urgent", "color": "#FF0000", ...}
    ],
    ...
  }
]
```

---

### 3. Full-Text Search

```bash
curl -X GET "http://localhost:8000/api/v1/123e4567-e89b-12d3-a456-426614174000/tasks?search=meeting+notes" \
  -H "Authorization: Bearer eyJhbGc..."
```

**Expected Behavior:**
- PostgreSQL GIN index used (`idx_tasks_title_description_fts`)
- Matches tasks with "meeting" OR "notes" in title/description
- Stemming applied (e.g., "meeting" matches "meetings")
- Results returned in <200ms

---

### 4. Create Tag with Color Normalization

```bash
curl -X POST http://localhost:8000/api/v1/123e4567-e89b-12d3-a456-426614174000/tags \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"name": "work", "color": "#f5a"}'
```

**Expected Response (201 Created):**
```json
{
  "id": 1,
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "work",
  "color": "#FF55AA",  // Normalized from #f5a to #FF55AA
  "created_at": "2025-12-30T14:30:00Z"
}
```

---

### 5. Assign Tag to Task

```bash
curl -X POST http://localhost:8000/api/v1/123e4567-e89b-12d3-a456-426614174000/tasks/123/tags \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"tag_id": 1}'
```

**Expected Response (201 Created):**
```json
{
  "task_id": 123,
  "tag_id": 1,
  "message": "Tag assigned successfully"
}
```

---

### 6. Partial Update Task (PATCH)

```bash
curl -X PATCH http://localhost:8000/api/v1/123e4567-e89b-12d3-a456-426614174000/tasks/123 \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries and bread", "priority": "medium"}'
```

**Expected Behavior:**
- Only `title` and `priority` updated
- `description`, `due_date`, etc. remain unchanged
- `updated_at` timestamp automatically updated

---

## Error Handling Examples

### 1. Duplicate Tag Name (409 Conflict)

```bash
# Create tag "work"
curl -X POST .../tags -d '{"name": "work", "color": "#FF5733"}'

# Try to create another tag "work" (same user)
curl -X POST .../tags -d '{"name": "work", "color": "#00FF00"}'
```

**Expected Response (409 Conflict):**
```json
{
  "error": "Tag name already exists",
  "code": "TAG_NAME_CONFLICT",
  "status": 409,
  "request_id": "req_abc123"
}
```

---

### 2. User ID Mismatch (403 Forbidden)

```bash
# JWT contains user_id = 123e4567...
# But URL has different user_id = 999e8888...
curl -X GET http://localhost:8000/api/v1/999e8888-e89b-12d3-a456-426614174000/tasks \
  -H "Authorization: Bearer eyJhbGc..."  # JWT for user 123e4567...
```

**Expected Response (403 Forbidden):**
```json
{
  "error": "User ID mismatch",
  "code": "FORBIDDEN",
  "status": 403,
  "request_id": "req_abc123"
}
```

---

### 3. Cross-User Task Access (404 Not Found)

```bash
# User A tries to access User B's task
curl -X GET http://localhost:8000/api/v1/123e4567.../tasks/999 \
  -H "Authorization: Bearer ..."  # JWT for user 123e4567...
# Task 999 belongs to a different user
```

**Expected Response (404 Not Found - NOT 403):**
```json
{
  "error": "Task not found",
  "code": "TASK_NOT_FOUND",
  "status": 404,
  "request_id": "req_abc123"
}
```

**Rationale:** Return 404 instead of 403 to prevent user enumeration attacks (attacker cannot tell if task exists but is forbidden vs doesn't exist)

---

### 4. Invalid Hex Color (422 Validation Error)

```bash
curl -X POST .../tags -d '{"name": "work", "color": "#GGGGGG"}'
```

**Expected Response (422 Unprocessable Entity):**
```json
{
  "error": "Invalid hex color format. Use #RRGGBB or #RGB.",
  "code": "VALIDATION_ERROR",
  "status": 422,
  "request_id": "req_abc123"
}
```

---

## Performance Checklist

Before marking feature complete, verify:

- [ ] Task creation <100ms p95 (simple tasks)
- [ ] Task list with filters <500ms p95 (10,000 tasks)
- [ ] Full-text search <200ms p95 (5,000 tasks)
- [ ] No N+1 queries (verify with SQL logging: only 2 queries for task + tags)
- [ ] Soft delete filter applied on all queries
- [ ] User isolation enforced on all endpoints
- [ ] Connection pool sized 5-20 (check `backend/src/core/database.py`)
- [ ] GIN index used for full-text search (verify with EXPLAIN ANALYZE)

---

## Deployment Checklist

Before deploying to production:

- [ ] All 50+ tests passing
- [ ] OpenAPI docs generated at /docs
- [ ] Environment variables set (DATABASE_URL, JWT_SECRET)
- [ ] CORS configured for frontend domain
- [ ] Health check endpoint /health returning 200
- [ ] Request ID middleware active (for tracing)
- [ ] Database migrations applied (no changes needed for this spec)
- [ ] Error responses follow standard format {error, code, status, request_id}
- [ ] Soft delete filtering tested (deleted tasks excluded from queries)

---

**Next Step**: Run `/sp.tasks` to generate atomic implementation tasks from this plan
