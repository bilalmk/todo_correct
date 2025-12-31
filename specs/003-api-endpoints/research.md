# Research: RESTful API Endpoints for Todo Application

**Feature**: 003-api-endpoints
**Date**: 2025-12-30
**Purpose**: Resolve all "NEEDS CLARIFICATION" items from Technical Context and establish architectural patterns for 15 API endpoints

---

## Research Tasks

### 1. FastAPI Repository Pattern Best Practices

**Decision**: Use repository pattern with async SQLModel for data access layer

**Rationale**:
- **Separation of Concerns**: Repositories isolate database logic from API endpoints, making code more testable and maintainable
- **Testability**: Repository methods can be unit tested independently; endpoints can use mock repositories
- **Reusability**: Common queries (e.g., soft delete filtering, user isolation) are centralized in repository methods
- **Type Safety**: Repository methods are fully typed with SQLModel and Pydantic, providing compile-time safety

**Pattern**:
```python
class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: UUID, data: TaskCreate) -> Task:
        """Create task with automatic user_id assignment."""
        task = Task(**data.model_dump(), user_id=user_id)
        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def get_by_id(self, user_id: UUID, task_id: int) -> Optional[Task]:
        """Get task by ID with user isolation and soft delete filter."""
        stmt = (
            select(Task)
            .where(Task.id == task_id)
            .where(Task.user_id == user_id)
            .where(Task.deleted_at.is_(None))
            .options(selectinload(Task.tags))  # Eager load tags
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
```

**Alternatives Considered**:
1. **Direct SQLModel queries in endpoints**: Rejected because it couples endpoint logic to database schema, making tests harder and violating separation of concerns
2. **Service layer + Repository**: Considered but rejected as over-engineering for this feature scope (no complex business logic beyond CRUD)
3. **Active Record pattern**: Rejected because SQLModel models are data models, not business logic containers

**Sources**:
- FastAPI official docs: https://fastapi.tiangolo.com/tutorial/sql-databases/
- SQLModel async patterns: https://sqlmodel.tiangolo.com/tutorial/async/
- Repository pattern: https://www.cosmicpython.com/book/chapter_02_repository.html

---

### 2. Pydantic v2 Schema Design for Request/Response DTOs

**Decision**: Use separate Pydantic models for Create, Update, and Response schemas

**Rationale**:
- **Request Validation**: Create/Update DTOs enforce input constraints (max lengths, enums, required fields) before database operations
- **Response Shaping**: Response DTOs control JSON serialization and include computed fields (nested tags, formatted timestamps)
- **API Evolution**: Separate schemas allow different request/response structures without breaking changes
- **Documentation**: FastAPI auto-generates OpenAPI schemas from Pydantic models with accurate field descriptions

**Pattern**:
```python
# Request DTO (input validation)
class TaskCreate(BaseModel):
    title: str = Field(max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=10000)
    priority: Optional[PriorityEnum] = None
    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None
    recurrence_pattern: Optional[RecurrencePatternEnum] = None
    recurrence_config: Optional[dict] = None

    @field_validator('reminder_at')
    def reminder_before_due(cls, v, info: ValidationInfo):
        """Ensure reminder_at is before due_date."""
        if v and info.data.get('due_date') and v >= info.data['due_date']:
            raise ValueError('reminder_at must be before due_date')
        return v

# Response DTO (output shaping)
class TaskResponse(BaseModel):
    id: int
    user_id: UUID
    title: str
    description: Optional[str]
    completed: bool
    priority: Optional[str]
    due_date: Optional[datetime]
    reminder_at: Optional[datetime]
    recurrence_pattern: Optional[str]
    recurrence_config: Optional[dict]
    tags: List[TagResponse] = []  # Nested tag details
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)  # Pydantic v2 ORM mode
```

**Alternatives Considered**:
1. **Single schema for both request/response**: Rejected because request validation rules differ from response structure (e.g., tags are input as IDs but returned as objects)
2. **Inheriting from SQLModel directly**: Rejected because it couples API contracts to database schema; schema evolution becomes harder
3. **Partial schema for PATCH**: Using `Optional` on all fields in a separate `TaskUpdate` schema to support partial updates

**Sources**:
- Pydantic v2 docs: https://docs.pydantic.dev/latest/
- FastAPI response models: https://fastapi.tiangolo.com/tutorial/response-model/
- Pydantic field validators: https://docs.pydantic.dev/latest/concepts/validators/

---

### 3. PostgreSQL Full-Text Search with SQLModel

**Decision**: Use `to_tsvector` and `ts_query` with existing GIN index for full-text search

**Rationale**:
- **Performance**: GIN index on `to_tsvector(title || ' ' || description)` enables sub-200ms searches on 5000+ tasks
- **Stemming**: PostgreSQL built-in stemming supports partial word matching (e.g., "meeting" matches "meetings")
- **Relevance Ranking**: Can use `ts_rank` for scoring results by relevance (future enhancement)
- **Native Integration**: No external search service required; works within existing PostgreSQL database

**Pattern**:
```python
# In TaskRepository
async def search(self, user_id: UUID, query: str) -> List[Task]:
    """Full-text search on title and description."""
    from sqlalchemy import func, text

    # PostgreSQL full-text search using GIN index
    stmt = (
        select(Task)
        .where(Task.user_id == user_id)
        .where(Task.deleted_at.is_(None))
        .where(
            text(
                "to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')) "
                "@@ plainto_tsquery('english', :query)"
            ).bindparams(query=query)
        )
        .options(selectinload(Task.tags))
    )
    result = await self.session.execute(stmt)
    return result.scalars().all()
```

**Existing Infrastructure**:
- Migration `7153bd9cdab5_add_gin_index_for_fulltext_search_on_.py` already created GIN index:
  ```sql
  CREATE INDEX idx_tasks_title_description_fts
  ON tasks USING GIN (
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
  );
  ```

**Alternatives Considered**:
1. **LIKE queries**: Rejected because it's 10x slower than GIN index and doesn't support stemming
2. **Elasticsearch**: Rejected as over-engineering for Phase II; overkill for 5000 tasks per user
3. **trigram indexes**: Considered for fuzzy matching but rejected; simpler to start with full-text and add later if needed

**Sources**:
- PostgreSQL full-text search: https://www.postgresql.org/docs/current/textsearch.html
- SQLAlchemy text search: https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.text
- Performance comparison: https://www.cybertec-postgresql.com/en/postgresql-full-text-search-vs-the-rest/

---

### 4. Query Building Service for Dynamic Filtering and Sorting

**Decision**: Create a `QueryService` class that builds SQLAlchemy `select()` statements from query parameters

**Rationale**:
- **Dynamic Filters**: Query params (status, priority, tags, due_date range) can be combined in any order
- **Type Safety**: SQLAlchemy select() statements are type-checked and prevent SQL injection
- **Maintainability**: Centralized query building logic is easier to test and modify than scattered filter conditions
- **Composability**: Filters, search, and sorting are composed into a single query for optimal performance

**Pattern**:
```python
class QueryService:
    @staticmethod
    def build_task_query(
        user_id: UUID,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        due_before: Optional[datetime] = None,
        due_after: Optional[datetime] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        order: str = "desc",
    ) -> Select:
        """Build dynamic query with filters, search, and sorting."""
        from sqlalchemy import or_, and_, text, func

        # Base query with user isolation and soft delete filter
        stmt = (
            select(Task)
            .where(Task.user_id == user_id)
            .where(Task.deleted_at.is_(None))
            .options(selectinload(Task.tags))
        )

        # Status filter
        if status == "complete":
            stmt = stmt.where(Task.completed == True)
        elif status == "incomplete":
            stmt = stmt.where(Task.completed == False)

        # Priority filter
        if priority:
            stmt = stmt.where(Task.priority == priority)

        # Due date range filters
        if due_before:
            stmt = stmt.where(Task.due_date < due_before)
        if due_after:
            stmt = stmt.where(Task.due_date > due_after)

        # Tag filter (OR logic for multiple tags)
        if tags:
            if "none" in tags:
                # Special case: tasks with no tags
                has_no_tags = ~exists(
                    select(1).where(TaskTag.task_id == Task.id)
                )
                if len(tags) == 1:
                    stmt = stmt.where(has_no_tags)
                else:
                    # Combine "none" with other tag names using OR
                    tag_names = [t for t in tags if t != "none"]
                    has_tags = exists(
                        select(1)
                        .where(TaskTag.task_id == Task.id)
                        .where(TaskTag.tag_id.in_(
                            select(Tag.id)
                            .where(Tag.user_id == user_id)
                            .where(Tag.name.in_(tag_names))
                            .where(Tag.deleted_at.is_(None))
                        ))
                    )
                    stmt = stmt.where(or_(has_no_tags, has_tags))
            else:
                # Tasks with any of the specified tags
                stmt = stmt.where(
                    exists(
                        select(1)
                        .where(TaskTag.task_id == Task.id)
                        .where(TaskTag.tag_id.in_(
                            select(Tag.id)
                            .where(Tag.user_id == user_id)
                            .where(Tag.name.in_(tags))
                            .where(Tag.deleted_at.is_(None))
                        ))
                    )
                )

        # Full-text search
        if search:
            stmt = stmt.where(
                text(
                    "to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')) "
                    "@@ plainto_tsquery('english', :search)"
                ).bindparams(search=search)
            )

        # Sorting
        sort_column = getattr(Task, sort_by, Task.created_at)
        if order == "asc":
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())

        return stmt
```

**Alternatives Considered**:
1. **ORM filter chaining in endpoint**: Rejected because it scatters query logic across endpoints
2. **Raw SQL queries**: Rejected due to SQL injection risk and loss of type safety
3. **Django-style Q objects**: Not available in SQLAlchemy; current approach is idiomatic

**Sources**:
- SQLAlchemy select: https://docs.sqlalchemy.org/en/20/tutorial/data_select.html
- Dynamic queries: https://docs.sqlalchemy.org/en/20/faq/performance.html#dynamic-relationship-loaders
- Eager loading: https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#selectin-eager-loading

---

### 5. JWT User ID Validation Dependency

**Decision**: Create `verify_user_match(current_user, user_id)` dependency to enforce URL path user_id matches JWT claim

**Rationale**:
- **Authorization**: Prevents users from accessing other users' data by manipulating URL parameters
- **Consistent Error Handling**: Returns HTTP 403 Forbidden with clear error message
- **Reusable Dependency**: Used across all user-scoped endpoints (tasks, tags, task-tags)

**Pattern**:
```python
# In backend/src/api/deps.py
from fastapi import HTTPException, status, Path
from uuid import UUID

def verify_user_match(
    current_user: User = Depends(get_current_user),
    user_id: UUID = Path(..., description="User ID from URL path"),
) -> User:
    """
    Verify that the authenticated user's ID matches the URL path user_id.

    Raises:
        HTTPException: 403 if user_id mismatch

    Returns:
        The authenticated user if match is successful
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID mismatch",
        )
    return current_user

# Usage in endpoint
@router.get("/api/v1/{user_id}/tasks")
async def list_tasks(
    user: User = Depends(verify_user_match),
    session: AsyncSession = Depends(get_session),
):
    # user.id is guaranteed to match URL user_id
    ...
```

**Alternatives Considered**:
1. **Manual validation in each endpoint**: Rejected due to code duplication and risk of forgotten checks
2. **Middleware-based validation**: Considered but rejected; dependency injection is more explicit and testable
3. **Extracting user_id from JWT only**: Rejected because RESTful URLs should include resource identifiers

**Sources**:
- FastAPI dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/
- Path parameters: https://fastapi.tiangolo.com/tutorial/path-params/
- Security best practices: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html

---

### 6. Soft Delete Filtering Best Practices

**Decision**: Apply `WHERE deleted_at IS NULL` filter in repository methods, not in models

**Rationale**:
- **Explicit Filtering**: Repository methods explicitly filter soft-deleted records, making behavior predictable
- **Recovery Support**: Allows admin endpoints to query soft-deleted records if needed (future enhancement)
- **No Magic**: Avoids SQLAlchemy global filters that can have unexpected side effects
- **Testability**: Tests can verify soft delete behavior by checking `deleted_at` timestamp

**Pattern**:
```python
# In TaskRepository
async def list_tasks(self, user_id: UUID) -> List[Task]:
    """List all active tasks for user."""
    stmt = (
        select(Task)
        .where(Task.user_id == user_id)
        .where(Task.deleted_at.is_(None))  # Explicit soft delete filter
        .options(selectinload(Task.tags.and_(Tag.deleted_at.is_(None))))  # Exclude soft-deleted tags
        .order_by(Task.created_at.desc())
    )
    result = await self.session.execute(stmt)
    return result.scalars().all()

async def soft_delete(self, user_id: UUID, task_id: int) -> bool:
    """Soft delete task by setting deleted_at timestamp."""
    task = await self.get_by_id(user_id, task_id)
    if not task:
        return False
    task.deleted_at = datetime.now(timezone.utc)
    await self.session.flush()
    return True
```

**Alternatives Considered**:
1. **SQLAlchemy with_loader_criteria**: Rejected because it's a global filter that can affect unintended queries
2. **Hard deletes**: Rejected per constitution principle (soft deletes preferred for data recovery)
3. **Hybrid property on model**: Considered but rejected; explicit filtering in queries is clearer

**Sources**:
- Soft delete patterns: https://www.martinfowler.com/eaaCatalog/auditLog.html
- SQLAlchemy filtering: https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#filtering-results

---

### 7. Eager Loading for Task-Tag Relationships (N+1 Prevention)

**Decision**: Use `selectinload(Task.tags)` to eagerly load tags in a single query

**Rationale**:
- **Performance**: Avoids N+1 query problem (1 query for tasks + N queries for each task's tags)
- **Batching**: selectinload issues a second query with `WHERE tag_id IN (...)` to fetch all tags at once
- **Type Safety**: SQLModel relationships are fully typed, preventing runtime errors
- **Soft Delete Filtering**: Can apply `and_(Tag.deleted_at.is_(None))` to exclude soft-deleted tags from eager load

**Pattern**:
```python
from sqlalchemy.orm import selectinload

# In TaskRepository methods
stmt = (
    select(Task)
    .where(Task.user_id == user_id)
    .where(Task.deleted_at.is_(None))
    .options(
        selectinload(Task.tags).where(Tag.deleted_at.is_(None))  # Eager load only active tags
    )
)
```

**Query Execution**:
1. Query 1: `SELECT * FROM tasks WHERE user_id = :user_id AND deleted_at IS NULL`
2. Query 2: `SELECT tags.* FROM tags JOIN task_tags ON ... WHERE task_tags.task_id IN (:id1, :id2, ...) AND tags.deleted_at IS NULL`

**Alternatives Considered**:
1. **Lazy loading**: Rejected because it causes N+1 queries (1 + number of tasks)
2. **joinedload**: Rejected because it uses LEFT JOIN which can return duplicate Task rows if a task has multiple tags
3. **Manual JOIN in query**: Rejected because selectinload is cleaner and handles duplicates automatically

**Sources**:
- SQLAlchemy eager loading: https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#selectin-eager-loading
- N+1 problem: https://secure.phabricator.com/book/phabcontrib/article/n_plus_one/
- SQLModel relationships: https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/

---

## Summary of Decisions

| Research Task | Decision | Key Benefit |
|---------------|----------|-------------|
| Repository Pattern | Use async repository classes for data access | Separation of concerns, testability, type safety |
| Pydantic Schemas | Separate Create/Update/Response DTOs | Input validation, output shaping, API evolution |
| Full-Text Search | PostgreSQL `to_tsvector` with GIN index | Sub-200ms search on 5000+ tasks, stemming support |
| Query Building | `QueryService.build_task_query()` for dynamic filters | Composable filters, type safety, maintainability |
| User Validation | `verify_user_match` dependency | Authorization, consistent error handling, reusability |
| Soft Deletes | Explicit `deleted_at IS NULL` in repository | Predictable behavior, recovery support, no magic |
| Eager Loading | `selectinload(Task.tags)` to avoid N+1 | Single query for tags, soft delete filtering |

All patterns are compatible with existing codebase (001-setup-auth-foundation, 002-database-schema) and follow constitutional principles (stateless, type-safe, async, testable).

---

**Next Step**: Phase 1 - Generate data-model.md, contracts/, and quickstart.md
